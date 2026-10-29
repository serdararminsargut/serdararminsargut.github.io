#!/usr/bin/env python3
"""For unpublished drafts only: force a noindex policy on generated HTML."""
from pathlib import Path
import re
out = Path("public")
if not out.is_dir():
    raise SystemExit("FAIL: Hugo did not create public/")
count = 0
for p in out.rglob("*.html"):
    s = p.read_text(encoding="utf-8")
    s = re.sub(r'<meta\s+[^>]*name=["\']robots["\'][^>]*>', "", s, flags=re.I)
    if not re.search(r"</head\s*>", s, flags=re.I):
        raise SystemExit(f"FAIL: missing head in {p}")
    s = re.sub(r"</head\s*>", '<meta name="robots" content="noindex,nofollow,noarchive">\n</head>', s, count=1, flags=re.I)
    p.write_text(s, encoding="utf-8")
    count += 1
(out/"robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
(out/"_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n  Cache-Control: no-store\n", encoding="utf-8")
print(f"PASS: {count} HTML noindex safeguards applied (not deployed)")
