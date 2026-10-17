#!/usr/bin/env python3
"""Serdar GSC preview: noindex, analytics-disabled, isolated branch only."""
import os,json,re,shutil,subprocess,sys
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
EVIDENCE=ROOT/"yandex-pilot-preview-evidence"
BRANCH="refs/heads/test/serdar-yandex-quality-pilot-20261017"
TAG='<script src="/assets/js/yandex-pilot-preview-suppress.js"></script>'
TARGETS={
 "/ru/model-detskoy-odezhdy/":("https://serdararminsargut.com/ru/model-detskoy-odezhdy/",["/casting-card/ru","/ru/model-malchik/"]),
 "/ky/balalar-kiim-modeli/":("https://serdararminsargut.com/ky/balalar-kiim-modeli/",["/casting-card/en","/ky/ul-bala-modeli/"])
}

def build():
 assert os.environ.get("GITHUB_REF")==BRANCH,"NO-GO wrong branch"
 if DIST.exists():shutil.rmtree(DIST)
 DIST.mkdir();EVIDENCE.mkdir(exist_ok=True)
 dirs=("assets","ar","az","blog","casting-card","de","downloads","en",
       "fa","fr","it","kk","ky","links","projeler","rehber","ru","tk","uz",
       "zh-cn","erkek-cocuk-model","spor-giyim-cocuk-modeli",
       "cocuk-giyim-modeli","e-ticaret-cocuk-modeli")
 files=("_headers","_redirects","404.html","index.html","robots.txt",
        "sitemap.xml","sitemap-google.xml","sitemap.txt","favicon.svg",
        "favicon.ico","favicon-96x96.png",".nojekyll","ai.txt","llms.txt",
        "llms-full.txt","indexnow-key.txt","card.html","postcard.html")
 for d in dirs:
  if (ROOT/d).is_dir():shutil.copytree(ROOT/d,DIST/d)
 for f in files:
  if (ROOT/f).is_file():shutil.copy2(ROOT/f,DIST/f)
 for f in ROOT.glob("yandex_*.html"):shutil.copy2(f,DIST/f.name)
 (DIST/"assets/js/yandex-pilot-preview-suppress.js").write_text(
  'window["ga-disable-G-H894LKL93J"]=true;\n'
  'window.__serdarYandexPilotNoCollection=true;\n',encoding="utf-8")
 count=0
 for f in DIST.rglob("*.html"):
  html=f.read_text(encoding="utf-8")
  m=re.search(r"<head\b[^>]*>",html,re.I)
  if not m:continue
  assert TAG not in html
  f.write_text(html[:m.end()]+TAG+html[m.end():],encoding="utf-8")
  count+=1
 assert count>=95,("Missing guarded HTML files",count)
 h=DIST/"_headers"
 orig=h.read_text(encoding="utf-8")
 assert orig.startswith("/*\n")
 s=orig.replace("/*\n","/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n",1)
 s,n=re.subn(r"connect-src [^;]+;","connect-src 'self';",s,count=1)
 assert n==1
 h.write_text(s,encoding="utf-8")
 (DIST/"robots.txt").write_text("User-agent: *\nDisallow: /\n",encoding="utf-8")
 assert (ROOT/"_headers").read_text()==orig
 proof={"build":"PASS","guardedPages":count,"scope":"TEST_PREVIEW","noindex":True,
        "analyticsCollectionDisabled":True,"production":"NO_GO"}
 (EVIDENCE/"bundle.json").write_text(json.dumps(proof,indent=2))
 print("SERDAR_YANDEX_PILOT_PREVIEW_BUNDLE_PASS "+json.dumps(proof))
def verify():
 from playwright.sync_api import sync_playwright
 url=os.environ["PREVIEW_URL"].rstrip("/")
 u=urlparse(url)
 assert u.scheme=="https" and u.hostname and u.hostname.endswith(".serdararminsargut.pages.dev")
 assert u.hostname!="serdararminsargut.pages.dev" and u.path in ("","/")
 results=[]
 EVIDENCE.mkdir(exist_ok=True)
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  try:
   for route,(canonical,links) in TARGETS.items():
    for width in (360,390,768,1280):
     ctx=browser.new_context(viewport={"width":width,"height":860})
     page=ctx.new_page()
     egress=[]
     def block(req):
      egress.append(req.request.url)
      req.abort()
     page.route(re.compile(r"https?://([^/]*\.)?(google-analytics\.com|analytics\.google\.com)/.*"),block)
     page.route("https://www.googletagmanager.com/gtag/js**",lambda req:req.abort())
     response=page.goto(url+route,wait_until="domcontentloaded",timeout=30000)
     assert response and response.status==200,(route,width,"http")
     assert "noindex" in response.headers.get("x-robots-tag","").lower(),(route,width,"noindex")
     assert "connect-src 'self';" in response.headers.get("content-security-policy",""),(route,width,"CSP")
     assert page.locator('script[src="/assets/js/yandex-pilot-preview-suppress.js"]').count()==1,(route,width,"suppress script")
     assert page.evaluate("Boolean(window.__serdarYandexPilotNoCollection)"),(route,width,"analytics suppress")
     got=page.locator('head link[rel="canonical"]').first.get_attribute("href")
     assert got==canonical,(route,width,"canonical",got)
     assert page.locator('head meta[name="robots"]').get_attribute("content").startswith("index,follow")
     for link in links:
      assert page.locator('a[href="'+link+'"]').count()>0,(route,width,link)
     images=page.locator('section img[src^="/assets/photos/"]')
     assert images.count()==3,(route,width,"image_count",images.count())
     page.wait_for_load_state("networkidle",timeout=30000)
     status=images.evaluate_all("(imgs)=>imgs.map(i=>({ready:i.complete,width:i.naturalWidth}))")
     assert all(x["ready"] and x["width"]>0 for x in status),(route,width,"image_load",status)
     dims=page.evaluate("({w:innerWidth,scroll:document.documentElement.scrollWidth,cols:getComputedStyle(document.querySelector('section .image-grid,section .portfolio-photo-grid')).gridTemplateColumns.split(' ').length})")
     assert dims["scroll"]<=dims["w"]+1,(route,width,"overflow",dims)
     assert dims["cols"]==(2 if width<=390 else 3),(route,width,"columns",dims)
     assert not egress,(route,width,"GA egress",egress)
     imageName=("ru" if route.startswith("/ru/") else "ky")+"-"+str(width)
     page.screenshot(path=str(EVIDENCE/(imageName+".png")),full_page=True)
     results.append({"route":route,"width":width,"noindex":True,"canonical":got,"images":3,"columns":dims["cols"],"overflow":False,"GA4EventsSent":0})
     ctx.close()
  finally: browser.close()
 t=subprocess.run(["curl","-fsS","--connect-timeout","10","--max-time","20",url+"/robots.txt"],capture_output=True,text=True)
 assert t.returncode==0 and "Disallow: /" in t.stdout
 (EVIDENCE/"remote.json").write_text(json.dumps({"status":"PASS","pages":results,"GA4EventsSent":0,"production":"NO_GO"},indent=2),encoding="utf-8")
 print("SERDAR_YANDEX_PILOT_PREVIEW_BROWSER_PASS 8/8 noindex=PASS analytics=BLOCKED")
if __name__=="__main__":
 assert len(sys.argv)==2 and sys.argv[1] in ("build","verify")
 {"build":build,"verify":verify}[sys.argv[1]]()
