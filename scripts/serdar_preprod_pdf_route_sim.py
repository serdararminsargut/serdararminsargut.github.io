#!/usr/bin/env python3
"""Production-path PDF replacement simulation for Serdar; runner-only, NO DEPLOY.

Copy the production-shaped dist into a detached temporary directory, overlay the
four approved-for-TEST metadata-clean PDFs, verify every other file stays byte
identical, then test actual HTTP PDF routes and casting-page click requests.
Never writes source dist, repository downloads, main, or Cloudflare.
"""
import argparse
import hashlib
import http.server
import json
from pathlib import Path
import shutil
import threading
from urllib.request import urlopen

import fitz
from playwright.sync_api import sync_playwright

LANGS=("TR","EN","AR","RU")
PREFIX="Serdar-Armin-Sargut-Comp-Card-"
URL="https://serdararminsargut.com/"

def require(cond,reason):
    if not cond: raise AssertionError("SERDAR_PDF_ROUTE_SIM_NO_GO: "+reason)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(source_root, candidate_root, overlay_root):
    s=source_root.resolve(strict=True)
    c=candidate_root.resolve(strict=True)
    o=overlay_root.resolve()
    require(s.is_dir() and c.is_dir(), "source directory missing")
    require(not o.exists(), "staging overlay directory must be new")
    require(len({s,c,o})==3, "source and output paths must differ")
    require(not any(x in o.parents for x in (s,c)) and not any(x in s.parents or x in c.parents for x in (o,)), "nested path unsafe")
    require(not any(x in o.parts for x in ('dist','public','downloads')), "overlay in publish tree")
    require(not s.is_symlink() and not c.is_symlink(), "symlink source")
    manifest_file=c/"SERDAR_METADATA_PREPROD_SHA256.json"
    require(manifest_file.is_file(),"candidate SHA256 manifest missing")
    m=json.loads(manifest_file.read_text(encoding="utf-8"))
    require(m.get("project")=="SERDAR_ONLY" and m.get("publish_authorized") is False and m.get("published") is False,"production authorization flags must be false")
    by_lang={row["language"]:row for row in m["results"]}
    require(set(by_lang)==set(LANGS),"exactly four separate languages required")
    require((s/"casting-card"/"comp-card-pdf-download.js").is_file(),"download JS missing")
    js=(s/"casting-card"/"comp-card-pdf-download.js").read_text(encoding="utf-8")
    require("window.location.assign(sourceUrl)" in js and "Blob" in js,"unexpected download handler; manual review required")
    for lang in LANGS:
        file=PREFIX+lang+".pdf"
        original=s/"downloads"/file
        candidate=c/by_lang[lang]["filename"]
        page=s/"casting-card"/(lang.lower()+".html")
        require(original.is_file() and candidate.is_file() and page.is_file(),lang+": source file missing")
        require(by_lang[lang]["sha256"]==sha(candidate),lang+": candidate digest mismatch")
        require('data-download-url="/downloads/'+file+'"' in page.read_text(encoding="utf-8"),lang+": HTML button points elsewhere")
    shutil.copytree(s,o,symlinks=False)
    changed=[]
    for lang in LANGS:
        fn=PREFIX+lang+".pdf"
        orig=s/"downloads"/fn
        candidate=c/by_lang[lang]["filename"]
        staged=o/"downloads"/fn
        require(staged.is_file() and sha(orig)==sha(staged),lang+": overlay source diverged")
        shutil.copyfile(candidate,staged)
        require(sha(staged)==sha(candidate),lang+": staged overlay digest wrong")
        require(sha(orig)!=sha(staged),lang+": candidate did not replace baseline")
        with fitz.open(staged) as doc:
            require(len(doc)==2 and doc[0].rect.width>590 and doc[0].rect.width<600,lang+": A4 pages")
            require(doc.metadata.get('title')==f"Serdar Armin Sargut | Comp Card | {lang}",lang+": metadata title incorrect")
            require(any(x.get('uri')==URL for x in doc[1].get_links()),lang+": portfolio hyperlink")
            require(any(str(x.get('uri','')).startswith('mailto:') for x in doc[1].get_links()),lang+": contact hyperlink")
        changed.append("downloads/"+fn)
    before={p.relative_to(s).as_posix():sha(p) for p in s.rglob("*") if p.is_file()}
    after={p.relative_to(o).as_posix():sha(p) for p in o.rglob("*") if p.is_file()}
    require(set(before)==set(after),"overlay must have identical file path inventory")
    changed_actual={x for x in before if before[x]!=after[x]}
    require(changed_actual==set(changed),"only four PDF outputs may change")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self,*a,**kw):
            super().__init__(*a,directory=str(o),**kw)
        def log_message(self,*a):
            pass
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base="http://127.0.0.1:"+str(server.server_port)
    try:
        # Actual HTTP GET verifies the final names, MIME type, bytes and
        # exact SHA for the production route without touching production.
        for lang in LANGS:
            fn=PREFIX+lang+".pdf"
            with urlopen(base+"/downloads/"+fn,timeout=20) as response:
                body=response.read()
                require(response.status==200,lang+": HTTP status")
                require("application/pdf" in response.headers.get("Content-Type",""),lang+": MIME")
                require(body.startswith(b"%PDF-") and hashlib.sha256(body).hexdigest()==by_lang[lang]["sha256"],lang+": HTTP bytes")
        # End-to-end browser acceptance: clicking the actual download button
        # must issue the expected same-origin PDF request in every language.
        with sync_playwright() as engine:
            browser=engine.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                for lang in LANGS:
                    fn=PREFIX+lang+".pdf"
                    context=browser.new_context(accept_downloads=True)
                    context.route("**/*",lambda route: route.continue_() if route.request.url.startswith(base+"/") else route.abort())
                    page=context.new_page()
                    try:
                        response=page.goto(base+"/casting-card/"+lang.lower()+".html",wait_until="domcontentloaded",timeout=30000)
                        require(response and response.status==200,lang+": casting page HTTP")
                        button=page.locator("#comp-card-pdf-download")
                        require(button.count()==1,lang+": download button missing")
                        require(button.get_attribute("data-download-url")=="/downloads/"+fn,lang+": button target incorrect")
                        with page.expect_request("**/downloads/"+fn,timeout=20000) as event:
                            button.click(no_wait_after=True,timeout=20000)
                        request=event.value
                        require(request.url==base+"/downloads/"+fn,lang+": browser requested wrong URL")
                        print("SERDAR_PDF_STAGING_ROUTE_PASS",lang,fn,flush=True)
                    finally:
                        context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
    proof={'project':'SERDAR_ONLY','staging_only':True,'published':False,'overlaid_pdf_files':changed,'unchanged_file_count':len(before)-4,'all_other_source_sha256_preserved':True,'http_200_pdf':True,'browser_button_request':True,'sha256':{lang:by_lang[lang]['sha256'] for lang in LANGS}}
    (o.parent/"SERDAR_4_DIL_ROUTING_SIM_NO_DEPLOY_PROOF.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SERDAR_4_DIL_PREPROD_HTTP_AND_BROWSER_PASS 4/4, NO DEPLOY",flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",type=Path,required=True)
    ap.add_argument("--candidate-root",type=Path,required=True)
    ap.add_argument("--overlay-root",type=Path,required=True)
    a=ap.parse_args()
    run(a.source_root,a.candidate_root,a.overlay_root)
