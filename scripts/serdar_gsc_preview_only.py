#!/usr/bin/env python3
"""Serdar GSC preview: noindex, analytics-disabled, isolated branch only."""
import os,json,re,shutil,subprocess,sys
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
EVIDENCE=ROOT/"gsc-preview-evidence"
BRANCH="refs/heads/test/serdar-gsc-index-20261017"
TAG='<script src="/assets/js/gsc-preview-suppress.js"></script>'
TARGETS={
 "/": ("https://serdararminsargut.com/",["/links/","/rehber/korfez-cocuk-model-portfoyu/"]),
 "/links/": ("https://serdararminsargut.com/links/",["/links/en/","/links/ar/","/links/ru/"]),
 "/links/ru": ("https://serdararminsargut.com/links/ru/",[]),
 "/links/ru/": ("https://serdararminsargut.com/links/ru/",[]),
 "/rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/":(
  "https://serdararminsargut.com/rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/",
  ["/tk/oglan-caga-modeli/","/uz/bolalar-kiyim-modeli/"]),
 "/tk/oglan-caga-modeli/":("https://serdararminsargut.com/tk/oglan-caga-modeli/",
  ["/tk/caga-geyim-modeli/","/tk/caga-sport-geyim-modeli/","/tk/elektron-sowda-caga-modeli/"]),
 "/uz/bolalar-kiyim-modeli/":("https://serdararminsargut.com/uz/bolalar-kiyim-modeli/",[])
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
 (DIST/"assets/js/gsc-preview-suppress.js").write_text(
  'window["ga-disable-G-H894LKL93J"]=true;\n'
  'window.__serdarGscPreviewNoCollection=true;\n',encoding="utf-8")
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
 print("SERDAR_GSC_PREVIEW_BUNDLE_PASS "+json.dumps(proof))
def verify():
 from playwright.sync_api import sync_playwright
 url=os.environ["PREVIEW_URL"].rstrip("/")
 u=urlparse(url)
 assert u.scheme=="https" and u.hostname and u.hostname.endswith(".serdararminsargut.pages.dev")
 assert u.hostname!="serdararminsargut.pages.dev" and u.path in ("","/")
 results=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  try:
   for route,(canonical,links) in TARGETS.items():
    ctx=browser.new_context()
    page=ctx.new_page()
    egress=[]
    def block(req):
     egress.append(req.request.url)
     req.abort()
    page.route(re.compile(r"https?://([^/]*\.)?(google-analytics\.com|analytics\.google\.com)/.*"),block)
    # Suppress the Google Tag loader separately from GA4 collection attempts.
    # A blocked loader is not a page_view or an outbound measurement event.
    def suppress_loader(req):
     req.abort()
    page.route("https://www.googletagmanager.com/gtag/js**",suppress_loader)
    response=page.goto(url+route,wait_until="domcontentloaded",timeout=25000)
    assert response is not None and response.status==200,(route,"HTTP")
    assert "noindex" in response.headers.get("x-robots-tag","").lower(),(route,"noindex")
    assert "connect-src 'self';" in response.headers.get("content-security-policy",""),(route,"CSP")
    page.wait_for_function("window.__serdarGscPreviewNoCollection === true")
    got=page.locator('head link[rel="canonical"]').first.get_attribute("href")
    assert got==canonical,(route,"canonical",got)
    for link in links:
     assert page.locator("a[href='"+link+"']").count()>=1,(route,link)
    assert not egress,(route,"Analytics requests attempted",egress)
    results.append({"route":route,"canonical":got,"http":200,"noindex":True,"linked":links})
    ctx.close()
  finally:browser.close()
 t=subprocess.run(["curl","-fsS","--connect-timeout","10","--max-time","20",
                   url+"/robots.txt"],capture_output=True,text=True)
 assert t.returncode==0 and "Disallow: /" in t.stdout,"robots"
 EVIDENCE.mkdir(exist_ok=True)
 (EVIDENCE/"remote.json").write_text(json.dumps({"status":"PASS","pages":results,
   "GA4EventsSent":0,"production":"NO_GO"},indent=2),encoding="utf-8")
 print("SERDAR_GSC_PREVIEW_BROWSER_PASS 7/7 noindex=PASS analytics=BLOCKED")
if __name__=="__main__":
 assert len(sys.argv)==2 and sys.argv[1] in ("build","verify")
 {"build":build,"verify":verify}[sys.argv[1]]()
