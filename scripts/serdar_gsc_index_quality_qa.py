#!/usr/bin/env python3
"""Serdar-only GSC indexing audit: static exact-diff and crawl pathways.
Google indexing is NOT asserted by this script; evidence is limited to local files and live HTTP.
"""
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter,defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

BASE = "b8bfdedfd697210aaedf23e4d140dc8c3343b401"
ROOT = Path(__file__).resolve().parent.parent
TARGETS = [
"/links/", "/links/en/", "/links/ar/", "/links/ru/",
"/rehber/korfez-cocuk-model-portfoyu/",
"/tk/caga-geyim-modeli/", "/tk/caga-sport-geyim-modeli/",
"/tk/elektron-sowda-caga-modeli/", "/uz/bolalar-kiyim-modeli/"
]
PRODUCTION_PROTECTED = ("_redirects", "_headers", "robots.txt", "sitemap.xml",
    ".github/workflows/deploy-cloudflare-pages.yml",
    "links/ru/index.html", "tk/oglan-caga-modeli/index.html",
    "uz/ogil-bola-modeli/index.html")
EXPECTED_CHANGED = {"index.html", "links/ru.html",
  "rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/index.html",
  "scripts/serdar_gsc_index_quality_qa.py",
  ".github/workflows/serdar-gsc-index-test-only.yml"}
ROOT_URL="https://serdararminsargut.com"

def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout

def expect(cond,msg):
    if not cond: raise AssertionError(msg)

