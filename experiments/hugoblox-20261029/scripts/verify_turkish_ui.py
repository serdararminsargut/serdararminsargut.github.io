#!/usr/bin/env python3
"""Verify rendered Turkish HugoBlox page labels before any Preview deployment."""
from __future__ import annotations
import html
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public")
pages = sorted((root / "post").glob("*/index.html"))
if len(pages) != 3:
    raise SystemExit(f"FAIL: expected 3 HugoBlox guide pages, found {len(pages)}")
for p in pages:
    source = p.read_text(encoding="utf-8")
    # Test final generated HTML, not merely an i18n configuration file.
    visible = html.unescape(re.sub(r"<[^>]+>", " ", source))
    visible = re.sub(r"\s+", " ", visible)
    required = ["Son güncelleme:", "dakika okuma"]
    unwanted = ["Last updated on", "min read"]
    missing = [label for label in required if label not in visible]
    untranslated = [label for label in unwanted if label in visible]
    if missing or untranslated:
        raise SystemExit(f"FAIL: Turkish UI {p}: missing={missing}, untranslated={untranslated}")
    print(f"PASS: Turkish UI generated HTML: {p}")
print(f"PASS: Turkish UI verified for {len(pages)} draft article pages")
