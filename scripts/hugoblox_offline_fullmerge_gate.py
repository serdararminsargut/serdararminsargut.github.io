#!/usr/bin/env python3
"""OFFLINE no-deploy HugoBlox + existing portfolio merger/release gate.

Consumes a pre-overlay, production-style static baseline and the separately
approved, transformed HugoBlox release-candidate tree.  Copies both to a fresh
TEMPORARY output, verifies old bytes unchanged and tests all new pages locally.
This script DOES NOT publish or update GitHub, Cloudflare, DNS or sitemaps.
"""
import argparse
import base64
import hashlib
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import sys
from threading import Thread
from urllib.request import urlopen
from xml.etree import ElementTree as ET

NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
PROJECTS = {
    'SERDAR': {
        'origin': 'https://serdararminsargut.com', 'old_urls': 90,
        'new_pages': ('index.html', 'post/index.html',
            'post/cocuk-giyim-e-ticaret-cekimlerinde-portfoy-secimi/index.html',
            'post/spor-giyim-ayakkabi-katalog-fotograflari/index.html',
            'post/cocuk-oyuncu-casting-sunum-dosyasi/index.html'),
        'old_protected': ('index.html', 'en/index.html', 'ar/index.html',
            'ru/index.html', 'az/index.html', 'kk/index.html',
            'uz/index.html', 'ky/index.html',
            'rehber/korfez-cocuk-model-portfoyu/index.html',
            'rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/index.html'),
        'other': 'Duru Mualla Sargut',
    },
    'DURU': {
        'origin': 'https://durumuallasargut.com', 'old_urls': 31,
        'new_pages': ('index.html', 'post/index.html',
            'post/tiyatro-deneyiminden-kamera-onu-oyunculuguna/index.html',
            'post/cocuk-oyuncu-self-tape-dosya-duzeni/index.html',
            'post/genc-oyuncu-showreel-sahne-ve-ekran-secimi/index.html'),
        'old_protected': ('index.html',),
        'other': 'Serdar Armin Sargut',
    },
}


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sitemap_urls(path):
    check(path.is_file(), 'Missing sitemap: ' + str(path))
    root = ET.parse(path).getroot()
    check(root.tag.endswith('}urlset'), 'Incorrect sitemap namespace/structure')
    locs = [node.text.strip() for node in root.findall(f'{{{NS}}}url/{{{NS}}}loc')]
    check(len(locs) == len(set(locs)), 'Duplicate sitemap URLs')
    return root, locs


def relative_name(name):
    return Path('rehber') / name


def route_for(name):
    return '/rehber/' if name == 'index.html' else '/rehber/' + name.removesuffix('index.html')


