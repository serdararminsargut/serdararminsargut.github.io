#!/usr/bin/env python3
"""Fail-closed, staging-only correction for untranslated upstream HugoBlox labels.

Only the three Serdar draft guide HTML documents are modified. No source
articles, production routes, or generated PDFs are touched. This is a
temporary output-level workaround pending a stable upstream i18n fix.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public")
guides = sorted((root / "post").glob("*/index.html"))
if len(guides) != 3:
    raise SystemExit(f"FAIL locale patch: expected 3 guides; found {len(guides)}")
translations = {
    "Last updated on": "Son güncelleme: ",
    "min read": "dakika okuma",
}
for page in guides:
    content = page.read_text(encoding="utf-8")
    for english, turkish in translations.items():
        count = content.count(english)
        if count != 1:
            raise SystemExit(
                f"FAIL locale patch: expected exactly one {english!r} in {page}, got {count}"
            )
        content = content.replace(english, turkish, 1)
    page.write_text(content, encoding="utf-8")
    print(f"PASS preview locale patch: {page}")
print("PASS: 3 Turkish draft guide outputs patched; verification runs separately")
