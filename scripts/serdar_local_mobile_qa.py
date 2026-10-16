#!/usr/bin/env python3
"""Serdar local-only Chromium QA: no Cloudflare access, deploy, or production writes."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROUTES = (
    ("/", "tr"),
    ("/en/", "en"),
    ("/ar/", "ar"),
    ("/ru/", "ru"),
    ("/blog/", "tr"),
    ("/links/", "tr"),
    ("/casting-card/tr.html", "tr"),
    ("/casting-card/ar.html", "ar"),
)
WIDTHS = (390, 430, 760, 761)


def main(origin: str, destination: Path) -> None:
    if not origin.startswith("http://127.0.0.1:") or not origin.endswith("/"):
        raise SystemExit("FAIL: only loopback HTTP source is permitted")
    destination.mkdir(parents=True, exist_ok=False)
    report = {
        "project": "SERDAR_ONLY",
        "scope": "LOCAL_CHROMIUM_TEST_ONLY",
        "cloudflareAuthenticatedPreview": "NOT_VERIFIED",
        "production": "NOT_TESTED",
        "realAndroid": "NOT_VERIFIED",
        "cases": [],
    }
    failures = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            for width in WIDTHS:
                context = browser.new_context(
                    viewport={"width": width, "height": 844},
                    device_scale_factor=1,
                    is_mobile=width <= 760,
                    has_touch=width <= 760,
                )
                context.route("**/*", lambda route: (
                    route.continue_()
                    if route.request.url.startswith(origin)
                    else route.abort()
                ))
                try:
                    for route, expected_lang in ROUTES:
                        page = context.new_page()
                        js_errors = []
                        page.on("pageerror", lambda error: js_errors.append(str(error)))
                        case = {"route": route, "width": width, "result": "NOT_VERIFIED"}
                        try:
                            response = page.goto(origin + route.lstrip("/"), wait_until="domcontentloaded", timeout=30000)
                            if response is None or response.status != 200:
                                raise AssertionError("HTTP status not 200")
                            metrics = page.evaluate("""async () => {
                              await document.fonts.ready;
                              return {
                                language: document.documentElement.lang,
                                h1: document.querySelectorAll('h1').length,
                                scrollWidth: document.documentElement.scrollWidth,
                                viewportWidth: window.innerWidth,
                                canonical: document.querySelector('link[rel="canonical"]')?.href || '',
                                robots: document.querySelector('meta[name="robots"]')?.content || ''
                              };
                            }""")
                            case.update(metrics)
                            case["jsErrors"] = js_errors
                            assert metrics["language"].lower().split("-")[0] == expected_lang, "incorrect language"
                            assert metrics["h1"] == 1, "expected one H1"
                            assert metrics["scrollWidth"] <= metrics["viewportWidth"] + 2, "horizontal overflow"
                            assert metrics["canonical"].startswith("https://serdararminsargut.com/"), "canonical origin mismatch"
                            assert "noindex" not in metrics["robots"].lower(), "indexed page has noindex"
                            case["result"] = "PASS"
                            if route == "/" and width in (390, 761):
                                page.screenshot(path=str(destination / f"serdar-home-{width}.png"), full_page=False)
                        except Exception as exc:
                            case["result"] = "FAIL"
                            case["error"] = str(exc)
                            failures.append(f"{route} @ {width}: {exc}")
                        finally:
                            report["cases"].append(case)
                            page.close()
                finally:
                    context.close()
        finally:
            browser.close()
    report["passed"] = sum(x["result"] == "PASS" for x in report["cases"])
    report["total"] = len(ROUTES) * len(WIDTHS)
    report["failures"] = failures
    (destination / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if failures:
        raise SystemExit("SERDAR MOBILE QA FAIL:\n" + "\n".join(failures))
    if report["passed"] != report["total"]:
        raise SystemExit("FAIL: incomplete matrix")
    print(f"SERDAR LOCAL MOBILE PASS {report['passed']}/{report['total']}; deployed Preview and real device NOT_VERIFIED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    main(args.url, args.output)
