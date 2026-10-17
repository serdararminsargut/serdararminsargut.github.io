#!/usr/bin/env python3
"""Production READ-ONLY HTTP/Chromium proof. Never send test events to GA4."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"postrelease-evidence"
BASE="https://serdararminsargut.com"
JS="/assets/js/ga4-untracked-pages.js"
TAG='<script defer src="/assets/js/ga4-untracked-pages.js"></script>'
COVERED=[
  "blog/cocuk-model-portfoyu/index.html",
  "blog/cocuk-oyuncu-comp-card/index.html",
  "blog/cocuk-oyuncu-showreel/index.html",
  "blog/erkek-cocuk-urun-modeli/index.html",
  "blog/istanbul-cocuk-oyuncu-casting/index.html",
  "blog/kidswear-cocuk-model-katalog/index.html",
  "blog/reklam-filmi-erkek-cocuk-oyuncu/index.html",
  "casting-card/tr.html",
  "casting-card/en.html",
  "casting-card/ar.html",
  "casting-card/ru.html",
  "de/ecommerce-kinder-model/index.html",
  "de/jungen-model/index.html",
  "de/kinder-sportmode-model/index.html",
  "de/kindermode-model/index.html",
  "en/boy-model/index.html",
  "en/ecommerce-child-model/index.html",
  "en/gulf-child-model-portfolio/index.html",
  "en/kids-sportswear-model/index.html",
  "en/kidswear-model/index.html",
  "ar/dalil-malaf-model-atfal-al-khalij/index.html",
  "ar/model-atfal-malabis-riyadiya/index.html",
  "ar/model-atfal-malabis/index.html",
  "ar/model-atfal-tijara-elektroniya/index.html",
  "ar/model-walad/index.html",
  "ru/detskaya-sportivnaya-model/index.html",
  "ru/model-detskoy-odezhdy/index.html",
  "ru/model-dlya-internet-magazina/index.html",
  "ru/model-malchik/index.html",
  "erkek-cocuk-model/index.html",
  "e-ticaret-cocuk-modeli/index.html",
  "spor-giyim-cocuk-modeli/index.html",
  "cocuk-giyim-modeli/index.html"
]
BRANCH="refs/heads/test/serdar-ga4-postrelease-proof-20261017"
PROD_SHA="b8bfdedfd697210aaedf23e4d140dc8c3343b401"
USER_AGENT="Mozilla/5.0 (compatible; SerdarPortfolioVerification/1.0; +https://serdararminsargut.com/)"

def fail_if(cond, explanation):
    if cond: raise AssertionError(explanation)

def url_of(path):
    return BASE + ("/" + path[:-11] if path.endswith("/index.html") else "/" + path[:-5]) + ("/" if path.endswith("/index.html") else "")

def fetch(url):
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        head=Path(directory)/"header"; body=Path(directory)/"body"
        cmd=["curl","--silent","--show-error","--location","--max-redirs","3",
             "--retry","1","--retry-delay","2","--connect-timeout","10","--max-time","35",
             "--user-agent",USER_AGENT,"--dump-header",str(head),"--output",str(body),
             "--write-out","%{http_code}\n%{url_effective}",url]
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if p.returncode!=0:
            raise AssertionError(f"HTTP fetch failed {url}: {p.stderr[-280:]}")
        lines=p.stdout.strip().splitlines()
        assert len(lines)==2, (url,p.stdout)
        status=int(lines[0]); final=lines[1]
        headers=head.read_text(errors="replace").split("\r\n\r\n")[-1].lower()
        if not headers: headers=head.read_text(errors="replace").lower()
        return status,final,headers,body.read_bytes()

def http_proof():
    assert os.environ.get("GITHUB_REF")==BRANCH, "Wrong branch, production proof must be read-only"
    assert len(COVERED)==33 and len(set(COVERED))==33
    OUT.mkdir(exist_ok=True)
    proof=[]
    for path in COVERED:
        url=url_of(path)
        status,final,h,b=fetch(url)
        if status!=200: raise AssertionError(f"{url}: HTTP {status}")
        if urlparse(final).hostname!="serdararminsargut.com":
            raise AssertionError(f"Unexpected redirect target {url}: {final}")
        if b.count(TAG.encode("utf-8"))!=1:
            raise AssertionError(f"GA4 marker missing or duplicated {url}: {b.count(TAG.encode('utf-8'))}")
        if b"G-H894LKL93J" in b or b"googletagmanager.com/gtag/js" in b:
            raise AssertionError(f"Legacy competing inline tag in {url}")
        if "x-robots-tag: noindex" in h:
            raise AssertionError(f"Production incorrectly noindex: {url}")
        proof.append({"url":url,"code":status,"ga4ScriptMarkers":1})
    status,final,h,js=fetch(BASE+JS)
    if status!=200: raise AssertionError(f"Missing GA4 asset: {status}")
    expected=(ROOT/"assets/js/ga4-untracked-pages.js").read_bytes()
    assert hashlib.sha256(js).digest()==hashlib.sha256(expected).digest(), "GA4 live script differs from published source"
    assert js.count(b"w.gtag('config', measurementId)")==1, "GA4 config not unique"
    assert b"ga-disable-G-H894LKL93J" not in js, "Production has preview tracking suppression"
    root_code,_,root_headers,root=fetch(BASE+"/")
    assert root_code==200 and TAG.encode() not in root, "Existing homepage GA4 must remain unchanged"
    assert "x-robots-tag: noindex" not in root_headers, "Homepage is noindex"
    result={"kind":"Serdar production HTTP read-only","status":"PASS",
            "productionSource":PROD_SHA,"testEventsSent":False,
            "pages":len(proof),"scriptMatchesPublishedSourceSHA256":True,"routes":proof}
    (OUT/"http.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("SERDAR_GA4_LIVE_HTTP_PASS 33/33 script_sha256=PASS homepage_unchanged=PASS")

def browser_proof():
    from playwright.sync_api import sync_playwright
    samples=["blog/erkek-cocuk-urun-modeli/index.html",
             "blog/istanbul-cocuk-oyuncu-casting/index.html",
             "casting-card/en.html",
             "de/kinder-sportmode-model/index.html",
             "en/boy-model/index.html",
             "ar/model-walad/index.html",
             "ru/model-malchik/index.html"]
    assert len(samples)==7 and all(x in COVERED for x in samples)
    records=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            for path in samples:
                ctx=browser.new_context(user_agent=USER_AGENT)
                page=ctx.new_page()
                loaders=[]; analytics_egress=[]
                def no_analytics(r):
                    analytics_egress.append(r.request.url)
                    r.abort()
                def fake_gtag(r):
                    loaders.append(r.request.url)
                    r.fulfill(status=200,content_type="application/javascript",
                              body="window.__sasMockGoogleTag=true;")
                # Installed BEFORE opening the live site. Never send GA4 or Tag requests.
                page.route(re.compile(r"https?://([^/]*\.)?(google-analytics\.com|analytics\.google\.com)/.*"),no_analytics)
                page.route("https://www.googletagmanager.com/gtag/js**",fake_gtag)
                response=page.goto(url_of(path),wait_until="domcontentloaded",timeout=35000)
                assert response is not None and response.status==200, (path,response.status if response else None)
                page.wait_for_function("window.__sasGa4PageviewOnce === true",timeout=15000)
                states=page.evaluate("""() => ({
                    config: Array.from(window.dataLayer||[]).filter(x=>x[0]==='config' && x[1]==='G-H894LKL93J').length,
                    js: Array.from(window.dataLayer||[]).filter(x=>x[0]==='js').length,
                    tag: document.querySelectorAll('script[data-sas-ga4-untracked]').length,
                    previewGuard: window.__serdarGa4PreviewOnly===true || window['ga-disable-G-H894LKL93J']===true
                })""")
                assert states=={"config":1,"js":1,"tag":1,"previewGuard":False},(path,states)
                assert len(loaders)==1,(path,loaders)
                assert analytics_egress==[],(path,analytics_egress)
                # Live site browser interaction is READ ONLY: no clicks, no submits.
                records.append({"path":path,"http":200,"configs":1,"gaLoaderIntercepted":1,"gaEventsSent":0})
                ctx.close()
        finally:
            browser.close()
    (OUT/"browser.json").write_text(json.dumps({
      "kind":"Serdar live browser read-only", "status":"PASS","testEventsSent":False,"routes":records,
      "googleTag":"intercepted before any browser request", "measurementDelivery":"NOT_VERIFIED"},
      indent=2)+"\n",encoding="utf-8")
    print("SERDAR_GA4_LIVE_CHROMIUM_PASS 7/7, duplicate_config=0, test_events_sent=0")

if __name__=="__main__":
    import sys
    assert len(sys.argv)==2 and sys.argv[1] in ("http","browser")
    {"http":http_proof,"browser":browser_proof}[sys.argv[1]]()
