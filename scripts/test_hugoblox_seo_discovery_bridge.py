#!/usr/bin/env python3
"""Synthetic negative/positive acceptance tests for staging-only homepage SEO bridge."""
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from hugoblox_seo_discovery_bridge import CONFIG, main

NS='{http://www.sitemaps.org/schemas/sitemap/0.9}'

def make_root(root, name):
    c=CONFIG[name]
    root.mkdir()
    (root/'rehber').mkdir()
    (root/'rehber/index.html').write_text('<html lang="tr"><body><h1>Rehber</h1></body></html>')
    for p in c['protected']:
        f=root/p;f.parent.mkdir(parents=True,exist_ok=True)
        f.write_bytes(b'%PDF-fake unit test' if p.endswith('.pdf') else b'<html><h1>Original</h1></html>')
    footer=('<footer class="footer">'+c['needle'] if name=='SERDAR' else '<footer class="site-footer">'+c['needle']+'</footer>')
    html=f'<html><head><title>Portfolio Title</title><link rel="canonical" href="{c["origin"]}/"></head><body><h1>Portfolio</h1><main>Portfolio content</main>{footer}</body></html>'
    (root/'index.html').write_text(html,encoding='utf-8')
    (root/'robots.txt').write_text('User-agent: *\nAllow: /\n')
    sitemap=ET.Element(NS+'urlset')
    for i in range(c['urls']):
        u=c['origin']+'/rehber/' if i==0 else c['origin']+'/sample-'+str(i)+'/'
        ET.SubElement(ET.SubElement(sitemap,NS+'url'),NS+'loc').text=u
    ET.ElementTree(sitemap).write(root/'sitemap.xml',encoding='utf-8',xml_declaration=True)

for name in CONFIG:
    with tempfile.TemporaryDirectory(prefix='seo-bridge-test-'+name.lower()) as d:
        root=Path(d)
        make_root(root/'src',name)
        a=main(name,root/'src',root/'out',root/'report.json')
        assert a['status']=='SEO_DISCOVERY_BRIDGE_STAGING_ONLY_PASS'
        assert a['changed_original_files']==['index.html']
        assert a['production_published'] is False
        # A second injection onto an already amended homepage MUST fail.
        try:main(name,root/'out',root/'twice',root/'twice.json');raise AssertionError('Duplicate not blocked')
        except AssertionError as e:
            assert 'href="/rehber/"' in str(e) or 'footer anchor' in str(e),str(e)
        # Missing destination MUST fail.
        (root/'src'/'rehber/index.html').unlink()
        try:main(name,root/'src',root/'missing',root/'missing.json');raise AssertionError('Missing guide not blocked')
        except AssertionError as e:
            assert 'guide destination missing' in str(e),str(e)
        # Creating on top of an existing output MUST fail.
        try:main(name,root/'out',root/'out',root/'replay.json');raise AssertionError('Self overwrite not blocked')
        except AssertionError as e:
            assert 'already exists' in str(e) or 'overlapping paths' in str(e)
        print(name+'_SEO_DISCOVERY_BRIDGE_SYNTHETIC_TEST_PASS')
print('SEO_DISCOVERY_BRIDGE_SYNTHETIC_TESTS_PASS')