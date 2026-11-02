#!/usr/bin/env python3
"""Fail-closed LOCAL HTTP acceptance for an isolated HugoBlox production-main mirror.

NO network access beyond 127.0.0.1, NO production deployment or GitHub write.
The origin is compared only as an expected literal canonical value.
"""
import argparse
import json
from contextlib import contextmanager
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
from xml.etree import ElementTree as ET

CONFIG = {
    'SERDAR': {
        'origin': 'https://serdararminsargut.com',
        'guide': ('/rehber/', '/rehber/post/',
            '/rehber/post/cocuk-giyim-e-ticaret-cekimlerinde-portfoy-secimi/',
            '/rehber/post/spor-giyim-ayakkabi-katalog-fotograflari/',
            '/rehber/post/cocuk-oyuncu-casting-sunum-dosyasi/'),
        'legacy': ('/', '/en/', '/ar/', '/links/',
            '/rehber/korfez-cocuk-model-portfoyu/',
            '/rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/',
            '/casting-card/tr.html'),
        'sitemap': 95, 'pdf_count': 4,
        'pdf_base': 'downloads', 'other': 'Duru Mualla Sargut',
    },
    'DURU': {
        'origin': 'https://durumuallasargut.com',
        'guide': ('/rehber/', '/rehber/post/',
            '/rehber/post/tiyatro-deneyiminden-kamera-onu-oyunculuguna/',
            '/rehber/post/cocuk-oyuncu-self-tape-dosya-duzeni/',
            '/rehber/post/genc-oyuncu-showreel-sahne-ve-ekran-secimi/'),
        'legacy': ('/', '/links/', '/comp-card/tr/', '/comp-card/ar/',
            '/comp-card/ur/', '/comp-card/ko/'),
        'sitemap': 36, 'pdf_count': 26,
        'pdf_base': 'comp-card/pdf', 'other': 'Serdar Armin Sargut',
    }
}


def require(ok, msg):
    if not ok:
        raise AssertionError('LOCAL_HTTP_NO_GO: ' + msg)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_open = False
        self.title = ''
        self.h1 = 0
        self.lang = ''
        self.canonical = []
        self.og_url = []
        self.robots = []
        self.description = []
        self.styles = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang','')
        elif tag == 'h1':
            self.h1 += 1
        elif tag == 'title':
            self.title_open = True
        elif tag == 'link':
            r = a.get('rel','').lower().split()
            if 'canonical' in r:
                self.canonical.append(a.get('href',''))
            if 'stylesheet' in r:
                self.styles.append(a.get('href',''))
        elif tag == 'meta':
            k = (a.get('name') or a.get('property') or '').lower()
            if k == 'og:url':
                self.og_url.append(a.get('content',''))
            elif k == 'robots':
                self.robots.append(a.get('content',''))
            elif k == 'description':
                self.description.append(a.get('content',''))

    def handle_endtag(self, tag):
        if tag == 'title':
            self.title_open = False

    def handle_data(self, txt):
        if self.title_open:
            self.title += txt


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


@contextmanager
def local_server(site_root):
    srv = ThreadingHTTPServer(('127.0.0.1',0), partial(QuietHandler, directory=str(site_root)))
    worker = Thread(target=srv.serve_forever,daemon=True)
    worker.start()
    try:
        yield 'http://127.0.0.1:' + str(srv.server_port)
    finally:
        srv.shutdown()
        srv.server_close()
        worker.join(timeout=4)


def fetch(base, route):
    require(route.startswith('/') and '://' not in route and '..' not in route,
            'unsafe local route '+route)
    with urlopen(base+route,timeout=15) as resp:
        return resp.status,resp.headers.get('content-type',''),resp.read()


