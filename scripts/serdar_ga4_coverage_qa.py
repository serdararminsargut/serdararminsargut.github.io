#!/usr/bin/env python3
"""Serdar-only GA4 preview coverage and single-pageview proof; NO production changes."""
import argparse
import json
import re
import subprocess
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

ROOT = Path(__file__).resolve().parent.parent
BASELINE = '557bd6396dad4d6ded8bc8d3a5b76808e2ed9d88'
MEASUREMENT_ID = "G-H894LKL93J"
MARKER = '<script defer src="/assets/js/ga4-untracked-pages.js"></script>'
COVERED = [
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
PROTECTED = (
    "index.html", "en/index.html", "ar/index.html", "ru/index.html",
    "blog/index.html", "blog/en/index.html", "blog/ar/index.html",
    "blog/az/index.html", "blog/ru/index.html",
)
QA_FILES = {"assets/js/ga4-untracked-pages.js",
            "scripts/serdar_ga4_coverage_qa.py",
            ".github/workflows/serdar-ga4-test-only.yml",
            ".github/workflows/validate-sitemap.yml"}

def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True)
    return r.stdout.decode("utf-8")

def static_audit():
    assert len(COVERED) == 33 and len(set(COVERED)) == len(COVERED)
    for path in COVERED:
        original = git("show", f"{BASELINE}:{path}")
        updated = (ROOT / path).read_text(encoding="utf-8")
        assert original.count("</head>") == 1, path
        assert updated.count(MARKER) == 1, path
        assert not re.search(r"googletagmanager|gtag\s*\(|G-H894LKL93J|analytics(?:\.[\w-]+)?\.js", original, re.I), path
        expected = original.replace("</head>", MARKER + "\n</head>", 1)
        assert updated == expected, f"Not a minimal GA4 script-only change: {path}"
        assert not re.search(r'<meta[^>]+noindex', updated, re.I), path
    for path in PROTECTED:
        assert (ROOT / path).read_text(encoding="utf-8") == git("show", f"{BASELINE}:{path}"), path
    # The existing sitemap gate was referencing an obsolete PDF verifier;
    # prove that its one-purpose correction matches the immutable baseline.
    sitemap_path = ".github/workflows/validate-sitemap.yml"
    sitemap_old = git("show", f"{BASELINE}:{sitemap_path}")
    source_pdf = 'pdf_workflow = Path(".github/workflows/deploy-language-comp-card-pdfs.yml").read_text(encoding="utf-8")'
    source_producer = 'deploy_workflow = Path(".github/workflows/deploy-cloudflare-pages.yml").read_text(encoding="utf-8")'
    source_check = 'if re.search(r"(?m)^\\s+links\\s+\\\\$", pdf_workflow) is None:'
    corrected_check = 'if re.search(r"(?m)^\\s+links\\s+\\\\$", deploy_workflow) is None:'
    source_error = 'PDF workflow must preserve the link hub in its Cloudflare production bundle'
    corrected_error = 'Production deploy workflow must preserve the link hub in its Cloudflare bundle'
    assert source_pdf in sitemap_old and source_check in sitemap_old and source_error in sitemap_old
    expected_sitemap = (sitemap_old.replace(source_pdf, source_producer, 1)
                        .replace(source_check, corrected_check, 1)
                        .replace(source_error, corrected_error, 1))
    assert (ROOT / sitemap_path).read_text(encoding="utf-8") == expected_sitemap, "Unexpected sitemap QA change"
    loader = (ROOT / "assets/js/ga4-untracked-pages.js").read_text(encoding="utf-8")
    assert loader.count(MEASUREMENT_ID) == 1
    assert loader.count("w.gtag('config', measurementId)") == 1
    assert "__sasGa4PageviewOnce" in loader
    assert "mc.yandex.ru" not in loader and "webvisor" not in loader
    changed = set(git("diff", "--name-only", BASELINE, "HEAD").splitlines())
    assert changed == set(COVERED) | QA_FILES, {
        "unexpected": sorted(changed - set(COVERED) - QA_FILES),
        "missing": sorted((set(COVERED) | QA_FILES) - changed)
    }
    print(json.dumps({"result": "GA4_STATIC_PASS", "covered": len(COVERED),
                      "existingGATrackedPagesUntouched": len(PROTECTED),
                      "singleScriptPerNewPage": True, "production": "NO_GO"}))

def browser_audit():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise SystemExit("NOT_VERIFIED: Playwright is required; browser test cannot be skipped") from e
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}/"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for path in COVERED:
                    context = browser.new_context()
                    page = context.new_page()
                    requests = []
                    def mock_ga(route):
                        requests.append(route.request.url)
                        route.fulfill(status=200, content_type="application/javascript",
                                      body="window.__sasMockGtagLoaded=true;")
                    page.route("https://www.googletagmanager.com/gtag/js**", mock_ga)
                    url = base + path.replace("index.html", "") if path.endswith("/index.html") else base + path
                    page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    page.wait_for_function("window.__sasGa4PageviewOnce === true", timeout=12000)
                    def snapshot():
                        return page.evaluate("""() => ({
                          configured: Array.from(window.dataLayer || []).filter(
                            x => x[0] === 'config' && x[1] === 'G-H894LKL93J').length,
                          initializations: Array.from(window.dataLayer || []).filter(
                            x => x[0] === 'js').length,
                          tags: document.querySelectorAll('script[data-sas-ga4-untracked]').length
                        })""")
                    first = snapshot()
                    assert first == {"configured":1, "initializations":1, "tags":1}, (path, first)
                    page.add_script_tag(url=base + "assets/js/ga4-untracked-pages.js")
                    second = snapshot()
                    assert second == first, (path, "duplicate pageview after reinjection", second)
                    assert len(requests) == 1, (path, "unexpected GA4 loader count", requests)
                    context.close()
                print(f"GA4_CHROMIUM_PASS {len(COVERED)}/{len(COVERED)} unique config, script and reinjection idempotence")
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()
    static_audit()
    if args.browser: browser_audit()