class Pages(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs=[]
        self.canonicals=[]
        self.robots=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="a" and d.get("href"): self.hrefs.append(d["href"])
        if tag=="link" and "canonical" in (d.get("rel") or "").lower():
            self.canonicals.append(d.get("href",""))
        if tag=="meta" and (d.get("name") or "").lower()=="robots":
            self.robots.append(d.get("content",""))

def pathname(p):
    if p=="index.html": return "/"
    if p.endswith("/index.html"): return "/"+p[:-11]
    if p.endswith(".html"): return "/"+p[:-5]
    return "/"+p

def static():
    before_main=git("show",f"{BASE}:index.html")
    after_main=(ROOT/"index.html").read_text()
    before_ru=git("show",f"{BASE}:links/ru.html")
    after_ru=(ROOT/"links/ru.html").read_text()
    before_guide=git("show",f"{BASE}:rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/index.html")
    after_guide=(ROOT/"rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/index.html").read_text()
    footer_old='<footer class="footer"><div class="wrap">© 2026 Serdar Armin Sargut • Profesyonel Model, Manken &amp; Oyuncu Portföyü</div></footer>'
    footer_new='<footer class="footer"><div class="wrap">© 2026 Serdar Armin Sargut • Profesyonel Model, Manken &amp; Oyuncu Portföyü · <a href="/links/">Resmî bağlantılar</a> · <a href="/rehber/korfez-cocuk-model-portfoyu/">Körfez portföy rehberi</a></div></footer>'
    expect(before_main.count(footer_old)==1,"unexpected homepage baseline footer")
    expect(after_main==before_main.replace(footer_old,footer_new),"unexpected homepage diff")
    expect(before_ru.count("https://serdararminsargut.com/links/ru")==5,"unexpected RU alias baseline")
    expect(after_ru==(before_ru.replace("https://serdararminsargut.com/links/ru",
        "https://serdararminsargut.com/links/ru/").replace('href="/links/ru"',
        'href="/links/ru/"')),"RU alias diff exceeded canonical normalization")
    before_title="Dört pazar, dört anlaşılır portföy sayfası."
    after_title="Beş pazar, beş anlaşılır portföy girişi."
    uz_old='<a href="/uz/" hreflang="uz">O‘zbek tilidagi portfolio →</a></article>'
    uz_new='<a href="/uz/" hreflang="uz">O‘zbek tilidagi portfolio →</a> · <a href="/uz/bolalar-kiyim-modeli/" hreflang="uz">Bolalar kiyimi modeli →</a></article>'
    ky='<article class="card"><h3>Кыргызстан</h3><p>“бала модель”, “бала актёр Стамбул”, “жарна актёр” жана каталог тартуу үчүн жергиликтүү бет.</p><a href="/ky/" hreflang="ky">Кыргыз тилиндеги портфолио →</a></article>'
    # The exact existing Kyrgyz copy is checked against a stable HTML anchor;
    # no rewritten locale copy is allowed.
    marker='<a href="/ky/" hreflang="ky">Кыргыз тилиндеги портфолио →</a></article>'
    card='<article class="card"><h3>Türkmenistan</h3><p>Çocuk giyim, katalog ve e-ticaret projeleri için Türkmen Türkçesinde hazırlanmış model portföyü.</p><a href="/tk/oglan-caga-modeli/" hreflang="tk">Türkmençe model portföyü →</a></article>'
    expect(before_guide.count(marker)==1 and before_guide.count(before_title)==1
           and before_guide.count(uz_old)==1,"unexpected guide source")
    expected_guide=(before_guide.replace(before_title,after_title)
                    .replace(uz_old,uz_new)
                    .replace(marker,marker+"\n      "+card))
    expect(after_guide==expected_guide,"unexpected guide diff")
    changed=set(git("diff","--name-only",BASE,"HEAD").splitlines())
    expect(changed==EXPECTED_CHANGED,
          f"unexpected file changes: {sorted(changed ^ EXPECTED_CHANGED)}")
    for p in PRODUCTION_PROTECTED:
        expect((ROOT/p).read_bytes()==git("show",f"{BASE}:{p}").encode(),
               f"protected asset changed: {p}")
    # Real hyperlinks (not sitemap entries or hreflang alone).
    graph=defaultdict(set)
    canonical={}
    robots={}
    aliases={}
    for f in ROOT.rglob("*.html"):
        if any(part in (".git","tests","scripts","dist",".github") for part in f.relative_to(ROOT).parts):
            continue
        raw=f.read_text(encoding="utf-8")
        parser=Pages(); parser.feed(raw)
        path=pathname(f.relative_to(ROOT).as_posix())
        aliases[path]=f.relative_to(ROOT).as_posix()
        canonical[path]=parser.canonicals
        robots[path]=parser.robots
        for a in parser.hrefs:
            if a.startswith(ROOT_URL):
                a=a[len(ROOT_URL):]
            if a.startswith("/") and not a.startswith("//"):
                graph[a.split("#")[0].split("?")[0]].add(path)
    index=Pages();index.feed(after_main)
    expect("/links/" in index.hrefs and "/rehber/korfez-cocuk-model-portfoyu/" in index.hrefs,
           "important hubs not directly discoverable from homepage")
    hub=Pages(); hub.feed((ROOT/"links/index.html").read_text())
    for link in ("/links/en/","/links/ar/","/links/ru/"):
        expect(link in hub.hrefs,f"missing hub language link {link}")
    guide=Pages();guide.feed(after_guide)
    expect("/tk/oglan-caga-modeli/" in guide.hrefs,"Turkmen pages inaccessible from regional guide")
    tk=Pages();tk.feed((ROOT/"tk/oglan-caga-modeli/index.html").read_text())
    for url in TARGETS:
        path=url+"index.html"
        # slash canonical pages must exist in the repo:
        expect((ROOT/path.lstrip("/")).is_file(),f"target page missing {url}")
        pg=Pages(); pg.feed((ROOT/path.lstrip("/")).read_text())
        expect(pg.canonicals==[ROOT_URL+url],f"wrong source canonical {url}: {pg.canonicals}")
        expect(not any("noindex" in x.lower() for x in pg.robots), f"unexpected noindex {url}")
    for link in ("/tk/caga-geyim-modeli/","/tk/caga-sport-geyim-modeli/",
                 "/tk/elektron-sowda-caga-modeli/"):
        expect(link in tk.hrefs, f"Turkmen cluster missing link {link}")
    expect("/uz/bolalar-kiyim-modeli/" in guide.hrefs,"Uzbek clothing link absent from guide")
    alias=Pages(); alias.feed(after_ru)
    expect(alias.canonicals==[ROOT_URL+"/links/ru/"], "Russian alias canonical is not sitemap URL")
    expect(any("hreflang" in after_ru for _ in [1]),"RU alias lost hreflang")
    site=ET.fromstring((ROOT/"sitemap.xml").read_text())
    locations={x.text for x in site.findall(".//{*}loc")}
    for url in TARGETS:
        expect(ROOT_URL+url in locations,f"missing sitemap target: {url}")
    evidence={"status":"PASS","scope":"TEST_BRANCH_ONLY","targets":len(TARGETS),
              "originalBaseline":BASE,"rootHubLinks":True,"ruAliasCanonicalUnified":True,
              "turkmenRootLinkedViaRegionalGuide":True,"independentIndexCoverageProven":False,
              "sourcePagesChecked":len(canonical),"urls":[{
                "url":url, "inboundInternalSources":len(graph.get(url,[])),
                "sources":sorted(graph.get(url,[]))[:12]} for url in TARGETS],
              "gscIndexation":"NOT_VERIFIED_BY_GOOGLE","production":"NO_GO"}
    print("SERDAR_GSC_STATIC_PASS "+json.dumps(evidence,ensure_ascii=False))
    (ROOT/"gsc-index-evidence").mkdir(exist_ok=True)
    (ROOT/"gsc-index-evidence/static.json").write_text(
        json.dumps(evidence,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def live():
    # READ ONLY, used to distinguish actual redirects from old GSC error statuses.
    import tempfile
    sites=["/links/ru", "/links/ru/", "/links/", "/links/en/",
           "/links/ar/","/showreel/","/tk/oglan-caga-modeli/"]
    results=[]
    for route in sites:
        cmd=["curl","--silent","--show-error","--location","--max-redirs","6",
             "--connect-timeout","10","--max-time","30",
             "--user-agent","Mozilla/5.0 (compatible; SerdarGSCIndexerAudit/1.0)",
             "--output","/dev/null","--write-out","%{http_code} %{url_effective} %{num_redirects}", ROOT_URL+route]
        p=subprocess.run(cmd,text=True,capture_output=True)
        expect(p.returncode==0,"HTTP failed "+route+": "+p.stderr[-200:])
        code,final,hops=p.stdout.strip().split(" ")
        expect(code=="200",f"HTTP failure {route}: {code}")
        expect(urlparse(final).hostname=="serdararminsargut.com",f"off-site redirect {route}: {final}")
        results.append({"url":ROOT_URL+route,"status":int(code),"final":final,"redirectCount":int(hops)})
    print("SERDAR_GSC_LIVE_READONLY_PASS "+json.dumps(results,ensure_ascii=False))
    (ROOT/"gsc-index-evidence").mkdir(exist_ok=True)
    (ROOT/"gsc-index-evidence/live.json").write_text(
      json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

if __name__=="__main__":
    expect(len(sys.argv)==2 and sys.argv[1] in ("static","live"),"static|live")
    {"static":static,"live":live}[sys.argv[1]]()
