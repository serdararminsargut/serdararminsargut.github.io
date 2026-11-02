#!/usr/bin/env python3
"""Synthetic positive and negative tests; never use production site data."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).parent))
from hugoblox_offline_fullmerge_gate import main, PROJECTS, route_for, NS


def sitemap(path, urls):
    root=ET.Element('{'+NS+'}urlset')
    for u in urls:
        ET.SubElement(ET.SubElement(root,'{'+NS+'}url'),'{'+NS+'}loc').text=u
    ET.register_namespace('',NS)
    ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)


def make_env(base, project):
    cfg=PROJECTS[project]
    origin=cfg['origin']
    baseline=base/'baseline';release=base/'release';baseline.mkdir();release.mkdir()
    for p in cfg['old_protected']:
        f=baseline/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('<h1>Original</h1>',encoding='utf8')
    (baseline/'robots.txt').write_text('User-agent: *\nAllow: /\n',encoding='utf8')
    (baseline/'_headers').write_text('/*\n  Referrer-Policy: strict-origin-when-cross-origin\n',encoding='utf8')
    old_urls=[origin+'/']+[origin+'/old-'+str(i)+'/' for i in range(cfg['old_urls']-1)]
    sitemap(baseline/'sitemap.xml',old_urls)
    if project=='SERDAR':sitemap(baseline/'sitemap-google.xml',old_urls)
    else:
        for j in range(26):
            p=baseline/f'comp-card/lang{j}/index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('good',encoding='utf8')
            p=baseline/f'comp-card/pdf/lang{j}.pdf';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'%PDF-1.7 dummy')
    src=release/'rehber';src.mkdir()
    css=src/'css/a.css';css.parent.mkdir(parents=True);css.write_text('body { color: black; }',encoding='utf8')
    hashb64=base64.b64encode(hashlib.sha256(css.read_bytes()).digest()).decode()
    for i,name in enumerate(cfg['new_pages']):
        p=src/name;p.parent.mkdir(parents=True,exist_ok=True)
        route=route_for(name);url=origin+route
        cta=(' '.join(['<a href="'+origin+'/">Portfolio</a>','<a href="'+origin+'/casting-card/tr.html">Casting</a>', '<a href="https://www.instagram.com/serdararminsargutt/">Instagram</a>'])
             if project=='SERDAR' else '<section id="portfolio-live-preview">Videoyu izle</section>')
        internal='<a href="/rehber/post/">Posts</a>'
        schema=json.dumps({'@context':'https://schema.org','@type':'Article' if i>1 else 'CollectionPage','url':url})
        text=f'''<!doctype html><html lang="tr"><head><title>{project} portföy rehberi {i} unique</title><meta name="description" content="Oyuncu ve model rehberlerinden faydalı bilgiler {i} burada."><meta name="robots" content="index,follow"><meta property="og:title" content="{project} guide {i}"><meta property="og:url" content="{url}"><link rel="canonical" href="{url}"><link rel="stylesheet" href="/rehber/css/a.css" integrity="sha256-{hashb64}"><script type="application/ld+json">{schema}</script></head><body><h1>Guide {i}</h1>{cta}{internal}</body></html>'''
        p.write_text(text,encoding='utf8')
    manifest={'project':project+'_ONLY','status':'OFFLINE_CANDIDATE_NOT_PUBLISHED','production_publish_authorized':False,
              'candidate_urls' if project=='SERDAR' else 'urls':[origin+route_for(n) for n in cfg['new_pages']]}
    (release/'manifest.json').write_text(json.dumps(manifest),encoding='utf8')
    return baseline,release


def expect_fail(project,root,change,label):
    baseline,release=make_env(root,project)
    change(baseline,release)
    try:
        main(project,baseline,release,root/'output')
    except (AssertionError, ValueError, FileNotFoundError, OSError) as ex:
        print('NEGATIVE_PASS',project,label,str(ex)[:140]);return
    raise AssertionError('Should have rejected '+project+' '+label)


def run():
    for project in PROJECTS:
        with tempfile.TemporaryDirectory(prefix='hugoblox-mergetest-') as d:
            root=Path(d)
            base,release=make_env(root,project)
            result=main(project,base,release,root/'output')
            assert result['local_http_200']==5
            print('POSITIVE_PASS',project,result['offline_merged_sitemap_urls'])
        tests={
            'noindex':lambda b,r:(r/'rehber/index.html').write_text((r/'rehber/index.html').read_text().replace('index,follow','noindex,follow'),encoding='utf8'),
            'css_integrity':lambda b,r:(r/'rehber/css/a.css').write_text('tampered',encoding='utf8'),
            'canonical':lambda b,r:(r/'rehber/index.html').write_text((r/'rehber/index.html').read_text().replace('rel="canonical" href="https://','rel="canonical" href="https://other-'),encoding='utf8'),
            'route_collision':lambda b,r:((b/'rehber').mkdir(exist_ok=True),(b/'rehber/index.html').write_text('existing',encoding='utf8')),
            'robots_disallow':lambda b,r:(b/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf8'),
            'missing_post':lambda b,r:(r/'rehber'/PROJECTS[project]['new_pages'][3]).unlink(),
        }
        for label,change in tests.items():
            with tempfile.TemporaryDirectory(prefix='hugoblox-nega-') as d:
                root=Path(d)
                expect_fail(project,root,change,label)
    print('OFFLINE_FULL_MERGE_SELFTEST_PASS: 2 positive + 12 fail-closed examples')

if __name__=='__main__':run()