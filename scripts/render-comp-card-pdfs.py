#!/usr/bin/env python3
"""Preview-only Comp Card PDF renderer. Requires playwright + Chromium.

Usage:
  python -m pip install playwright
  python -m playwright install chromium
  python scripts/render-comp-card-pdfs.py

Never run this script as part of a production deploy.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_compcard_pdf_preview"
LANGS = ("tr", "en", "ar", "ru")

def main():
    OUT.mkdir(exist_ok=True)
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
      with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for lang in LANGS:
                source = ROOT / "casting-card" / f"{lang}.html"
                assert source.is_file(), f"Missing HTML: {source}"
                page = browser.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
                page.goto(f"http://127.0.0.1:{server.server_port}/casting-card/{lang}.html", wait_until="networkidle")
                page.emulate_media(media="print")
                page.evaluate("document.fonts.ready")
                images = page.evaluate("""() => [...document.images].map(i => ({src:i.currentSrc, ok:i.complete && i.naturalWidth>0}))""")
                if not images or not all(i["ok"] for i in images):
                    raise RuntimeError(f"{lang}: broken image(s): {images}")
                if page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"):
                    raise RuntimeError(f"{lang}: horizontal overflow")
                path = OUT / f"Serdar-Armin-Sargut-Comp-Card-{lang.upper()}.pdf"
                page.pdf(path=str(path), format="A4", print_background=True, prefer_css_page_size=True)
                print(f"{lang.upper()}: {path} ({path.stat().st_size} bytes); verify page count and visual layout manually")
                page.close()
        finally:
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    main()
