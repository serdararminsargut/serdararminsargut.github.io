#!/usr/bin/env python3
"""Read-only Serdar live Cloudflare Preview browser QA; never tests production."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "https://41ba74bb.serdararminsargut.pages.dev"
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
                            heroHeadlineLines: (() => { const h=document.querySelector('.hero h1'); if(!h) return null; const st=getComputedStyle(h); return Math.round(h.getBoundingClientRect().height / parseFloat(st.lineHeight)); })()
                          };
                        }""")
                        case.update(metrics)
                        assert metrics["ready"] == "complete", "incomplete document"
                        assert metrics["lang"].lower().split("-")[0] == lang, "wrong HTML language"
                        assert metrics["h1"] == 1, "H1 uniqueness"
                        assert metrics["scrollWidth"] <= metrics["innerWidth"] + 2, "horizontal overflow"
                        assert metrics["canonical"].startswith("https://serdararminsargut.com/"), "canonical mismatch"
                        assert metrics["ogImage"].startswith("https://serdararminsargut.com/"), "OG image missing"
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
