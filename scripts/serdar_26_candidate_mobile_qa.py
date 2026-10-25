#!/usr/bin/env python3
"""Local responsive browser gate for the isolated Serdar 26-locale candidate."""
from pathlib import Path
import json
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / os.environ.get("SERDAR_26_SOURCE_DIR", "serdar-26-candidate/casting-card")
OUT = ROOT / os.environ.get("SERDAR_26_QA_OUT", "serdar-26-candidate/mobile-qa")
EXPECTED_ROBOTS = os.environ.get("SERDAR_26_EXPECTED_ROBOTS", "noindex,nofollow,noarchive")
LOCALES = ("tr","en","ru","ar","az","de","fr","es","kk","uz","ky","tk","it","pt-br","uk","pl","bg","el","sr-latn","sq","fa","ur","hi","zh-hans","ja","ko")
RTL = {"ar", "fa", "ur"}
LANG_TAG = {code: code for code in LOCALES}
LANG_TAG.update({"pt-br": "pt-BR", "sr-latn": "sr-Latn", "zh-hans": "zh-Hans"})
WIDTHS = (390, 430)

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results, failures = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            for width in WIDTHS:
                context = browser.new_context(viewport={"width": width, "height": 844}, is_mobile=True, has_touch=True)
                try:
                    for code in LOCALES:
                        page = context.new_page()
                        try:
                            relative_source = SOURCE.relative_to(ROOT).as_posix()
                            response = page.goto(f"http://127.0.0.1:8765/{relative_source}/{code}.html", wait_until="load", timeout=30000)
                            assert response and response.status == 200
                            page.wait_for_function("""() => {
                              const hero = document.querySelector('.headshot');
                              return hero && hero.complete && hero.naturalWidth > 0
                                && hero.getBoundingClientRect().width > 100
                                && hero.getBoundingClientRect().height > 100;
                            }""", timeout=15000)
                            # Let Chromium paint decoded WebP pixels before preserving visual evidence.
                            page.wait_for_timeout(500)
                            metrics = page.evaluate("""async () => {
                              await document.fonts.ready;
                              const hero = document.querySelector('.headshot').getBoundingClientRect();
                              return {lang:document.documentElement.lang, dir:document.documentElement.dir || 'ltr',
                                h1:document.querySelectorAll('h1').length, scrollWidth:document.documentElement.scrollWidth,
                                viewport:window.innerWidth, robots:document.querySelector('meta[name=robots]')?.content || '',
                                selector:document.querySelectorAll('.language-switch a').length,
                                hero:{width:hero.width,height:hero.height},
                                images:[...document.images].map(x=>({ok:x.complete && x.naturalWidth>0,src:x.currentSrc}))};
                            }""")
                            assert metrics["lang"] == LANG_TAG[code]
                            assert metrics["dir"] == ("rtl" if code in RTL else "ltr")
                            assert metrics["h1"] == 1
                            assert metrics["scrollWidth"] <= metrics["viewport"] + 2, metrics
                            assert metrics["robots"] == EXPECTED_ROBOTS
                            assert metrics["selector"] == 26
                            assert metrics["hero"]["width"] > 100 and metrics["hero"]["height"] > 100, metrics["hero"]
                            assert all(i["ok"] for i in metrics["images"]), metrics["images"]
                            results.append({"locale": code, "width": width, "result": "PASS"})
                            if code in {"tr", "ar", "ja"} and width == 390:
                                page.screenshot(path=str(OUT / f"{code}-{width}.png"), full_page=True)
                        except Exception as exc:
                            failures.append(f"{code}@{width}: {exc}")
                            results.append({"locale": code, "width": width, "result": "FAIL", "error": str(exc)})
                        finally:
                            page.close()
                finally:
                    context.close()
        finally:
            browser.close()
    (OUT / "report.json").write_text(json.dumps({"project":"SERDAR_ONLY","scope":"LOCAL_TEST_ONLY","source":str(SOURCE.relative_to(ROOT)),"results":results,"failures":failures}, ensure_ascii=False, indent=2), encoding="utf-8")
    if failures:
        raise SystemExit("SERDAR_26_MOBILE_QA_FAIL\n" + "\n".join(failures))
    print(f"SERDAR_26_MOBILE_QA_PASS {len(results)}/{len(LOCALES)*len(WIDTHS)}")

if __name__ == "__main__":
    main()
