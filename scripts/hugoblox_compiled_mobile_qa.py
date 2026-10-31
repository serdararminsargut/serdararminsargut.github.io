#!/usr/bin/env python3
"""Local Chromium acceptance of the COMPILED Serdar HugoBlox Preview, not production."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROUTES = (
    "/rehber/",
    "/rehber/post/",
    "/rehber/post/cocuk-oyuncu-casting-sunum-dosyasi/",
    "/rehber/portfoy-guncel/",
)
WIDTHS = (360, 390, 430, 1280)
CTA = {
    "portfolio": "https://serdararminsargut.com/",
    "casting": "https://serdararminsargut.com/casting-card/tr.html",
    "instagram": "https://www.instagram.com/serdararminsargutt/",
}

def main(origin, destination):
    if not origin.startswith("http://127.0.0.1:") or not origin.endswith("/"):
        raise SystemExit("BLOCKED: QA only accepts a loopback staging server")
    destination.mkdir(parents=True, exist_ok=False)
    records, failures = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            for width in WIDTHS:
                context = browser.new_context(
                    viewport={"width": width, "height": 860},
                    device_scale_factor=1,
                    is_mobile=width < 1000,
                    has_touch=width < 1000,
                )
                # For local QA, never navigate/fetch production, Meta, or other domains.
                context.route("**/*", lambda route: (
                    route.continue_() if route.request.url.startswith(origin) else route.abort()
                ))
                try:
                    for route in ROUTES:
                        page = context.new_page()
                        js_errors = []
                        page.on("pageerror", lambda e: js_errors.append(str(e)))
                        case = {"route": route, "width": width, "status": "NOT_TESTED"}
                        try:
                            response = page.goto(origin + route.lstrip("/"), wait_until="load", timeout=30000)
                            assert response is not None and response.status == 200, "Expected HTTP 200"
                            page.wait_for_timeout(300)
                            info = page.evaluate("""() => ({
                                lang: document.documentElement.lang,
                                robots: document.querySelector('meta[name="robots"]')?.content || '',
                                viewport: document.documentElement.clientWidth,
                                scroll: document.documentElement.scrollWidth,
                                h1: document.querySelectorAll('h1').length,
                                css: [...document.styleSheets].filter(x =>
                                    x.href && x.href.includes('/rehber/css/')).length,
                                font: getComputedStyle(document.body).fontFamily,
                            })""")
                            case.update(info)
                            case["jsErrors"] = js_errors
                            assert info["lang"].lower().split("-")[0] == "tr", "HTML lang mismatch"
                            assert "noindex" in info["robots"].lower(), "Preview noindex missing"
                            assert info["scroll"] <= info["viewport"] + 3, "Horizontal overflow"
                            if route != "/rehber/portfoy-guncel/":
                                assert info["css"] >= 1, "HugoBlox CSS absent"
                                assert info["h1"] >= 1, "HugoBlox heading missing"
                            if route == "/rehber/":
                                case["cta"] = {}
                                heading = page.locator("#serdar-hugo-cta")
                                assert heading.count() == 1 and heading.is_visible(), "CTA heading missing"
                                links_list = page.locator("#serdar-hugo-cta + ul")
                                assert links_list.count() == 1, "CTA link list not adjacent to heading"
                                layout = links_list.evaluate("""el => ({
                                    display: getComputedStyle(el).display,
                                    columns: getComputedStyle(el).gridTemplateColumns,
                                    width: el.getBoundingClientRect().width
                                })""")
                                assert layout["display"] == "grid", "CTA CSS grid not applied"
                                case["ctaLayout"] = layout
                                for name, url in CTA.items():
                                    matches = page.locator('#serdar-hugo-cta + ul a[href="' + url + '"]')
                                    visible = next((matches.nth(i) for i in range(matches.count())
                                                    if matches.nth(i).is_visible()), None)
                                    assert visible is not None, name + " CTA absent/hidden"
                                    style = visible.evaluate("""el => {
                                        const r = el.getBoundingClientRect();
                                        const s = getComputedStyle(el);
                                        return {height:r.height,width:r.width,minHeight:s.minHeight,
                                            background:s.backgroundColor,color:s.color,
                                            decoration:s.textDecorationLine,display:s.display}
                                    }""")
                                    assert style["height"] >= 44, name + " touch target below 44px"
                                    assert style["display"] == "flex", name + " CTA box style not loaded"
                                    assert style["decoration"] == "none", name + " CTA still plain link"
                                    if name == "casting":
                                        assert style["background"] != "rgb(255, 255, 255)", "Primary CTA background not applied"
                                    visible.scroll_into_view_if_needed(timeout=4000)
                                    visible.click(trial=True, timeout=4000)
                                    case["cta"][name] = {"result":"ACTIONABLE","style":style}
                                page.screenshot(path=str(destination / ("serdar-hugoblox-%s.png" % width)),
                                                full_page=False)
                            assert not js_errors, "JavaScript runtime error(s)"
                            case["status"] = "PASS"
                        except Exception as exc:
                            case["status"] = "FAIL"
                            case["reason"] = str(exc)
                            failures.append(f"{route} @ {width}: {exc}")
                        finally:
                            records.append(case)
                            page.close()
                finally:
                    context.close()
        finally:
            browser.close()
    summary = {
        "project": "SERDAR_ONLY",
        "scope": "COMPILED_HUGOBLOX_LOCAL_CHROMIUM_QA",
        "deployed_preview": "NOT_VERIFIED",
        "real_android": "NOT_VERIFIED",
        "tested": len(records),
        "passed": sum(x["status"] == "PASS" for x in records),
        "failures": failures,
        "cases": records,
    }
    (destination / "report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("HUGOBLOX_COMPILED_MOBILE_QA:", summary["passed"], "/", summary["tested"],
          "local Chromium; external protected Preview NOT_VERIFIED", flush=True)
    if failures:
        raise SystemExit("HUGOBLOX_COMPILED_MOBILE_QA_FAIL:\n" + "\n".join(failures))

if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("--url", required=True)
    argp.add_argument("--output", type=Path, required=True)
    args = argp.parse_args()
    main(args.url, args.output)
