#!/usr/bin/env python3
"""Preview-only Serdar GA4 proof. No production changes, no real GA4 events."""
import json
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse
from serdar_ga4_coverage_qa import COVERED, MARKER

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
PROOF = ROOT / "preview-evidence"
EXPECTED_BRANCH = "refs/heads/test/serdar-ga4-coverage-20261017"
MEASUREMENT_ID = "G-H894LKL93J"
GUARD_TAG = '<script src="/assets/js/serdar-ga4-preview-disable.js"></script>'
SRC_DIRS = ("assets", "ar", "az", "blog", "casting-card", "de", "downloads",
            "en", "fa", "fr", "it", "kk", "ky", "links", "projeler",
            "rehber", "ru", "tk", "uz", "zh-cn", "erkek-cocuk-model",
            "spor-giyim-cocuk-modeli", "cocuk-giyim-modeli",
            "e-ticaret-cocuk-modeli")
SRC_FILES = ("_headers", "_redirects", "404.html", "index.html", "robots.txt",
             "sitemap.xml", "sitemap-google.xml", "sitemap.txt", "favicon.svg",
             "favicon.ico", "favicon-96x96.png", ".nojekyll", "ai.txt",
             "llms.txt", "llms-full.txt", "indexnow-key.txt",
             "72f0dad836e29ffcc2d9dd42a794dbf0.txt", "card.html",
             "postcard.html")

