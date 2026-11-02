#!/usr/bin/env python3
"""Create verified NO-DEPLOY static bundle from an already-accepted real main mirror.

Never reads credentials, talks to remote services, modifies the source, or deploys.
Failures are fatal. A successful bundle remains *unauthorized* for publication.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
from xml.etree import ElementTree as ET

PROJECTS = {
    'SERDAR': {'site':'https://serdararminsargut.com', 'urls':95,'pdfs':4,'count':174},
    'DURU': {'site':'https://durumuallasargut.com', 'urls':36,'pdfs':26,'count':128},
}
NS='{http://www.sitemaps.org/schemas/sitemap/0.9}'


def need(ok, reason):
    if not ok:
        raise RuntimeError('NO_GO: '+reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def files_under(root):
    need(root.is_dir(),'static root absent')
    need(not root.is_symlink(), 'root symlink forbidden')
    items=[]
    for f in root.rglob('*'):
        need(not f.is_symlink(),'symlink forbidden in release: '+str(f))
        if f.is_file():
            rel=f.relative_to(root).as_posix()
            need(not rel.startswith('/') and '..' not in Path(rel).parts,'bad relative path')
            need(not re.search(r'(^|/)(\.git|\.env|__qa[^/]*|portfoy-guncel|source-status\.json)(/|$)',rel,re.I),
                 'testing or credential material forbidden: '+rel)
            items.append((rel,f))
    need(len(items)>100,'suspiciously incomplete output')
    return sorted(items)


def sitemap_urls(path):
    need(path.is_file(),'sitemap.xml absent')
    doc=ET.parse(path).getroot()
    need(doc.tag == NS+'urlset','invalid XML sitemap structure')
    locs=[x.text.strip() for x in doc.findall(NS+'url/'+NS+'loc')]
    need(len(locs)==len(set(locs)),'duplicate sitemap URL')
    return locs


def read_json(path):
    obj=json.loads(path.read_text(encoding='utf-8'))
    need(isinstance(obj,dict),'report not object')
    return obj


def freeze(project, source, receipt, http_proof, out_dir, pdf_parity=None):
    project=project.upper()
    need(project in PROJECTS,'unrecognized project')
    config=PROJECTS[project]
    source=source.resolve();out_dir=out_dir.resolve()
    need(source.is_dir(),'source missing')
    need(not out_dir.exists(),'output directory exists: refuse overwrite')
    need(out_dir!=source and not(out_dir in source.parents or source in out_dir.parents),
         'source and output must be isolated')
    report=read_json(receipt)
    need(report.get('project')==project,'receipt wrong project')
    need(report.get('status')=='PRODUCTION_MAIN_MIRROR_NO_DEPLOY_PASS','mirror not accepted')
    need(report.get('production_root_source')=='GITHUB_MAIN_PRODUCTION_BUILD_NOT_STAGING_BASELINE',
         'mirror did not start with genuine production build')
    need(report.get('production_published') is False and report.get('production_publish_authorized') is False,
         'receipt must explicitly prohibit publication')
    need(report.get('merged_sitemap_urls')==config['urls'],'wrong sitemap count in receipt')
    need(report.get('new_verified_guide_files')==12 and report.get('new_hugo_html')==5,
         'unexpected HugoBlox additions in receipt')
    probe=read_json(http_proof)
    need(probe.get('project')==project and
         probe.get('status')=='LOCAL_PRODUCTION_MIRROR_HTTP_ACCEPTANCE_PASS',
         'local HTTP acceptance missing')
    if project=='DURU':
        need(pdf_parity is not None and Path(pdf_parity).is_file(),'Duru PDF visual parity proof absent')
        pdfproof=read_json(Path(pdf_parity))
        need(pdfproof.get('project')=='DURU' and
             pdfproof.get('status')=='DURU_26_PDF_RENDER_PARITY_PASS',
             'Duru PDF render parity not accepted')
    items=files_under(source)
    need(len(items)==report.get('final_file_count')==config['count'],'file count differs')
    allhashes=[]
    manifest_files={}
    for rel,f in items:
        content=f.read_bytes()
        sha=digest(content)
        allhashes.append(f'{rel}\t{sha}')
        manifest_files[rel]={'sha256':sha,'size_bytes':len(content)}
    tree=digest('\n'.join(allhashes).encode('utf-8'))
    need(tree==report.get('output_root_sha256'),'receipt and output filetree SHA mismatch')
    urls=sitemap_urls(source/'sitemap.xml')
    need(len(urls)==config['urls'] and all(u.startswith(config['site']+'/') for u in urls),
         'wrong sitemap origin/count')
    guide_paths=[p for p,_ in items if p.startswith('rehber/') and p.endswith('index.html')]
    need(len(guide_paths)>=5,'missing guide pages')
    need((source/'rehber/index.html').is_file() and (source/'rehber/post/index.html').is_file(),
         'missing guide landing or post index')
    for f in (source/'rehber').rglob('*.html'):
        if f.parts[-1]=='index.html' and f.relative_to(source).as_posix() in (
                'rehber/index.html','rehber/post/index.html'):
            pass
    require_pages=[config['site']+'/rehber/',config['site']+'/rehber/post/']
    need(all(x in urls for x in require_pages),'guide landing missing from sitemap')
    need(len([u for u in urls if u.startswith(config['site']+'/rehber/') and
              u not in ([config['site']+'/rehber/korfez-cocuk-model-portfoyu/',
                         config['site']+'/rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/'] if project=='SERDAR' else [])])==5,
         'new sitemap guide count not 5')
    robots=(source/'robots.txt').read_text(encoding='utf-8')
    need(not any(line.strip().lower()=='disallow: /' for line in robots.splitlines()),
         'production robots disallow all')
    if (source/'_headers').is_file():
        need('X-Robots-Tag: noindex' not in (source/'_headers').read_text(encoding='utf-8'),
             'production global noindex')
    pdfs=[p for p,_ in items if p.lower().endswith('.pdf')]
    if project=='SERDAR':
        need(all(f'downloads/Serdar-Armin-Sargut-Comp-Card-{x}.pdf' in pdfs for x in ('TR','EN','AR','RU')),
             'Serdar four generated Comp Card PDFs not present')
    else:
        need(len([x for x in pdfs if x.startswith('comp-card/pdf/')])==26,
             'Duru 26 Comp Card PDFs not present')
        need(len(list((source/'comp-card').glob('*/index.html')))==26,
             'Duru 26 HTML locale cards not present')
    need(len(pdfs)>=config['pdfs'],'missing generated PDFs')
    out_dir.mkdir(parents=True,exist_ok=False)
    tarfile_path=out_dir/(project.lower()+'-pinned-main-static-root.tar.gz')
    with tarfile_path.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='',compresslevel=4) as gz:
            with tarfile.open(fileobj=gz,mode='w',format=tarfile.PAX_FORMAT) as tar:
                for rel,f in items:
                    info=tarfile.TarInfo(rel)
                    info.size=f.stat().st_size
                    info.uid=0;info.gid=0;info.uname='';info.gname=''
                    info.mtime=0;info.mode=0o644
                    with f.open('rb') as stream:
                        tar.addfile(info,stream)
    manifest={
        'project':project,
        'status':'VERIFIED_PINNED_MAIN_ROOT_NOT_PUBLISHED',
        'production_publish_authorized':False,
        'production_published':False,
        'total_files':len(items),
        'existing_files_preserved':report['original_production_files_preserved'],
        'new_guide_files':12,
        'guide_html_pages':5,
        'sitemap_urls':len(urls),
        'pdf_count':len(pdfs),
        'filetree_sha256':tree,
        'tar_gzip_name':tarfile_path.name,
        'tar_gzip_sha256':digest(tarfile_path.read_bytes()),
        'tar_gzip_bytes':tarfile_path.stat().st_size,
        'files':manifest_files,
    }
    with tarfile_path.open('rb') as src:
        with tarfile.open(fileobj=src,mode='r:gz') as tar:
            names=tar.getnames()
            need(names==[x[0] for x in items],'archive filelist mismatch')
            for rel,_ in items:
                member=tar.extractfile(rel)
                need(member is not None and digest(member.read())==manifest_files[rel]['sha256'],
                     'archive file corruption: '+rel)
    manifest_path=out_dir/(project.lower()+'-pinned-main-manifest.json')
    manifest_path.write_text(json.dumps(manifest,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={k:v for k,v in manifest.items() if k!='files'}
    print(project+'_PINNED_MAIN_FROZEN_RELEASE_NO_DEPLOY_PASS: '+json.dumps(summary,sort_keys=True),flush=True)
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--project',required=True,choices=PROJECTS)
    p.add_argument('--static-root',required=True,type=Path)
    p.add_argument('--receipt',required=True,type=Path)
    p.add_argument('--local-http-acceptance',required=True,type=Path)
    p.add_argument('--pdf-parity',type=Path,default=None)
    p.add_argument('--output-dir',required=True,type=Path)
    args=p.parse_args()
    freeze(args.project,args.static_root,args.receipt,args.local_http_acceptance,args.output_dir,args.pdf_parity)