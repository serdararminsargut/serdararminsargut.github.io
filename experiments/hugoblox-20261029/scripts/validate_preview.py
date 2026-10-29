#!/usr/bin/env python3
"""Verify draft content, page generation and noindex after an isolated Hugo build."""
from pathlib import Path
import re
person = Path("site_identity.txt").read_text().strip().lower()
slugs = {
 "serdar": ["cocuk-giyim-e-ticaret-cekimlerinde-portfoy-secimi", "spor-giyim-ayakkabi-katalog-fotograflari", "cocuk-oyuncu-casting-sunum-dosyasi"],
 "duru": ["tiyatro-deneyiminden-kamera-onu-oyunculuguna", "cocuk-oyuncu-self-tape-dosya-duzeni", "genc-oyuncu-showreel-sahne-ve-ekran-secimi"]
}
assert person in slugs, "FAIL: unknown identity"
root = Path("public")
files = list(root.rglob("*.html"))
assert len(files) >= 4, f"FAIL: only {len(files)} HTML files; expected 4 or more"
for slug in slugs[person]:
    assert any(slug in str(p) for p in files), f"FAIL: missing slug {slug}"
for p in files:
    s = p.read_text(encoding="utf-8")
    assert re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']noindex,nofollow,noarchive["\']', s, re.I), f"FAIL: {p} not noindex"
    assert "<html" in s.lower() and "</html" in s.lower(), f"FAIL: incomplete HTML {p}"
assert (root/"robots.txt").read_text() == "User-agent: *\nDisallow: /\n", "FAIL: robots"
assert "X-Robots-Tag: noindex, nofollow" in (root/"_headers").read_text(), "FAIL: headers"
print(f"PASS: {person}: {len(files)} HTML pages / all expected slugs / noindex")