def build():
    assert os.environ.get("GITHUB_REF") == EXPECTED_BRANCH, "Not isolated Serdar GA4 test branch"
    assert len(COVERED) == len(set(COVERED)) == 33
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    PROOF.mkdir(exist_ok=True)
    for d in SRC_DIRS:
        if (ROOT / d).is_dir():
            shutil.copytree(ROOT / d, DIST / d)
    for f in SRC_FILES:
        if (ROOT / f).is_file():
            shutil.copy2(ROOT / f, DIST / f)
    for src in ROOT.glob("yandex_*.html"):
        shutil.copy2(src, DIST / src.name)
    (DIST / "assets/js/serdar-ga4-preview-disable.js").write_text(
        'window["ga-disable-G-H894LKL93J"] = true;\n'
        'window.__serdarGa4PreviewOnly = true;\n', encoding="utf-8")
    covered_count = 0
    pages_modified = 0
    for source in DIST.rglob("*.html"):
        original = source.read_text(encoding="utf-8")
        match = re.search(r"<head\b[^>]*>", original, flags=re.I)
        if not match:
            continue
        assert GUARD_TAG not in original, source
        updated = original[:match.end()] + GUARD_TAG + original[match.end():]
        source.write_text(updated, encoding="utf-8")
        pages_modified += 1
        relative = source.relative_to(DIST).as_posix()
        if relative in COVERED:
            assert original.count(MARKER) == 1, relative
            assert updated.count(MARKER) == 1, relative
            assert updated.count(GUARD_TAG) == 1, relative
            assert updated.replace(GUARD_TAG, "", 1) == original, relative
            covered_count += 1
    assert covered_count == len(COVERED) == 33, ("Missing GA4 pages", covered_count)
    assert (DIST / "assets/js/ga4-untracked-pages.js").read_bytes() == (
        ROOT / "assets/js/ga4-untracked-pages.js").read_bytes()
    h = DIST / "_headers"
    original_headers = h.read_text(encoding="utf-8")
    assert original_headers.startswith("/*\n")
    headers = original_headers.replace(
        "/*\n", "/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n", 1)
    headers, n_connect = re.subn(
        r"connect-src [^;]+;", "connect-src 'self';", headers, count=1)
    headers, n_img = re.subn(
        r"img-src [^;]+;", "img-src 'self' data: https://i.vimeocdn.com;",
        headers, count=1)
    assert n_connect == n_img == 1
    assert headers.count("X-Robots-Tag: noindex, nofollow, noarchive") == 1
    assert "connect-src 'self';" in headers
    h.write_text(headers, encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    assert (ROOT / "_headers").read_text(encoding="utf-8") == original_headers
    assert (ROOT / "robots.txt").read_text(encoding="utf-8") != (
        DIST / "robots.txt").read_text(encoding="utf-8")
    assert not (DIST / ".github").exists()
    assert not (DIST / "scripts").exists()
    proof = {"branch": EXPECTED_BRANCH, "status": "PREVIEW_ONLY",
             "covered": covered_count, "guardedHtmlPages": pages_modified,
             "noindex": True, "analyticsCollectionCspBlocked": True,
             "gaDisable": True, "originalSourceUnchanged": True,
             "previewUploadsNoPrivateRepoFiles": True, "production": "NO_GO"}
    (PROOF / "bundle.json").write_text(
        json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("SERDAR_PREVIEW_BUNDLE_PASS " + json.dumps(proof, sort_keys=True))

def verify_remote():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise AssertionError("Playwright missing; can't call this PASS") from exc
    url = os.environ.get("PREVIEW_URL", "").rstrip("/")
    parsed = urlparse(url)
    assert parsed.scheme == "https" and parsed.hostname, "No verified HTTPS preview URL"
    assert parsed.hostname.endswith(".serdararminsargut.pages.dev")
    assert parsed.hostname != "serdararminsargut.pages.dev"
    PROOF.mkdir(exist_ok=True)
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            routes = ("/", "/blog/erkek-cocuk-urun-modeli/",
                      "/blog/istanbul-cocuk-oyuncu-casting/",
                      "/casting-card/en", "/de/kinder-sportmode-model/",
                      "/en/", "/links/")
            for route in routes:
                context = browser.new_context()
                page = context.new_page()
                outbound = []
                gtag = []
                def block_ga(r):
                    outbound.append(r.request.url)
                    r.abort()
                def fake_gtag(r):
                    gtag.append(r.request.url)
                    r.fulfill(status=200, content_type="application/javascript",
                              body="window.__serdarMockGtagLoaded = true;")
                page.route("**/*google-analytics.com/**", block_ga)
                page.route("**/g/collect*", block_ga)
                page.route("https://www.googletagmanager.com/gtag/js**", fake_gtag)
                response = page.goto(url + route, wait_until="domcontentloaded",
                                     timeout=25000)
                assert response is not None and response.status == 200, (
                    route, response.status if response else None,
                    "NO-GO: inaccessible or Cloudflare Access protected preview")
                assert "noindex" in response.headers.get("x-robots-tag", "").lower(), (
                    route, "Missing live noindex header")
                assert "connect-src 'self';" in response.headers.get(
                    "content-security-policy", ""), (route, "Collect CSP missing")
                page.wait_for_function(
                    "window.__serdarGa4PreviewOnly === true && "
                    "window['ga-disable-G-H894LKL93J'] === true", timeout=12000)
                assert not outbound, (route, "Analytics send attempt on preview", outbound)
                if route in ("/blog/erkek-cocuk-urun-modeli/",
                             "/blog/istanbul-cocuk-oyuncu-casting/",
                             "/casting-card/en", "/de/kinder-sportmode-model/"):
                    page.wait_for_function(
                        "window.__sasGa4PageviewOnce === true", timeout=12000)
                    metrics = page.evaluate("""() => ({
                        configs: Array.from(window.dataLayer || []).filter(
                          x => x[0] === 'config' && x[1] === 'G-H894LKL93J').length,
                        tags: document.querySelectorAll(
                          'script[data-sas-ga4-untracked]').length
                    })""")
                    assert metrics == {"configs":1, "tags":1}, (route, metrics)
                    assert len(gtag) == 1, (route, gtag)
                assert not outbound, (route, "GA4 egress detected", outbound)
                results.append({"route":route,"http":200,"noindex":True,
                                "analyticsSuppressed":True,
                                "gtagLoaderIntercepted":len(gtag)})
                context.close()
        finally:
            browser.close()
    # Cloudflare challenges urllib's default User-Agent (HTTP 403); use
    # the same curl read-only probe already passed by the HTTP gate.
    import subprocess
    robots = subprocess.run(
        ["curl", "--silent", "--show-error", "--fail",
         "--connect-timeout", "10", "--max-time", "20", url + "/robots.txt"],
        capture_output=True, check=True).stdout.decode("utf-8")
    assert "Disallow: /" in robots
    out = {"status":"PASS", "url":url, "routes":results,
           "analyticsProductionEventsEmitted":False,
           "notes":"Google tag loader mocked during browser checks; live GA4 hits deliberately suppressed. No production measurement proof."}
    (PROOF / "remote.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("SERDAR_PREVIEW_BROWSER_PASS routes=" + str(len(results)) +
          " live_noindex=PASS ga4_send_suppression=PASS")

if __name__ == "__main__":
    assert len(sys.argv) == 2 and sys.argv[1] in ("build", "verify")
    {"build":build,"verify":verify_remote}[sys.argv[1]]()
