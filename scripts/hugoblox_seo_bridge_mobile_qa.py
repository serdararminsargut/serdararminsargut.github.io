#!/usr/bin/env python3
"""Local Playwright footer discovery link acceptance on isolated static candidate.

Runs only loopback 127.0.0.1. Validates visible 44px touch target and navigation
on 360/390/430px mobile and 1280px desktop. No network to public websites.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_):pass

def run(root, outdir, project):
    outdir.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    origin='http://127.0.0.1:'+str(server.server_port)
    results=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
            try:
                for width in (360,390,430,1280):
                    page=browser.new_page(viewport={'width':width,'height':840},device_scale_factor=1)
                    try:
                        page.goto(origin+'/',wait_until='domcontentloaded',timeout=20000)
                        a=page.locator('footer a[href="/rehber/"]')
                        assert a.count()==1, f'{width}: link missing/duplicate'
                        a.scroll_into_view_if_needed(timeout=10000)
                        assert a.is_visible(),f'{width}: link not visible'
                        box=a.bounding_box()
                        assert box and box['height']>=43, f'{width}: small tap target {box}'
                        measure=page.evaluate('''() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,
                            h1:document.querySelectorAll('h1').length, robots:document.querySelector('meta[name=robots]')?.content||''})''')
                        assert measure['h1']==1,f'{width}: H1 changed'
                        assert measure['scroll'] <= measure['width']+2, f'{width}: horizontal overflow: {measure}'
                        page.screenshot(path=str(outdir/f'{project.lower()}-footer-{width}px.png'),full_page=False)
                        a.click(timeout=15000)
                        page.wait_for_url(origin+'/rehber/',timeout=15000)
                        assert page.locator('h1').count()==1,f'{width}: guide H1 absent'
                        results.append({'width':width,'result':'PASS','link_height':round(box['height'],2),
                                        'horizontal_overflow':False,'destination':'/rehber/','h1':1})
                    finally:page.close()
            finally:browser.close()
    finally:
        server.shutdown();server.server_close();thread.join(timeout=4)
    r={'project':project,'status':'SEO_DISCOVERY_MOBILE_QA_PASS','production_published':False,'results':results}
    (outdir/f'{project.lower()}-seo-mobile-qa.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
    print(project+'_SEO_DISCOVERY_MOBILE_QA_PASS: '+str(len(results))+' widths, links clickable, no horizontal overflow; NO DEPLOY')
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--project',choices=['SERDAR','DURU'],required=True)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args();run(a.root,a.output_dir,a.project)