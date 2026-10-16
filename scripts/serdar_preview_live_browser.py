#!/usr/bin/env python3
"""Read-only Serdar live Cloudflare Preview browser QA; never tests production."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "https://8ee0f94e.serdararminsargut.pages.dev"
ROUTES = (("/", "tr"), ("/en/", "en"), ("/ar/", "ar"), ("/ru/", "ru"),
          ("/blog/", "tr"), ("/links/", "tr"),
          ("/casting-card/tr.html", "tr"), ("/casting-card/ar.html", "ar"))
WIDTHS = (390, 430, 760, 761)
OUT = Path("live-preview-evidence")
OUT.mkdir(exist_ok=False)
failures, cases = [], []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    try:
        for width in WIDTHS:
            context = browser.new_context(viewport={"width": width, "height": 844},
                                           device_scale_factor=1, is_mobile=width <= 760,
                                           has_touch=width <= 760)
            try:
                for route, lang in ROUTES:
                    page = context.new_page()
                    js_errors = []
                    page.on("pageerror", lambda err: js_errors.append(str(err)))
                    case = {"route": route, "width": width, "status": "FAIL"}
                    try:
                        response = page.goto(BASE + route, wait_until="load", timeout=30000)
                        assert response is not None and response.status == 200, "HTTP error"
                        assert "noindex" in response.headers.get("x-robots-tag", "").lower(), "Preview HTTP noindex missing"
                        metrics = page.evaluate("""async () => {
                          await document.fonts.ready;
                          return {
                            ready: document.readyState,
                            lang: document.documentElement.lang,
                            h1: document.querySelectorAll('h1').length,
                            innerWidth: innerWidth,
                            scrollWidth: document.documentElement.scrollWidth,
                            canonical: document.querySelector('link[rel="canonical"]')?.href || '',
                            ogImage: document.querySelector('meta[property="og:image"]')?.content || '',
                            imageCount: document.querySelectorAll('img').length,
                            heroHeadlineLines: (() => { const h=document.querySelector('.hero h1'); if(!h) return null; const st=getComputedStyle(h); return Math.round(h.getBoundingClientRect().height / parseFloat(st.lineHeight)); })(),
                            creditsColumns: (() => { const el=document.querySelector('.credits'); if(!el) return null; return getComputedStyle(el).gridTemplateColumns.split(' ').filter(Boolean).length; })(),
                            creditsStylesheetLoaded: [...document.styleSheets].some(s => !!s.href && s.href.includes('/assets/css/site.css')),
                            galleryColumns: (() => { const el=document.querySelector('.gallery'); if(!el) return null; return getComputedStyle(el).gridTemplateColumns.split(' ').filter(Boolean).length; })()
                          };
                        }""")
                        case.update(metrics)
                        assert metrics["ready"] == "complete", "incomplete document"
                        assert metrics["lang"].lower().split("-")[0] == lang, "wrong HTML language"
                        assert metrics["h1"] == 1, "H1 uniqueness"
                        assert metrics["scrollWidth"] <= metrics["innerWidth"] + 2, "horizontal overflow"
                        assert metrics["canonical"].startswith("https://serdararminsargut.com/"), "canonical mismatch"
                        assert metrics["ogImage"].startswith("https://serdararminsargut.com/"), "OG image missing"
                        if route == "/":
                            assert metrics["creditsStylesheetLoaded"], "Serdar main stylesheet not loaded"
                            assert metrics["creditsColumns"] == 1, "Acting credit cards not one-column on mobile"
                            if width in (390, 430):
                                assert metrics["galleryColumns"] == 2, "photo gallery not two-column on phone"
                        if route == "/" and width == 761:
                            assert metrics["heroHeadlineLines"] is not None and metrics["heroHeadlineLines"] <= 6, "tablet hero headline is excessively fragmented"
                        assert not js_errors, "JavaScript exception: " + str(js_errors[:2])
                        case["status"] = "PASS"
                        if route == "/" and width in (390, 761):
                            page.screenshot(path=str(OUT / f"home-{width}.png"), full_page=False)
                    except Exception as exc:
                        case["error"] = str(exc)
                        failures.append(f"{route} @ {width}: {exc}")
                    finally:
                        cases.append(case)
                        page.close()
            finally:
                context.close()
    finally:
        browser.close()
report = {"project": "SERDAR_ONLY", "source": "CLOUDFLARE_IMMUTABLE_PREVIEW",
          "url": BASE, "production": "NOT_TOUCHED",
          "realAndroid": "NOT_VERIFIED",
          "passed": sum(c["status"] == "PASS" for c in cases),
          "total": len(ROUTES) * len(WIDTHS),
          "cases": cases, "failures": failures}
(OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
if failures:
    raise SystemExit("SERDAR LIVE PREVIEW BROWSER FAIL:\n" + "\n".join(failures))
print(f"SERDAR LIVE PREVIEW BROWSER PASS {report['passed']}/{report['total']}, physical Android NOT_VERIFIED")

# Test the exact Comp Card button users tap, not just the containing HTML page.
# This was omitted from earlier browser QA, allowing missing PDFs to ship.
pdf_results = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    try:
        context = browser.new_context(accept_downloads=True)
        try:
            for lang in ("TR", "EN", "AR", "RU"):
                file_name = f"Serdar-Armin-Sargut-Comp-Card-{lang}.pdf"
                pdf_url = f"{BASE}/downloads/{file_name}"
                result = {"lang": lang, "file": file_name, "status": "FAIL"}
                try:
                    http = context.request.get(pdf_url, timeout=30000)
                    assert http.status == 200, f"PDF HTTP {http.status}"
                    assert "application/pdf" in http.headers.get("content-type", ""), "PDF Content-Type missing"
                    pdf_content = http.body()
                    assert len(pdf_content) > 20000 and pdf_content.startswith(b"%PDF-"), "invalid PDF bytes"
                    page = context.new_page()
                    try:
                        page_response = page.goto(f"{BASE}/casting-card/{lang.lower()}.html",
                                                  wait_until="load", timeout=30000)
                        assert page_response is not None and page_response.status == 200, "Comp Card HTML error"
                        assert page.locator("h1").count() >= 1, "Comp Card heading missing"
                        assert not page.locator("body").inner_text().startswith("Sayfa bulunamadı"), "404 fallback"
                        with page.expect_download(timeout=12000) as download_info:
                            page.locator("#comp-card-pdf-download").click()
                        download = download_info.value
                        assert download.suggested_filename == file_name, "wrong download filename"
                        saved = download.path()
                        assert saved is not None and saved.stat().st_size > 20000, "button downloaded empty file"
                        assert saved.open("rb").read(5) == b"%PDF-", "button download is not a real PDF"
                        result["status"] = "PASS"
                        result["bytes"] = len(pdf_content)
                    finally:
                        page.close()
                except Exception as exc:
                    result["error"] = str(exc)
                    pdf_results.append(result)
                    raise
                pdf_results.append(result)
                print("SERDAR_LIVE_PDF_BUTTON " + json.dumps(result), flush=True)
        finally:
            context.close()
    finally:
        browser.close()
(OUT / "pdf-buttons.json").write_text(json.dumps(pdf_results, indent=2) + "\n")
print("SERDAR_LIVE_PDF_BUTTON_PASS 4/4", flush=True)

# Verify actual portfolio link navigation as well as direct Comp Card URLs.
more_routes = (
    "/casting-card/tr", "/casting-card/en", "/casting-card/ar",
    "/casting-card/ru", "/casting-card/",
    "/postcard.html", "/postcard", "/card", "/card.html",
    "/blog/erkek-cocuk-urun-modeli/",
    "/en/gulf-child-model-portfolio/",
    "/ar/dalil-malaf-model-atfal-al-khalij/",
)
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    try:
        context = browser.new_context()
        for route in more_routes:
            response = context.request.get(BASE + route, timeout=20000)
            assert response.status == 200, f"{route}: unexpected HTTP {response.status}"
            body = response.text()
            assert "bu GitHub aynasında bulunamadı" not in body, f"{route}: legacy 404"
            assert "İstenen sayfa veya dosya bulunamadı" not in body, f"{route}: updated 404"
            print("SERDAR_LINK_PASS " + route, flush=True)
        page = context.new_page()
        first = page.goto(BASE + "/", wait_until="load", timeout=20000)
        assert first and first.status == 200, "homepage failed"
        target = page.locator('a[href="/casting-card/tr.html"]').first
        assert target.count() == 1, "Comp Card link missing on home"
        target.click()
        page.wait_for_url("**/casting-card/tr*", timeout=20000)
        assert "Serdar Armin Sargut" in page.locator("body").inner_text(), "Comp Card click landed on wrong page"
        assert page.locator("#comp-card-pdf-download").count() == 1, "Comp Card button missing"
        print("SERDAR_HOMEPAGE_TO_COMP_CARD_NAV_PASS", flush=True)
    finally:
        browser.close()
print(f"SERDAR_SECONDARY_LINKS_PASS {len(more_routes)}/{len(more_routes)}", flush=True)


