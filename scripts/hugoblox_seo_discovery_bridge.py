#!/usr/bin/env python3
"""Add ONE transparent, accessible indexable homepage link to verified HugoBlox guide.

Only in fresh isolated OUTPUT ROOT. No Git, Cloudflare, DNS or production write.
The only permitted original file modification is index.html. All other bytes
(including 26/26 Duru locale HTML+PDF and 4 Serdar PDFs) remain unchanged.
"""
import argparse
import hashlib
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
from functools import partial
from threading import Thread
from urllib.request import urlopen
from xml.etree import ElementTree as ET

NS='{http://www.sitemaps.org/schemas/sitemap/0.9}'
CONFIG={
    'SERDAR': {
        'origin':'https://serdararminsargut.com', 'urls':95,
        'anchor':'<a href="/rehber/" style="display:inline-flex;align-items:center;min-height:44px">Çocuk giyim ve casting rehberleri</a>',
        'needle':'<a href="/rehber/korfez-cocuk-model-portfoyu/">Körfez portföy rehberi</a></div></footer>',
        'replacement':'<a href="/rehber/korfez-cocuk-model-portfoyu/">Körfez portföy rehberi</a> · <a href="/rehber/" style="display:inline-flex;align-items:center;min-height:44px">Çocuk giyim ve casting rehberleri</a></div></footer>',
        'protected': ['casting-card/tr.html','downloads/Serdar-Armin-Sargut-Comp-Card-TR.pdf','downloads/Serdar-Armin-Sargut-Comp-Card-EN.pdf','downloads/Serdar-Armin-Sargut-Comp-Card-AR.pdf','downloads/Serdar-Armin-Sargut-Comp-Card-RU.pdf'],
    },
    'DURU': {
        'origin':'https://durumuallasargut.com', 'urls':36,
        'anchor':'<a class="text-link" href="/rehber/" style="display:inline-flex;align-items:center;min-height:44px">Oyunculuk ve casting rehberleri</a>',
        'needle':'<span>DURU MUALLA SARGUT</span>\n      <span>RESMÎ PORTFÖY</span>',
        'replacement':'<span>DURU MUALLA SARGUT</span>\n      <a class="text-link" href="/rehber/" style="display:inline-flex;align-items:center;min-height:44px">Oyunculuk ve casting rehberleri</a>\n      <span>RESMÎ PORTFÖY</span>',
        'protected':['comp-card/tr/index.html','comp-card/ur/index.html','comp-card/ko/index.html'],
    },
}


def require(cond, msg):
    if not cond:raise AssertionError('NO_GO: '+msg)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digests(root):
    return {str(p.relative_to(root)):digest(p) for p in root.rglob('*') if p.is_file()}


class Parsed(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[];self.h1=0;self.title=0;self.canon=[];self.in_footer=False;self.seen_footer=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='footer':self.in_footer=True;self.seen_footer=True
        if tag=='a':self.links.append((a.get('href',''),self.in_footer))
        if tag=='h1':self.h1+=1
        if tag=='title':self.title+=1
        if tag=='link' and 'canonical' in a.get('rel','').split():self.canon.append(a.get('href'))
    def handle_endtag(self,tag):
        if tag=='footer':self.in_footer=False


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*_):pass


def local_http_check(root):
    h=partial(QuietHandler,directory=str(root))
    server=ThreadingHTTPServer(('127.0.0.1',0),h)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        for route in ('/','/rehber/'):
            with urlopen('http://127.0.0.1:'+str(server.server_port)+route,timeout=4) as response:
                require(response.status==200,'local route not HTTP 200: '+route)
                require(b'<html' in response.read().lower(),'local route invalid HTML: '+route)
    finally:
        server.shutdown();server.server_close();thread.join(timeout=3)