def run(project,site_root,out):
    project=project.upper()
    require(project in CONFIG,'project unknown')
    cfg=CONFIG[project]
    root=site_root.resolve()
    require(root.is_dir(),'static root missing')
    require(not any(p.is_symlink() for p in root.rglob('*')),'symlinks in static root')
    old_routes=[];new_routes=[];pdfs=[]
    with local_server(root) as base:
        for route in cfg['guide']:
            code,ct,raw=fetch(base,route)
            require(code==200 and 'html' in ct.lower(),f'new route not HTML 200: {route}')
            html=raw.decode('utf-8')
            p=Page();p.feed(html)
            expected=cfg['origin']+route
            require(p.canonical==[expected],f'canonical incorrect at {route}: {p.canonical}')
            require(p.og_url==[expected],f'OG URL incorrect at {route}: {p.og_url}')
            require(len(p.robots)==1 and p.robots[0].replace(' ','').lower()=='index,follow',
                    'robots not index,follow at '+route)
            require(p.h1==1 and len(p.title.strip())>10 and p.lang.lower().startswith('tr'),
                    'missing H1/title/lang at '+route)
            require(len(p.description)==1 and len(p.description[0])>=25,
                    'missing description at '+route)
            require(cfg['other'] not in html, 'cross-project identity at '+route)
            for token in ('PORTFOLIO_AUTOSYNC_PREVIEW_START','portfoy-guncel','source-status.json',
                          'Resmî portföyden güncel bilgiler (test)'):
                require(token not in html,'preview data in '+route)
            for href in p.styles:
                if href.startswith('/rehber/'):
                    c,t,b=fetch(base,href)
                    require(c==200 and b,'broken HugoBlox CSS '+href)
            new_routes.append({'path':route,'status':code,'canonical':expected})
        for route in cfg['legacy']:
            code,ct,raw=fetch(base,route)
            require(code==200 and 'html' in ct.lower() and len(raw)>200,
                    'critical prior HTML route failed '+route)
            old_routes.append({'path':route,'status':code})
        if project=='DURU':
            locales=sorted((root/'comp-card').glob('*/index.html'))
            require(len(locales)==26,'Duru 26 locale HTML files missing')
            for f in locales:
                route='/comp-card/'+f.parent.name+'/'
                code,ct,raw=fetch(base,route)
                require(code==200 and 'html' in ct.lower() and len(raw)>200,
                        'Duru locale HTTP failed '+route)
                if route not in cfg['legacy']:
                    old_routes.append({'path':route,'status':code})
        pdf_candidates=sorted((root/cfg['pdf_base']).rglob('*.pdf'))
        if project=='SERDAR':
            pdf_candidates=[root/'downloads'/f'Serdar-Armin-Sargut-Comp-Card-{lang}.pdf'
                            for lang in ('TR','EN','AR','RU')]
        require(len(pdf_candidates)==cfg['pdf_count'], 'wrong Comp Card PDF count')
        for pdf in pdf_candidates:
            require(pdf.is_file(),'missing PDF '+str(pdf))
            route='/'+pdf.relative_to(root).as_posix()
            code,ct,raw=fetch(base,route)
            require(code==200 and raw.startswith(b'%PDF-') and len(raw)>1000,
                    'PDF HTTP/signature failed '+route)
            require('pdf' in ct.lower(), 'PDF content type incorrect '+route)
            pdfs.append({'path':route,'status':code,'bytes':len(raw)})
        code,ct,raw=fetch(base,'/robots.txt')
        require(code==200 and b'Disallow: /' not in raw,'production robots globally disallowed')
        require(cfg['origin'].encode() in raw,'robots sitemap domain missing')
        code,ct,raw=fetch(base,'/sitemap.xml')
        require(code==200,'sitemap HTTP failed')
        tree=ET.fromstring(raw)
        ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls=[n.text for n in tree.findall('s:url/s:loc',ns)]
        require(len(urls)==cfg['sitemap'] and len(set(urls))==len(urls),'sitemap count/dupes')
        require(all(cfg['origin']+r in urls for r in cfg['guide']),'new guides absent from sitemap')
        if project=='SERDAR':
            c,t,data=fetch(base,'/sitemap-google.xml')
            g=ET.fromstring(data)
            gu=[n.text for n in g.findall('s:url/s:loc',ns)]
            require(c==200 and gu==urls,'Serdar Google sitemap list mismatch')
    report={'project':project,'status':'LOCAL_PRODUCTION_MIRROR_HTTP_ACCEPTANCE_PASS',
            'production_published':False,'published_by_this_script':False,
            'server_binding':'127.0.0.1 only','new_guide_http_200':len(new_routes),
            'critical_existing_html_http_200':len(old_routes),
            'comp_card_pdf_http_200':len(pdfs),'sitemap_urls':len(urls),
            'new_routes':new_routes,'legacy_routes':old_routes,'pdf_routes':pdfs}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(project+'_LOCAL_PRODUCTION_MIRROR_HTTP_ACCEPTANCE_PASS: '
          +str(len(new_routes))+' new, '+str(len(old_routes))+' legacy, '
          +str(len(pdfs))+' PDF, '+str(len(urls))+' sitemap; NO DEPLOY')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--project',choices=CONFIG,required=True)
    parser.add_argument('--static-root',type=Path,required=True)
    parser.add_argument('--output-json',type=Path,required=True)
    args=parser.parse_args()
    run(args.project,args.static_root,args.output_json)