class ReadHead(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.in_title = False
        self.in_ldjson = False
        self.title = ''
        self.lang = ''
        self.h1 = 0
        self.description = []
        self.robots = []
        self.canonical = []
        self.og_url = []
        self.og_title = []
        self.css = []
        self.jsonld = []
        self.local_links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang', '')
        if tag == 'head':
            self.in_head = True
        if tag == 'title' and self.in_head:
            self.in_title = True
        if tag == 'h1':
            self.h1 += 1
        if tag == 'script' and self.in_head and a.get('type', '').lower() == 'application/ld+json':
            self.in_ldjson = True
        if tag == 'meta' and self.in_head:
            key = (a.get('name') or a.get('property') or '').lower()
            if key == 'description':
                self.description.append(a.get('content', ''))
            if key == 'robots':
                self.robots.append(a.get('content', ''))
            if key == 'og:url':
                self.og_url.append(a.get('content', ''))
            if key == 'og:title':
                self.og_title.append(a.get('content', ''))
        if tag == 'link' and self.in_head:
            rel = (a.get('rel') or '').lower().split()
            if 'canonical' in rel:
                self.canonical.append(a.get('href', ''))
            if 'stylesheet' in rel:
                self.css.append((a.get('href', ''), a.get('integrity', '')))
        if tag == 'a':
            self.local_links.append(a.get('href', ''))

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'head':
            self.in_head = False
        if tag == 'script':
            self.in_ldjson = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_ldjson:
            self.jsonld.append(data)


def read_head(path, config, expected, merged):
    html = path.read_text(encoding='utf-8')
    check(config['other'] not in html, 'Cross-profile identity leak at ' + expected)
    for forbidden in ('PORTFOLIO_AUTOSYNC_PREVIEW_START',
                      'PORTFOLIO_AUTOSYNC_PREVIEW_END',
                      'Resmî portföyden güncel bilgiler (test)',
                      '/rehber/portfoy-guncel/', 'source-status.json',
                      'x-preview-purpose', 'example.invalid'):
        check(forbidden not in html, 'Preview/diagnostic leak: ' + forbidden + ' in ' + expected)
    p = ReadHead()
    p.feed(html)
    check(p.lang.lower().split('-')[0] == 'tr', 'Incorrect lang at ' + expected)
    check(p.h1 == 1, 'Expected exactly one H1 at ' + expected)
    check(len(p.title.strip()) >= 15, 'Missing title at ' + expected)
    check(len(p.description) == 1 and len(p.description[0]) >= 25, 'Invalid description at ' + expected)
    check(len(p.robots) == 1 and p.robots[0].replace(' ', '').lower() == 'index,follow',
          'Incorrect production robots at ' + expected)
    check(p.canonical == [expected], 'Missing/non-self/duplicate canonical at ' + expected)
    check(p.og_url == [expected], 'OG URL mismatch/duplicate at ' + expected)
    check(len(p.og_title) == 1, 'OG title missing/duplicate at ' + expected)
    check(len(p.jsonld) >= 1, 'JSON-LD missing at ' + expected)
    schemas = [json.loads(x) for x in p.jsonld if x.strip()]
    check(any(isinstance(v, dict) and v.get('url') == expected and
              v.get('@type') in ('CollectionPage', 'Article') for v in schemas),
          'Incorrect page JSON-LD at ' + expected)
    css_verified = 0
    for href, integrity in p.css:
        check(not href.startswith('/css/'), 'Unrewritten CSS path at ' + expected)
        if href.startswith('/rehber/css/'):
            actual = merged / href.lstrip('/')
            check(actual.is_file(), 'Missing compiled CSS: ' + href)
            if integrity:
                check(integrity.startswith(('sha256-', 'sha384-', 'sha512-')),
                      'Unexpected CSS integrity algorithm: ' + href)
                alg, b64 = integrity.split('-', 1)
                computed = base64.b64encode(hashlib.new(alg, actual.read_bytes()).digest()).decode()
                check(computed == b64, 'Mismatched CSS SRI: ' + href)
            else:
                # HugoBlox sometimes embeds a SHA-256 digest into a same-origin
                # stylesheet filename instead of adding an SRI attribute.
                # Require exact byte-to-filename agreement.
                parts = actual.name.split(".")
                stamp = parts[-2] if len(parts) >= 3 else ""
                check(len(stamp) == 64 and all(ch in "0123456789abcdef" for ch in stamp)
                      and digest(actual) == stamp,
                      'CSS lacks verified SRI or SHA-256 filename fingerprint: ' + href)
            css_verified += 1
    check(css_verified > 0, 'No verified HugoBlox CSS at ' + expected)
    for href in p.local_links:
        check(not href.startswith('/post/'), 'Unrewritten /post/ link at ' + expected)
        check(not href.startswith('/media/'), 'Unrewritten /media/ link at ' + expected)
        if href.startswith('/rehber/') and not href.startswith('/rehber/#'):
            path_part = href.split('#', 1)[0].split('?', 1)[0]
            if path_part:
                target = merged / path_part.lstrip('/')
                if path_part.endswith('/'):
                    target = target / 'index.html'
                check(target.is_file(), 'Broken internal guide link: ' + href)
    return {'url': expected, 'title': p.title.strip(), 'css_sri_links': css_verified,
            'h1': p.h1, 'robots': p.robots[0], 'canonical': p.canonical[0]}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def http_probe(merged, routes, origin):
    # Uses loopback only, NEVER production endpoints.
    from functools import partial
    handler = partial(QuietHandler, directory=str(merged))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for path in routes:
            url = f'http://127.0.0.1:{server.server_port}{path}'
            with urlopen(url, timeout=5) as response:
                check(response.status == 200, 'Local merged HTTP not 200: ' + path)
                markup = response.read().decode('utf-8')
                check(origin + path in markup, 'Wrong local merged page at ' + path)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def main(project, baseline, release, output):
    project = project.upper()
    check(project in PROJECTS, 'Unknown project')
    cfg = PROJECTS[project]
    baseline, release, output = (x.resolve() for x in (baseline, release, output))
    check(baseline.is_dir() and release.is_dir(), 'Missing baseline or release candidate tree')
    check(not output.exists(), 'Output must not already exist (fail closed)')
    for a, b in ((baseline, output), (release, output), (output, baseline), (output, release)):
        check(a not in b.parents, 'Output may not overlap source')
    for root in (baseline, release):
        check(not any(p.is_symlink() for p in root.rglob('*')), 'Symlinks not allowed in merge source')
    check((baseline/'index.html').is_file(), 'Missing original portfolio homepage')
    check((baseline/'robots.txt').is_file(), 'Original robots missing')
    if project == 'SERDAR':
        check((baseline/'_headers').is_file(), 'Original Serdar headers missing')
    check(not any(line.strip().lower() == 'disallow: /'
                  for line in (baseline/'robots.txt').read_text().splitlines()),
          'Production-like baseline robots globally disallow indexing')
    if (baseline/'_headers').is_file():
        check('X-Robots-Tag: noindex' not in (baseline/'_headers').read_text(encoding='utf-8'),
              'Production-like baseline header blocks indexing')
    for name in cfg['old_protected']:
        check((baseline / name).is_file(), 'Missing old protected path: ' + name)
    if project == 'DURU':
        comp_card = baseline/'comp-card'
        html = list(comp_card.glob('*/index.html'))
        pdfs = list(comp_card.rglob('*.pdf'))
        check(len(html) == 26 and len(pdfs) == 26, 'Expected 26 HTML and 26 PDFs')
        for pdf in pdfs:
            check(pdf.open('rb').read(5) == b'%PDF-', 'Invalid PDF signature: ' + pdf.name)
    original_files = {p.relative_to(baseline): digest(p) for p in baseline.rglob('*') if p.is_file()}
    original_sitemap = baseline/'sitemap.xml'
    sitemap, old_urls = sitemap_urls(original_sitemap)
    check(len(old_urls) == cfg['old_urls'], f'Baseline URL count mismatch {len(old_urls)}')
    check(all(u.startswith(cfg['origin'] + '/') for u in old_urls), 'Other domain in baseline sitemap')
    secondary = baseline/'sitemap-google.xml'
    if project == 'SERDAR':
        _, secondary_urls = sitemap_urls(secondary)
        check(secondary_urls == old_urls, 'Serdar Google sitemap disagrees with primary')
    else:
        check(not secondary.exists(), 'Unexpected secondary sitemap on Duru')

    rmanifest = json.loads((release/'manifest.json').read_text(encoding='utf-8'))
    check(rmanifest.get('production_publish_authorized') is False and
          rmanifest.get('status') == 'OFFLINE_CANDIDATE_NOT_PUBLISHED',
          'Release candidate is not properly marked as NOT PUBLISHED')
    check(rmanifest.get('project') == project + '_ONLY', 'Cross-project release manifest')
    new_urls = [cfg['origin'] + route_for(n) for n in cfg['new_pages']]
    supplied_urls = rmanifest.get('candidate_urls', rmanifest.get('urls'))
    check(supplied_urls == new_urls, 'Release candidate URL order/content changed')
    check(not set(new_urls).intersection(old_urls), 'New guide route collides with existing sitemap')
    src = release/'rehber'
    check(src.is_dir() and not (src/'portfoy-guncel').exists(), 'Release contains diagnostics')
    for name in cfg['new_pages']:
        check((src/name).is_file(), 'Missing candidate HTML: ' + name)
        check(not (baseline/'rehber'/name).exists(), 'Refusing to overwrite existing route ' + name)

    # Only under an isolated temporary output, no deployment to any system.
    merged = output/'merged-root'
    shutil.copytree(baseline, merged)
    for obj in src.rglob('*'):
        if obj.is_dir():
            continue
        rel = obj.relative_to(release)
        dest = merged/rel
        check(not dest.exists(), 'Baseline collision, refusing to overwrite: ' + str(rel))
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(obj, dest)

    for name, oldhash in original_files.items():
        if name in (Path('sitemap.xml'), Path('sitemap-google.xml')):
            continue
        check((merged/name).is_file() and digest(merged/name) == oldhash,
              'Original file changed or missing: ' + str(name))
    for name in cfg['new_pages']:
        check((merged/'rehber'/name).is_file(), 'New file absent after merge')

    # Deep-copy existing XML nodes by mutating in-memory tree; preserves all old URLs.
    for path in (['sitemap.xml', 'sitemap-google.xml'] if project == 'SERDAR' else ['sitemap.xml']):
        root, current = sitemap_urls(merged/path)
        check(current == old_urls, 'Baseline XML mismatch in simulated merge')
        for u in new_urls:
            ET.SubElement(ET.SubElement(root, '{' + NS + '}url'), '{' + NS + '}loc').text = u
        ET.register_namespace('', NS)
        ET.ElementTree(root).write(merged/path, encoding='utf-8', xml_declaration=True)
        _, result = sitemap_urls(merged/path)
        check(result == old_urls + new_urls, 'Incorrect merged sitemap order')

    records = [read_head(merged/'rehber'/name, cfg, cfg['origin']+route_for(name), merged)
               for name in cfg['new_pages']]
    titles = [x['title'] for x in records]
    check(len(titles) == len(set(titles)), 'Duplicate HugoBlox titles')
    landing = (merged/'rehber/index.html').read_text(encoding='utf-8')
    if project == 'SERDAR':
        for cta in (cfg['origin']+'/', cfg['origin']+'/casting-card/tr.html',
                    'https://www.instagram.com/serdararminsargutt/'):
            check(cta in landing, 'CTA missing in combined root: ' + cta)
        for name in cfg['old_protected']:
            check(digest(merged/name) == original_files[Path(name)],
                  'Existing legacy Serdar content changed: ' + name)
    else:
        check('portfolio-live-preview' in landing and 'Videoyu izle' in landing,
              'Duru compact video section absent')
        check(len(list((merged/'comp-card').glob('*/index.html'))) == 26,
              'Duru 26 language HTML lost')
        check(len(list((merged/'comp-card').rglob('*.pdf'))) == 26,
              'Duru 26 PDFs lost')
    check(not (merged/'rehber/portfoy-guncel').exists(), 'Diagnostic route leaked')
    http_probe(merged, [route_for(name) for name in cfg['new_pages']], cfg['origin'])

    summary = {
        'project': project, 'status': 'OFFLINE_FULL_MERGE_PASS', 'production_published': False,
        'production_publish_authorized': False, 'merged_root_is_local_temporary': True,
        'original_files_hash_preserved': len(original_files)- (2 if project=='SERDAR' else 1),
        'baseline_sitemap_urls': len(old_urls), 'new_rehber_urls': len(new_urls),
        'offline_merged_sitemap_urls': len(old_urls)+len(new_urls),
        'local_http_200': len(new_urls), 'html_checks': records,
        'legacy_serdar_pages': 10 if project=='SERDAR' else None,
        'duru_locale_html_pdf_count': [26, 26] if project=='DURU' else None,
        'preview_data_excluded': True,
        'requires_external_cloudflare_verification': True,
    }
    output.mkdir(exist_ok=True)
    (output/'offline_full_merge_report.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(project + '_OFFLINE_FULL_MERGE_PASS: ' + str(len(old_urls)) + '+' + str(len(new_urls)) +
          ' URLs, ' + str(len(new_urls)) + ' local HTTP 200, original files unchanged; NO DEPLOY', flush=True)
    return summary


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', choices=PROJECTS, required=True)
    ap.add_argument('--baseline-root', type=Path, required=True)
    ap.add_argument('--release-root', type=Path, required=True)
    ap.add_argument('--output-root', type=Path, required=True)
    args = ap.parse_args()
    main(args.project, args.baseline_root, args.release_root, args.output_root), actual.name)
                check(match is not None and digest(actual) == match.group(1),
                      'CSS has neither verified SRI nor matching SHA-256 filename: ' + href)
            css_verified += 1
    check(css_verified > 0, 'No verified HugoBlox CSS at ' + expected)
    for href in p.local_links:
        check(not href.startswith('/post/'), 'Unrewritten /post/ link at ' + expected)
        check(not href.startswith('/media/'), 'Unrewritten /media/ link at ' + expected)
        if href.startswith('/rehber/') and not href.startswith('/rehber/#'):
            path_part = href.split('#', 1)[0].split('?', 1)[0]
            if path_part:
                target = merged / path_part.lstrip('/')
                if path_part.endswith('/'):
                    target = target / 'index.html'
                check(target.is_file(), 'Broken internal guide link: ' + href)
    return {'url': expected, 'title': p.title.strip(), 'css_sri_links': css_verified,
            'h1': p.h1, 'robots': p.robots[0], 'canonical': p.canonical[0]}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def http_probe(merged, routes, origin):
    # Uses loopback only, NEVER production endpoints.
    from functools import partial
    handler = partial(QuietHandler, directory=str(merged))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for path in routes:
            url = f'http://127.0.0.1:{server.server_port}{path}'
            with urlopen(url, timeout=5) as response:
                check(response.status == 200, 'Local merged HTTP not 200: ' + path)
                markup = response.read().decode('utf-8')
                check(origin + path in markup, 'Wrong local merged page at ' + path)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def main(project, baseline, release, output):
    project = project.upper()
    check(project in PROJECTS, 'Unknown project')
    cfg = PROJECTS[project]
    baseline, release, output = (x.resolve() for x in (baseline, release, output))
    check(baseline.is_dir() and release.is_dir(), 'Missing baseline or release candidate tree')
    check(not output.exists(), 'Output must not already exist (fail closed)')
    for a, b in ((baseline, output), (release, output), (output, baseline), (output, release)):
        check(a not in b.parents, 'Output may not overlap source')
    for root in (baseline, release):
        check(not any(p.is_symlink() for p in root.rglob('*')), 'Symlinks not allowed in merge source')
    check((baseline/'index.html').is_file(), 'Missing original portfolio homepage')
    check((baseline/'robots.txt').is_file(), 'Original robots missing')
    if project == 'SERDAR':
        check((baseline/'_headers').is_file(), 'Original Serdar headers missing')
    check(not any(line.strip().lower() == 'disallow: /'
                  for line in (baseline/'robots.txt').read_text().splitlines()),
          'Production-like baseline robots globally disallow indexing')
    if (baseline/'_headers').is_file():
        check('X-Robots-Tag: noindex' not in (baseline/'_headers').read_text(encoding='utf-8'),
              'Production-like baseline header blocks indexing')
    for name in cfg['old_protected']:
        check((baseline / name).is_file(), 'Missing old protected path: ' + name)
    if project == 'DURU':
        comp_card = baseline/'comp-card'
        html = list(comp_card.glob('*/index.html'))
        pdfs = list(comp_card.rglob('*.pdf'))
        check(len(html) == 26 and len(pdfs) == 26, 'Expected 26 HTML and 26 PDFs')
        for pdf in pdfs:
            check(pdf.open('rb').read(5) == b'%PDF-', 'Invalid PDF signature: ' + pdf.name)
    original_files = {p.relative_to(baseline): digest(p) for p in baseline.rglob('*') if p.is_file()}
    original_sitemap = baseline/'sitemap.xml'
    sitemap, old_urls = sitemap_urls(original_sitemap)
    check(len(old_urls) == cfg['old_urls'], f'Baseline URL count mismatch {len(old_urls)}')
    check(all(u.startswith(cfg['origin'] + '/') for u in old_urls), 'Other domain in baseline sitemap')
    secondary = baseline/'sitemap-google.xml'
    if project == 'SERDAR':
        _, secondary_urls = sitemap_urls(secondary)
        check(secondary_urls == old_urls, 'Serdar Google sitemap disagrees with primary')
    else:
        check(not secondary.exists(), 'Unexpected secondary sitemap on Duru')

    rmanifest = json.loads((release/'manifest.json').read_text(encoding='utf-8'))
    check(rmanifest.get('production_publish_authorized') is False and
          rmanifest.get('status') == 'OFFLINE_CANDIDATE_NOT_PUBLISHED',
          'Release candidate is not properly marked as NOT PUBLISHED')
    check(rmanifest.get('project') == project + '_ONLY', 'Cross-project release manifest')
    new_urls = [cfg['origin'] + route_for(n) for n in cfg['new_pages']]
    supplied_urls = rmanifest.get('candidate_urls', rmanifest.get('urls'))
    check(supplied_urls == new_urls, 'Release candidate URL order/content changed')
    check(not set(new_urls).intersection(old_urls), 'New guide route collides with existing sitemap')
    src = release/'rehber'
    check(src.is_dir() and not (src/'portfoy-guncel').exists(), 'Release contains diagnostics')
    for name in cfg['new_pages']:
        check((src/name).is_file(), 'Missing candidate HTML: ' + name)
        check(not (baseline/'rehber'/name).exists(), 'Refusing to overwrite existing route ' + name)

    # Only under an isolated temporary output, no deployment to any system.
    merged = output/'merged-root'
    shutil.copytree(baseline, merged)
    for obj in src.rglob('*'):
        if obj.is_dir():
            continue
        rel = obj.relative_to(release)
        dest = merged/rel
        check(not dest.exists(), 'Baseline collision, refusing to overwrite: ' + str(rel))
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(obj, dest)

    for name, oldhash in original_files.items():
        if name in (Path('sitemap.xml'), Path('sitemap-google.xml')):
            continue
        check((merged/name).is_file() and digest(merged/name) == oldhash,
              'Original file changed or missing: ' + str(name))
    for name in cfg['new_pages']:
        check((merged/'rehber'/name).is_file(), 'New file absent after merge')

    # Deep-copy existing XML nodes by mutating in-memory tree; preserves all old URLs.
    for path in (['sitemap.xml', 'sitemap-google.xml'] if project == 'SERDAR' else ['sitemap.xml']):
        root, current = sitemap_urls(merged/path)
        check(current == old_urls, 'Baseline XML mismatch in simulated merge')
        for u in new_urls:
            ET.SubElement(ET.SubElement(root, '{' + NS + '}url'), '{' + NS + '}loc').text = u
        ET.register_namespace('', NS)
        ET.ElementTree(root).write(merged/path, encoding='utf-8', xml_declaration=True)
        _, result = sitemap_urls(merged/path)
        check(result == old_urls + new_urls, 'Incorrect merged sitemap order')

    records = [read_head(merged/'rehber'/name, cfg, cfg['origin']+route_for(name), merged)
               for name in cfg['new_pages']]
    titles = [x['title'] for x in records]
    check(len(titles) == len(set(titles)), 'Duplicate HugoBlox titles')
    landing = (merged/'rehber/index.html').read_text(encoding='utf-8')
    if project == 'SERDAR':
        for cta in (cfg['origin']+'/', cfg['origin']+'/casting-card/tr.html',
                    'https://www.instagram.com/serdararminsargutt/'):
            check(cta in landing, 'CTA missing in combined root: ' + cta)
        for name in cfg['old_protected']:
            check(digest(merged/name) == original_files[Path(name)],
                  'Existing legacy Serdar content changed: ' + name)
    else:
        check('portfolio-live-preview' in landing and 'Videoyu izle' in landing,
              'Duru compact video section absent')
        check(len(list((merged/'comp-card').glob('*/index.html'))) == 26,
              'Duru 26 language HTML lost')
        check(len(list((merged/'comp-card').rglob('*.pdf'))) == 26,
              'Duru 26 PDFs lost')
    check(not (merged/'rehber/portfoy-guncel').exists(), 'Diagnostic route leaked')
    http_probe(merged, [route_for(name) for name in cfg['new_pages']], cfg['origin'])

    summary = {
        'project': project, 'status': 'OFFLINE_FULL_MERGE_PASS', 'production_published': False,
        'production_publish_authorized': False, 'merged_root_is_local_temporary': True,
        'original_files_hash_preserved': len(original_files)- (2 if project=='SERDAR' else 1),
        'baseline_sitemap_urls': len(old_urls), 'new_rehber_urls': len(new_urls),
        'offline_merged_sitemap_urls': len(old_urls)+len(new_urls),
        'local_http_200': len(new_urls), 'html_checks': records,
        'legacy_serdar_pages': 10 if project=='SERDAR' else None,
        'duru_locale_html_pdf_count': [26, 26] if project=='DURU' else None,
        'preview_data_excluded': True,
        'requires_external_cloudflare_verification': True,
    }
    output.mkdir(exist_ok=True)
    (output/'offline_full_merge_report.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(project + '_OFFLINE_FULL_MERGE_PASS: ' + str(len(old_urls)) + '+' + str(len(new_urls)) +
          ' URLs, ' + str(len(new_urls)) + ' local HTTP 200, original files unchanged; NO DEPLOY', flush=True)
    return summary


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', choices=PROJECTS, required=True)
    ap.add_argument('--baseline-root', type=Path, required=True)
    ap.add_argument('--release-root', type=Path, required=True)
    ap.add_argument('--output-root', type=Path, required=True)
    args = ap.parse_args()
    main(args.project, args.baseline_root, args.release_root, args.output_root)