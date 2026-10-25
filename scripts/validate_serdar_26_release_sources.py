#!/usr/bin/env python3
"""Static gate for the unpublishable Serdar 26-locale release-source package."""
from pathlib import Path
import re

from build_serdar_26_candidate import LANGUAGE_NOTE, L, LANG_TAG
from build_serdar_26_release_sources import EXTRAS, NAV

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "serdar-26-release-sources" / "casting-card"
RTL = {"ar", "fa", "ur"}


def main() -> None:
    found = tuple(sorted(p.stem for p in PAGES.glob("*.html")))
    assert found == tuple(sorted(L)), found
    for code in L:
        body = (PAGES / f"{code}.html").read_text(encoding="utf-8")
        tag = LANG_TAG[code]
        assert f'<html lang="{tag}"' in body
        assert (f'<html lang="{tag}" dir="rtl"' in body) == (code in RTL)
        assert 'name="robots" content="index,follow"' in body
        assert f'<link rel="canonical" href="https://serdararminsargut.com/casting-card/{code}">' in body
        assert LANGUAGE_NOTE[code] in body
        assert EXTRAS[code][0] in body and EXTRAS[code][1] in body
        for nav_label in NAV[code]:
            assert nav_label in body
        assert 'class="language-switch"' in body and 'class="extras"' in body
        assert f'/downloads/Serdar-Armin-Sargut-Comp-Card-{code.upper()}.pdf' in body
        assert body.count('hreflang=') == 27
        for other in L:
            assert f'hreflang="{LANG_TAG[other]}" href="https://serdararminsargut.com/casting-card/{other}"' in body
        assert 'hreflang="x-default" href="https://serdararminsargut.com/casting-card/tr"' in body
        assert "durumuallasargut" not in body and "Duru" not in body
        assert not re.search(r"(?:tel:|\+90|gmail\.com)", body, re.I)
    print("SERDAR_26_RELEASE_SOURCE_STATIC_PASS 26/26")


if __name__ == "__main__":
    main()
