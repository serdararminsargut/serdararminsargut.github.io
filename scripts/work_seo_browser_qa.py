"""Chromium QA of an isolated localhost Pages build, never of production."""
import argparse,json,time,hashlib
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--project',choices=['serdar','duru'],required=True);p.add_argument('--root',required=True);p.add_argument('--base',default='http://127.0.0.1:8788');a=p.parse_args()
assert urlsplit(a.base).hostname in ('127.0.0.1','localhost'),'Local QA only'
r=Path(a.root);out=Path('work-evidence');shots=out/'screenshots';shots.mkdir(parents=True,exist_ok=True)
routes=[urlsplit(x.text).path for x in ET.parse(r/'sitemap.xml').getroot().iter() if x.tag.endswith('}loc')]
cards=[u for u in routes if u.startswith('/casting-card/' if a.project=='serdar' else '/comp-card/')]
assert len(cards)==26
main=['/','/links/en/','/casting-card/tr','/casting-card/en','/casting-card/ar','/casting-card/fa','/casting-card/ur','/ar/','/ky/','/en/'] if a.project=='serdar' else ['/','/links/','/comp-card/tr/','/comp-card/en/','/comp-card/ar/','/comp-card/fa/','/comp-card/ur/']
main=[u for u in main if u in routes]
cases=[(u,w) for u in main for w in (360,390,430,1280)]+[(u,390) for u in cards if u not in main]
if a.project=='serdar':cases +=[(u,390) for u in ('/ru/','/az/','/kk/','/uz/','/tk/caga-geyim-modeli/','/de/ecommerce-kinder-model/','/rehber/post/') if u in routes]
results=[];interactions=[];pdf_results=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,args=['--no-sandbox'])
    for route,width in cases:
        ctx=b.new_context(viewport={'width':width,'height':844},is_mobile=width<600,has_touch=width<600,accept_downloads=True)
        # Prevent synthetic analytics visits; no page content or document responses are mocked.
        ctx.route('**/*',lambda req:req.abort() if any(x in req.request.url for x in ('google-analytics.com','googletagmanager.com','mc.yandex','cloudflareinsights.com')) else req.continue_())
        page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        item={'route':route,'width':width,'environment':'LOCAL_PAGES_CHROMIUM','status':'FAIL'}
        try:
            resp=page.goto(a.base+route,wait_until='load',timeout=30000)
            assert resp and resp.status==200,'HTTP page failure'
            assert 'noindex' in resp.headers.get('x-robots-tag',''),'No local Pages noindex header'
            page.evaluate('document.fonts.ready');page.wait_for_timeout(1200 if route=='/' else 350)
            info=page.evaluate("""() => ({lang:document.documentElement.lang,dir:document.documentElement.dir||'ltr',h1:document.querySelectorAll('h1').length,viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,canonical:document.querySelector('link[rel=canonical]')?.href,images:[...document.images].filter(i=>i.getAttribute('src')).map(i=>({src:i.currentSrc||i.src,complete:i.complete,width:i.naturalWidth,lazy:i.loading==='lazy'})),briefs:[...document.querySelectorAll('a[href*=\"docs.google.com/document/d/\"]')].map(e=>({href:e.href,target:e.target,rel:e.rel})),forms:document.forms.length})""")
            item.update(info);assert info['h1']==1,'H1 count'
            assert info['scrollWidth']<=width+2,'Horizontal overflow'
            assert info['canonical'].startswith('https://'+('serdararminsargut.com' if a.project=='serdar' else 'durumuallasargut.com')),'Canonical origin changed'
            assert not errors,'JavaScript exceptions: '+str(errors)
            if '/casting-card/' in route or '/comp-card/' in route:
                assert len(page.locator('a[hreflang]').all())>=26,'Language menu incomplete'
                if any('/'+lang in route for lang in ('ar','fa','ur')):assert info['dir']=='rtl','RTL missing'
            if route in ('/','/links/en/' if a.project=='serdar' else '/comp-card/tr/'):
                assert len(info['briefs'])==1,'Casting Brief absent or duplicated'
                doc='1rBx2v_8ovMuzS0WQzcoPQwWAMNGIHM9TQLSrZkm80Fs' if a.project=='serdar' else '165dtNSKAEE5SisHuFEMH6xGwlqxS89KrjhU7g8NAOBg'
                assert doc in info['briefs'][0]['href'],'Wrong person document'
                link=page.locator('a[href*="'+doc+'"]');link.scroll_into_view_if_needed()
                hit=link.evaluate("e=>{const r=e.getBoundingClientRect();const h=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return {left:r.x,right:r.right,height:r.height,hit:!!h&&(e===h||e.contains(h))}}")
                assert hit['hit'] and hit['left']>=-1 and hit['right']<=width+1,'Brief obscured or clipped'
                assert info['briefs'][0]['target']=='_blank' and {'noopener','noreferrer'}<=set(info['briefs'][0]['rel'].split()),'Unsafe brief target'
                item['brief_hit_test']=hit
            page.evaluate('window.scrollTo(0,0)')
            name=route.strip('/').replace('/','_').replace('.','_') or 'home'
            shot=name+'-'+str(width)+'.png';page.screenshot(path=str(shots/shot),full_page=route=='/' or '/ar' in route)
            item['screenshot']='screenshots/'+shot;item['status']='PASS'
            if route=='/' and width in (390,1280):
                interaction={'width':width,'menu':'not present','lightbox':'NOT VERIFIED','media':'NOT VERIFIED','audio_audibility':'NOT VERIFIED'}
                menu=page.locator('.menu-toggle')
                if menu.count() and menu.is_visible():
                    menu.click();assert menu.get_attribute('aria-expanded')=='true';menu.click();assert menu.get_attribute('aria-expanded')=='false';interaction['menu']='PASS open and close'
                if a.project=='serdar':
                    btn=page.locator('[data-lightbox]:not([data-instagram-tile])').first
                    btn.click();assert page.locator('.lightbox.open').count()==1
                    page.locator('.lightbox button').click();assert page.locator('.lightbox.open').count()==0;interaction['lightbox']='PASS open and close'
                    page.locator('[data-model-filter="sport"]').click();assert page.locator('[data-model-filter="sport"]').get_attribute('aria-pressed')=='true';page.locator('[data-model-filter="sport"]').click();interaction['filter']='PASS'
                    page.locator('[data-video]').first.click();frame=page.locator('.video-modal iframe');interaction['media']='Vimeo iframe mounted: '+str(frame.get_attribute('src'))
                    page.keyboard.press('Escape')
                    assert page.locator('.video-modal.open').count()==0
                else:
                    btn=page.locator('.gallery-photo-link').first
                    if btn.count():
                        btn.click();assert page.locator('#lightbox').evaluate('e=>e.open');page.locator('.close-dialog').click();assert not page.locator('#lightbox').evaluate('e=>e.open');interaction['lightbox']='PASS open and close'
                    filters=page.locator('[data-filter="editorial"]');filters.click();assert 'is-active' in filters.get_attribute('class');page.locator('[data-filter="all"]').click();interaction['filter']='PASS'
                    video=page.locator('video').first
                    if video.count():
                        video.scroll_into_view_if_needed();video.evaluate('v=>{v.muted=true;return v.play()}');page.wait_for_timeout(800);t=video.evaluate('v=>({time:v.currentTime,paused:v.paused,error:v.error?.code})');interaction['media']=t;assert t['time']>0 and not t['paused'],'Local video failed';video.evaluate('v=>v.pause()')
                page.keyboard.press('Tab');interaction['keyboard_focus']=page.evaluate('({tag:document.activeElement.tagName,outline:getComputedStyle(document.activeElement).outlineStyle})');interactions.append(interaction)
            if width==390 and route in cards:
                link=page.locator('a[href$=".pdf"]').first
                if link.count():
                    href=link.get_attribute('href');u=a.base+urlsplit(href).path if href.startswith('https://') else a.base+urlsplit(__import__('urllib.parse').parse.urljoin(a.base+route,href)).path
                    response=ctx.request.get(u);data=response.body();assert response.status==200 and data.startswith(b'%PDF-'),'PDF invalid'
                    pdf_results.append({'route':route,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'status':'PASS'})
        except Exception as e:item['status']='FAIL';item['error']=str(e);print('CASE_FAILURE',json.dumps(item,ensure_ascii=False),flush=True)
        finally:results.append(item);ctx.close()
    b.close()
report={'project':a.project,'environment':'LOCAL_CLOUDFLARE_PAGES_EMULATION','real_cloudflare_preview':'BLOCKED by Access login; this is not preview acceptance','physical_android':'NOT VERIFIED','cases':results,'interactions':interactions,'pdfs':pdf_results,'total':len(results),'passed':sum(x['status']=='PASS' for x in results)}
(out/'browser-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('LOCAL_BROWSER_QA',report['project'],report['passed'],'/',report['total'],'PDF',len(pdf_results),flush=True)
if report['passed']!=report['total']:raise SystemExit(1)
