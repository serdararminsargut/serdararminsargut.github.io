#!/usr/bin/env python3
"""Read-only gate for isolated, production-style HugoBlox SOURCE release candidates.

No deploy, git mutation, DNS or Cloudflare API operations. CI needs only local files.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

CONFIG = {
 'SERDAR': {'count':174,'sitemap':95,'pdf':4,'origin':'https://serdararminsargut.com',
            'main':'bb4737ed7367b84008c860ec3f722055a56ae518'},
 'DURU':   {'count':128,'sitemap':36,'pdf':26,'origin':'https://durumuallasargut.com',
            'main':'0455109adba70ce54f0424090c95e64d527dd9bd'},
}
NS = {'x':'http://www.sitemaps.org/schemas/sitemap/0.9'}


def need(yes,desc):
    if not yes: raise AssertionError('SOURCE_RELEASE_NO_GO: '+desc)


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def check(project, repo, built):
    cfg=CONFIG[project]
    meta=json.loads((repo/'release-candidate/hugoblox-source-manifest.json').read_text(encoding='utf-8'))
    need(meta['project']==project and meta['main_sha']==cfg['main'],'incorrect project or main anchor')
    need(meta['production_publish_authorized'] is False and meta['production_published'] is False,
         'unexpected publication flag')
    expected=meta['source_sha256']
    need(len(expected) in (12,15), 'wrong approved source list count')
    for rel, sha in expected.items():
        path=repo/rel
        need(path.is_file() and digest(path)==sha,'source differs from pinned HugoBlox release: '+rel)
    changed=subprocess.check_output(['git','diff','--name-only',cfg['main']+'..HEAD'],cwd=repo,text=True).splitlines()
    allowed=set(expected) | {'release-candidate/hugoblox-source-manifest.json',
      '.github/workflows/hugoblox-source-release-candidate-ci.yml',
      'scripts/hugoblox_source_release_ci.py','scripts/hugoblox_source_release_http_qa.py'}
    if project=='SERDAR': allowed.add('scripts/prepare_serdar_production_main_static.py')
    else: allowed.update({'build.sh','scripts/hugoblox_production_source_overlay.py'})
    need(set(changed)==allowed, 'unexpected source diff paths: '+repr(sorted(set(changed)^allowed)))
    need(built.is_dir() and not built.is_symlink(),'missing built root')
    need(not any(f.is_symlink() for f in built.rglob('*')),'symlinks forbidden')
    output={f.relative_to(built).as_posix():digest(f) for f in built.rglob('*') if f.is_file()}
    need(len(output)==cfg['count'],'unexpected production build file count: '+str(len(output)))
    for rel,sha in expected.items():
        builtpath=rel.removeprefix('site-overrides/hugoblox/')
        if builtpath in ('index.html','sitemap.xml','sitemap-google.xml') or builtpath.startswith('rehber/'):
            need(output.get(builtpath)==sha, 'built source asset/content differs: '+builtpath)
    home=(built/'index.html').read_text(encoding='utf-8')
    need(home.count('href="/rehber/"')==1,'missing or duplicate homepage guide link')
    robots=(built/'robots.txt').read_text(encoding='utf-8')
    need('Disallow: /' not in robots and cfg['origin'] in robots,'bad production robots')
    sitemap=ET.parse(built/'sitemap.xml').getroot()
    locs=[x.text for x in sitemap.findall('x:url/x:loc',NS)]
    need(len(locs)==cfg['sitemap'] and len(locs)==len(set(locs)),'sitemap wrong URL count/duplicates')
    need(all(u.startswith(cfg['origin']+'/') for u in locs),'sitemap cross-project domain')
    need(len([x for x in locs if x.startswith(cfg['origin']+'/rehber/')])==(7 if project=='SERDAR' else 5),'new+old guides wrong')
    if project=='SERDAR':
        sm2=ET.parse(built/'sitemap-google.xml').getroot()
        need([x.text for x in sm2.findall('x:url/x:loc',NS)]==locs,'Google sitemap differs')
        pdfs=[built/'downloads'/f'Serdar-Armin-Sargut-Comp-Card-{lang}.pdf' for lang in ('TR','EN','AR','RU')]
    else:
        need(len(list((built/'comp-card').glob('*/index.html')))==26,'26 locale HTML missing')
        pdfs=sorted((built/'comp-card/pdf').glob('*.pdf'))
    need(len(pdfs)==cfg['pdf'] and all(p.is_file() and p.read_bytes()[:5]==b'%PDF-' and p.stat().st_size>2000 for p in pdfs),
         'PDF count/signature invalid')
    print(f'{project}_SOURCE_RELEASE_NO_DEPLOY_PASS: {len(output)} files, {len(locs)} URLs, {len(pdfs)} PDFs; main unchanged')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--project',choices=CONFIG,required=True)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--built',type=Path,required=True)
    a=parser.parse_args();check(a.project,a.repo.resolve(),a.built.resolve())
