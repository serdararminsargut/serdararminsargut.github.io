#!/usr/bin/env python3
"""NO-DEPLOY frozen release handoff verification for Serdar and Duru HugoBlox.

Reads evidence ZIP + previously recorded Cloudflare production baseline ZIP,
creates a temporary Cloudflare-compatible static root, independently validates
all file bytes, SEO and baseline commit, and writes only a local receipt.

No internet, token, git, Cloudflare, DNS, index submission or deploy operations.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import zipfile
from xml.etree import ElementTree as ET

CONFIG = {
    'SERDAR': {'site':'https://serdararminsargut.com','project':'serdararminsargut',
               'files':169,'old_files':155,'urls':95,'baseline_urls':90,
               'output_name':'dist', 'main':'bb4737ed7367b84008c860ec3f722055a56ae518'},
    'DURU': {'site':'https://durumuallasargut.com','project':'duru-mualla-sargut-site',
             'files':128,'old_files':115,'urls':36,'baseline_urls':31,
             'output_name':'public', 'main':'0455109adba70ce54f0424090c95e64d527dd9bd'},
}
SITEMAP_NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def ensure(condition, error):
    if not condition:
        raise AssertionError('NO_GO: ' + error)


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def path_safe(name):
    p = PurePosixPath(name)
    return (bool(name) and not name.startswith('/') and not name.startswith('\\')
            and '\\' not in name and not any(part in ('', '.', '..') for part in name.split('/'))
            and not re.match(r'^[A-Za-z]:', name) and len(p.parts) > 0)


def read_zip_json(archive, kind):
    with zipfile.ZipFile(archive, 'r') as z:
        ensure(z.testzip() is None, f'{kind}: zip checksum failed')
        files = [n for n in z.namelist() if not n.endswith('/')]
        jsons = [n for n in files if n.endswith('.json')]
        ensure(len(jsons) == 1, f'{kind}: expected exactly one JSON')
        return json.loads(z.read(jsons[0]))


class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals=[];self.robots=[];self.ogurls=[];self.lang='';self.h1=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag == 'html': self.lang=a.get('lang', '')
        if tag == 'h1': self.h1+=1
        if tag == 'link' and 'canonical' in a.get('rel','').split():
            self.canonicals.append(a.get('href',''))
        if tag == 'meta' and a.get('name')=='robots':
            self.robots.append(a.get('content',''))
        if tag == 'meta' and a.get('property')=='og:url':
            self.ogurls.append(a.get('content',''))


def release_paths(project):
    paths={
      'SERDAR': ['rehber/index.html','rehber/post/index.html',
                 'rehber/post/cocuk-giyim-e-ticaret-cekimlerinde-portfoy-secimi/index.html',
                 'rehber/post/spor-giyim-ayakkabi-katalog-fotograflari/index.html',
                 'rehber/post/cocuk-oyuncu-casting-sunum-dosyasi/index.html'],
      'DURU': ['rehber/index.html','rehber/post/index.html',
               'rehber/post/tiyatro-deneyiminden-kamera-onu-oyunculuguna/index.html',
               'rehber/post/cocuk-oyuncu-self-tape-dosya-duzeni/index.html',
               'rehber/post/genc-oyuncu-showreel-sahne-ve-ekran-secimi/index.html'],
    }
    return paths[project]


def validate_manifest(m, project):
    c=CONFIG[project]
    ensure(m.get('project')==project,'wrong project identity')
    ensure(m.get('cloudflare_project')==c['project'],'Cloudflare project mismatch')
    ensure(m.get('site')==c['site'],'site origin mismatch')
    ensure(m.get('kind')=='IMMUTABLE_OFFLINE_RELEASE_EVIDENCE_NOT_DEPLOYED','unknown archive kind')
    ensure(m.get('production_publish_authorized') is False and
           m.get('production_published') is False,'an already-authorized/published candidate is not allowed')
    ensure(m.get('file_count')==c['files'] and len(m.get('files',[]))==c['files'],
           'file count mismatch')
    ensure(m.get('old_files_preserved')==c['old_files'],'old files not preserved')
    ensure(m.get('merged_sitemap_urls')==c['urls'] and m.get('new_rehber_pages')==5,
           'sitemap/new guide counts incorrect')
    ensure(bool(re.fullmatch(r'[0-9a-f]{64}',m.get('archive_sha256',''))),'invalid archive SHA')
    ensure(m.get('archive','').endswith('.tar.gz'),'unexpected archive format')
    ensure(bool(re.fullmatch(r'[0-9a-f]{40}',m.get('staging_commit',''))),'invalid staging SHA')
    files={}
    for v in m['files']:
        name=v.get('path','')
        ensure(path_safe(name), 'unsafe path in manifest')
        ensure(name not in files, 'duplicate manifest path')
        ensure(bool(re.fullmatch(r'[0-9a-f]{64}',v.get('sha256',''))), 'invalid sha for '+name)
        ensure(isinstance(v.get('size_bytes'),int) and 0<=v['size_bytes']<=25*1024*1024,
               'file exceeds Cloudflare Pages 25 MiB or invalid size: '+name)
        files[name]=v
    return files


def read_baseline(zippath,project, expected_main):
    o=read_zip_json(zippath,'Cloudflare baseline')
    c=CONFIG[project]
    ensure(o.get('project')==project and
           o.get('cloudflare_pages_project')==c['project'], 'baseline project mismatch')
    ensure(o.get('production_branch')=='main','unexpected Cloudflare production branch')
    latest=o.get('latest_production_deployment',{})
    rollback=o.get('rollback_candidate_production',{})
    ensure(latest.get('environment')=='production' and latest.get('stage_status')=='success',
           'no successful production baseline')
    ensure(latest.get('commit_hash')==expected_main and rollback.get('commit_hash')==expected_main,
           'baseline commit does not match GitHub main')
    ensure(latest.get('deployment_id')==rollback.get('deployment_id') and
           bool(re.fullmatch(r'[0-9a-f-]{36}',latest.get('deployment_id',''))),
           'missing valid rollback candidate')
    return {'deployment_id':latest['deployment_id'],'commit_hash':latest['commit_hash'],
            'url':latest['url'],'observed_at_utc':o['observed_at_utc']}


def unpack(archive_zip, manifest, expected_files, root):
    with zipfile.ZipFile(archive_zip,'r') as z:
        ensure(z.testzip() is None,'evidence ZIP invalid')
        listed=[name for name in z.namelist() if not name.endswith('/')]
        ensure(set(listed)=={manifest['archive'],next(n for n in listed if n.endswith('.json'))},
               'unexpected ZIP member')
        archive_bytes=z.read(manifest['archive'])
    ensure(len(archive_bytes)==manifest['archive_bytes'],'compressed tar byte count mismatch')
    ensure(checksum(archive_bytes)==manifest['archive_sha256'],'compressed tar SHA mismatch')
    root.mkdir(parents=True,exist_ok=False)
    actual=set()
    with tarfile.open(fileobj=io.BytesIO(archive_bytes),mode='r:gz') as tf:
        for m in tf:
            ensure(m.isfile(),'tar contains non-file member')
            ensure(path_safe(m.name),'unsafe tar member '+m.name)
            ensure(m.name in expected_files,'unexpected tar member '+m.name)
            ensure(m.name not in actual,'duplicate tar member '+m.name)
            data=tf.extractfile(m).read()
            v=expected_files[m.name]
            ensure(len(data)==v['size_bytes'] and checksum(data)==v['sha256'],
                   'file SHA/size differs: '+m.name)
            dest=root/m.name
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(data)
            actual.add(m.name)
    ensure(actual==set(expected_files),'missing static root files')
    return archive_bytes


def inspect_site(root,project):
    c=CONFIG[project]; site=c['site'];paths=release_paths(project)
    found=list(root.rglob('*'))
    ensure(not any(x.is_symlink() for x in found),'symlink in built root')
    robots=(root/'robots.txt').read_text(encoding='utf-8')
    ensure('Disallow: /' not in robots, 'production robots globally blocked')
    headers=root/'_headers'
    if headers.exists():
        ensure('X-Robots-Tag: noindex' not in headers.read_text(encoding='utf-8'),
               'production X-Robots noindex leakage')
    sitemap=ET.parse(root/'sitemap.xml').getroot()
    urls=[x.text.strip() for x in sitemap.findall(f'{SITEMAP_NS}url/{SITEMAP_NS}loc')]
    ensure(len(urls)==c['urls'] and len(set(urls))==len(urls),'missing or duplicate sitemap URLs')
    ensure(all(u.startswith(site+'/') for u in urls),'sitemap cross-origin entry')
    if project=='SERDAR':
        other=ET.parse(root/'sitemap-google.xml').getroot()
        other_urls=[x.text.strip() for x in other.findall(f'{SITEMAP_NS}url/{SITEMAP_NS}loc')]
        ensure(other_urls==urls,'secondary sitemap differs')
    else:
        htmls=list((root/'comp-card').glob('*/index.html'))
        pdfs=list((root/'comp-card').rglob('*.pdf'))
        ensure(len(htmls)==26 and len(pdfs)==26,'Duru 26 HTML/PDF protection mismatch')
        ensure(all(p.open('rb').read(5)==b'%PDF-' for p in pdfs),'broken PDF signatures')
    for path in paths:
        ensure((root/path).is_file(),'missing route '+path)
        route=path.removesuffix('index.html')
        expected=site+'/'+route
        ensure(expected in urls,'route absent in sitemap '+expected)
        markup=(root/path).read_text(encoding='utf-8')
        for forbidden in ('PORTFOLIO_AUTOSYNC_PREVIEW_START','portfoy-guncel/source-status.json',
                          'Resmî portföyden güncel bilgiler (test)', 'example.invalid'):
            ensure(forbidden not in markup,'diagnostic leakage: '+path)
        parser=MetaParser();parser.feed(markup)
        ensure(parser.lang.startswith('tr'),'incorrect language: '+path)
        ensure(parser.h1==1,'H1 count unexpected: '+path)
        ensure(parser.canonicals==[expected],'canonical mismatch: '+path)
        ensure(parser.ogurls==[expected],'Open Graph mismatch: '+path)
        ensure(len(parser.robots)==1 and parser.robots[0].replace(' ','').lower()=='index,follow',
               'robots mismatch: '+path)
    ensure(not (root/'rehber'/'portfoy-guncel').exists(),'diagnostic folder leak')
    return {'new_routes':5,'sitemap_urls':len(urls),
            'old_urls_preserved_count':c['baseline_urls'],'duru_html_pdfs':'26/26' if project=='DURU' else None}


def main(args):
    project=args.project
    expected_main=args.main_commit or CONFIG[project]['main']
    ensure(expected_main==CONFIG[project]['main'], 'expected main changed: STOP before trying release')
    ensure(not args.output_root.exists(),'output already exists — refusing to overwrite')
    root=args.output_root/CONFIG[project]['output_name']
    with zipfile.ZipFile(args.frozen_zip,'r') as z:
        json_names=[x for x in z.namelist() if x.endswith('manifest.json')]
        ensure(len(json_names)==1,'expected one release manifest')
        manifest=json.loads(z.read(json_names[0]))
    files=validate_manifest(manifest,project)
    cloudflare=read_baseline(args.baseline_zip,project,expected_main)
    compressed=unpack(args.frozen_zip,manifest,files,root)
    tests=inspect_site(root,project)
    evidence=sorted((p, files[p]['sha256']) for p in files)
    root_digest=checksum('\n'.join(f'{p}\t{h}' for p,h in evidence).encode('utf-8'))
    receipt={
      'status':'NO_DEPLOY_HANDOFF_PASS', 'production_publish_authorized':False,
      'project':project,'cloudflare_project':CONFIG[project]['project'],
      'git_main_expected':expected_main,'staging_commit':manifest['staging_commit'],
      'source_archive_sha256':checksum(compressed), 'total_static_files':len(files),
      'root_tree_digest_sha256':root_digest, 'static_directory':CONFIG[project]['output_name'],
      'cloudflare_readonly_baseline':cloudflare,'checks':tests,
      'writes_performed':'LOCAL_OUTPUT_ONLY', 'production_status':'NOT_PUBLISHED'
    }
    out=args.output_root/'HANDOFF_RECEIPT.json'
    out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(project+'_NO_DEPLOY_HANDOFF_PASS: '+str(len(files))+' verified files / '+str(tests['sitemap_urls'])+' sitemap URLs; production unchanged')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--project',required=True,choices=CONFIG)
    p.add_argument('--frozen-zip',type=Path,required=True)
    p.add_argument('--baseline-zip',type=Path,required=True)
    p.add_argument('--output-root',type=Path,required=True)
    p.add_argument('--main-commit')
    main(p.parse_args())