#!/usr/bin/env python3
"""Offline structural checks for generated Serdar 26-locale preview pages."""
from pathlib import Path
import re

root = Path(__file__).with_name("dist")
pages = sorted(root.glob("*/index.html"))
assert len(pages) == 26
for page in pages:
    content = page.read_text(encoding="utf-8")
    assert 'name="robots" content="noindex,nofollow,noarchive"' in content
    assert "does not state or imply that Serdar speaks this language" in content
    assert "info@serdararminsargut.com" in content
    assert not re.search(r"(?:\\+?90|tel:|\\b0\\d{2,3}[ -]?\\d{3})", content)
assert "X-Robots-Tag: noindex, nofollow, noarchive" in (root / "_headers").read_text()
print("SERDAR_26_NOINDEX_PREVIEW_PASS 26/26")