def main(project, source, output, receipt):
    project=project.upper();require(project in CONFIG,'wrong project')
    c=CONFIG[project]
    source,output,receipt=(Path(v).resolve() for v in (source,output,receipt))
    require(source.is_dir(),'input root missing')
    require(not output.exists(),'output directory already exists')
    require(output!=source and source not in output.parents and output not in source.parents,'overlapping paths')
    require(not any(x.is_symlink() for x in source.rglob('*')),'symlink present')
    require(receipt!=source and receipt not in source.parents and receipt not in output.parents,'receipt must not be inside the input or output root')
    original=digests(source)
    require('index.html' in original,'homepage missing')
    require((source/'rehber/index.html').is_file(),'guide destination missing')
    require(all((source/p).is_file() for p in c['protected']),'protected HTML/PDF missing')
    sitemap=ET.parse(source/'sitemap.xml').getroot()
    urls=[x.text.strip() for x in sitemap.findall(NS+'url/'+NS+'loc')]
    require(len(urls)==len(set(urls))==c['urls'],'sitemap count/uniqueness mismatch')
    require(c['origin']+'/rehber/' in urls,'guide not in sitemap')
    before=(source/'index.html').read_text(encoding='utf-8')
    require(before.count(c['needle'])==1,'expected unique homepage footer anchor missing')
    require('href="/rehber/"' not in before,'homepage already contains new guide link')
    before_parser=Parsed();before_parser.feed(before)
    require(before_parser.h1==1 and before_parser.title==1,'homepage title/H1 invalid')
    require(before_parser.seen_footer,'no footer')
    require(before_parser.canon==[c['origin']+'/'],'homepage canonical unexpected')
    require('noindex' not in before.lower().split('</head>',1)[0],'production homepage appears noindex')
    after=before.replace(c['needle'],c['replacement'],1)
    require(after.count(c['anchor'])==1,'new visible anchor missing or repeated')
    after_parser=Parsed();after_parser.feed(after)
    require(after_parser.h1==before_parser.h1 and after_parser.title==before_parser.title,'homepage heading or title changed')
    require(after_parser.canon==before_parser.canon,'homepage canonical changed')
    require(after_parser.links.count(('/rehber/',True))==1,'guide must have a genuine footer href')
    require(after.replace(c['replacement'],c['needle'],1)==before,'homepage change exceeds approved single footer link')
    shutil.copytree(source,output,symlinks=False)
    (output/'index.html').write_text(after,encoding='utf-8')
    later=digests(output)
    require(set(later)==set(original),'new/missing static file')
    changes=[p for p in original if original[p]!=later[p]]
    require(changes==['index.html'],'only existing homepage HTML may change: '+repr(changes))
    local_http_check(output)
    require(digest(source/'sitemap.xml')==digest(output/'sitemap.xml'),'sitemap changed')
    require(digest(source/'rehber/index.html')==digest(output/'rehber/index.html'),'guide changed')
    receipt.parent.mkdir(parents=True,exist_ok=True)
    report={'status':'SEO_DISCOVERY_BRIDGE_STAGING_ONLY_PASS','project':project,
            'production_published':False,'production_publish_authorized':False,
            'changed_original_files':changes,'preserved_original_files':len(original)-1,
            'original_file_count':len(original),'new_file_count':len(later),'sitemap_urls':len(urls),
            'added_link_target':'/rehber/','added_link_anchor_text':c['anchor'].split('>')[1].split('<')[0],
            'source_homepage_sha256':original['index.html'],'preview_homepage_sha256':later['index.html'],
            'source_filetree_sha256':hashlib.sha256(json.dumps(original,sort_keys=True).encode()).hexdigest(),
            'candidate_filetree_sha256':hashlib.sha256(json.dumps(later,sort_keys=True).encode()).hexdigest(),
            'local_http_200_paths':['/','/rehber/'],
            'production_site_untouched':True}
    receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(project+'_SEO_DISCOVERY_BRIDGE_STAGING_ONLY_PASS: '+str(len(original)-1)+' old bytes preserved; only index.html gains visible /rehber/ link; NO DEPLOY')
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--project',choices=CONFIG,required=True)
    ap.add_argument('--source-root',type=Path,required=True)
    ap.add_argument('--output-root',type=Path,required=True)
    ap.add_argument('--receipt',type=Path,required=True)
    args=ap.parse_args()
    main(args.project,args.source_root,args.output_root,args.receipt)