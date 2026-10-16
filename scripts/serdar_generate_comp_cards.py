#!/usr/bin/env python3
"""Generate the four approved Serdar HTML Comp Cards as A4 PDFs in dist.

No production calls, accounts, Cloudflare Access, or remote content. Runs in
the Pages build against on-disk Serdar files; failure blocks deployment.
"""
import argparse
import hashlib
import http.server
from io import BytesIO
import json
from pathlib import Path
import threading
from urllib.parse import unquote, urlsplit

from PIL import Image
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

LANGUAGES = ("TR", "EN", "AR", "RU")
OUT_PREFIX = "Serdar-Armin-Sargut-Comp-Card-"


def run(root: Path) -> None:
    root = root.resolve()
    assert root.is_dir(), "Dist build directory missing"
    for lang in LANGUAGES:
        assert (root / "casting-card" / (lang.lower() + ".html")).is_file()
    assert (root / "assets" / "photos").is_dir()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def log_message(self, fmt, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:" + str(server.server_port)
    (root / "downloads").mkdir(exist_ok=True)
    results = []
    photo_cache = {}

    def serve_only_local_assets(route):
        url = route.request.url
        if not url.startswith(base + "/"):
            route.abort()
            return
        relative_path = unquote(urlsplit(url).path).lstrip("/")
        if relative_path.startswith("assets/photos/") and relative_path.lower().endswith(
            (".webp", ".jpeg", ".jpg", ".png")
        ):
            path = (root / relative_path).resolve()
            assert path.is_relative_to(root) and path.is_file(), "photo outside local dist"
            if path not in photo_cache:
                with Image.open(path) as original:
                    image = original.convert("RGB")
                    image.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
                    buffer = BytesIO()
                    image.save(buffer, "JPEG", quality=82, subsampling=0, optimize=True)
                    photo_cache[path] = buffer.getvalue()
            route.fulfill(status=200, body=photo_cache[path], content_type="image/jpeg")
            return
        route.continue_()

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for lang in LANGUAGES:
                    context = browser.new_context()
                    context.route("**/*", serve_only_local_assets)
                    page = context.new_page()
                    try:
                        response = page.goto(
                            base + "/casting-card/" + lang.lower() + ".html",
                            wait_until="load",
                            timeout=30000,
                        )
                        assert response is not None and response.status == 200, "HTML source not served"
                        assert page.locator("html").get_attribute("lang").lower().startswith(lang.lower())
                        images = page.evaluate("""() => [...document.images].map(img =>
                          ({src:img.currentSrc, complete:img.complete, width:img.naturalWidth}))""")
                        assert images, "Comp Card must include images"
                        assert all(img["complete"] and img["width"] > 0 for img in images), (
                            f"{lang}: failed local image: " + str([i for i in images if not i["width"]])
                        )
                        assert page.locator(".card-shell").count() == 1, "Comp Card template missing"
                        await_fonts = page.evaluate("() => document.fonts.ready.then(() => true)")
                        assert await_fonts
                        data = page.pdf(
                            format="A4", prefer_css_page_size=True,
                            print_background=True, display_header_footer=False,
                        )
                        file_name = OUT_PREFIX + lang + ".pdf"
                        target = root / "downloads" / file_name
                        target.write_bytes(data)
                        assert data.startswith(b"%PDF-"), "PDF signature missing"
                        assert 20000 < len(data) < 3000000, (
                            f"{lang}: PDF too large for mobile delivery: {len(data)} bytes"
                        )
                        doc = PdfReader(str(target))
                        assert 1 <= len(doc.pages) <= 2, f"{lang}: unexpected {len(doc.pages)} A4 pages"
                        pages_text = "\n".join(p.extract_text() or "" for p in doc.pages)
                        assert "Serdar" in pages_text and "162" in pages_text, (
                            f"{lang}: validated name/height not represented in PDF text"
                        )
                        result = {
                            "language": lang, "file": "downloads/" + file_name,
                            "pages": len(doc.pages), "bytes": len(data),
                            "sha256": hashlib.sha256(data).hexdigest(),
                            "imagesLoaded": len(images),
                            "source": "casting-card/" + lang.lower() + ".html",
                        }
                        results.append(result)
                        print("SERDAR_COMP_CARD_PDF_PASS " + json.dumps(result), flush=True)
                    finally:
                        page.close()
                        context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()

    assert len(results) == 4, "Not all four language PDFs generated"
    manifest = root / "downloads" / "serdar-pdf-evidence.json"
    manifest.write_text(json.dumps({"project": "SERDAR_ONLY", "files": results}, indent=2) + "\n")
    print("SERDAR_ALL_COMP_CARD_PDFS_PASS 4/4", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="static build directory (dist)")
    args = parser.parse_args()
    run(args.root)
