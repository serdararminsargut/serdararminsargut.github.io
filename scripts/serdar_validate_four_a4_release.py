#!/usr/bin/env python3
"""Fail-closed A4 quality gate for the four Serdar Comp Card PDFs.

Called by the production workflow *before* Cloudflare deployment.
Does not modify any source, PDF, branch, site, DNS, or account.
"""
from pathlib import Path
from pypdf import PdfReader
import sys

def main(folder: Path) -> None:
    folder = folder.resolve()
    expected = ("TR", "EN", "AR", "RU")
    for lang in expected:
        path = folder / "downloads" / f"Serdar-Armin-Sargut-Comp-Card-{lang}.pdf"
        if not path.is_file():
            raise SystemExit(f"FAIL {lang}: PDF missing")
        size = path.stat().st_size
        if not 20_000 < size < 1_200_000:
            raise SystemExit(f"FAIL {lang}: invalid PDF size {size}")
        reader = PdfReader(str(path))
        if len(reader.pages) != 1:
            raise SystemExit(f"FAIL {lang}: expected exactly one A4 page, got {len(reader.pages)}")
        page = reader.pages[0]
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        if not (592 <= w <= 598 and 839 <= h <= 845):
            raise SystemExit(f"FAIL {lang}: A4 geometry {w:.1f} x {h:.1f} pt")
        content = page.extract_text() or ""
        if any(value not in content for value in ("Serdar", "2014", "162", "37")):
            raise SystemExit(f"FAIL {lang}: expected identity and approved values missing")
        count = len(list(page.images))
        if count < 6:
            raise SystemExit(f"FAIL {lang}: missing image or QR, found {count}")
        print(f"PASS {lang}: one A4, {count} images, {size} bytes")
    print("SERDAR_RELEASE_FOUR_SINGLE_A4_PASS 4/4 — safe to continue to deployment step")

if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv)>1 else "dist"))
