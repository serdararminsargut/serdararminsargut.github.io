#!/usr/bin/env python3
"""Offline safety and structure gate for the Serdar-only 26-locale candidate."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "serdar-26-candidate" / "casting-card"
EXPECTED = ("tr","en","ru","ar","az","de","fr","es","kk","uz","ky","tk","it","pt-br","uk","pl","bg","el","sr-latn","sq","fa","ur","hi","zh-hans","ja","ko")
RTL = {"ar", "fa", "ur"}
required_assets = ("serdar-armin-sargut-cocuk-oyuncu-model-portre-1536-v12-1-20260826.webp","serdar-armin-sargut-bej-takim-tam-boy.webp","serdar-armin-sargut-gri-takim-yelek.webp","serdar-armin-sargut-futbol-spor-portre.webp","serdar-armin-sargut-beyaz-tisort-lifestyle.webp","portfolio-qr.png")

def main() -> None:
    found = tuple(sorted(p.stem for p in PAGES.glob("*.html")))
    assert found == tuple(sorted(EXPECTED)), (found, EXPECTED)
    for code in EXPECTED:
        body = (PAGES / f"{code}.html").read_text(encoding="utf-8")
        assert f'<html lang="{code}"' in body
        assert (f'<html lang="{code}" dir="rtl"' in body) == (code in RTL)
        assert 'name="robots" content="noindex,nofollow,noarchive"' in body
        assert f'https://serdararminsargut.com/casting-card/{code}' in body
        assert "TEST PREVIEW · NOINDEX" in body
        assert "info@serdararminsargut.com" in body
        assert "Serdar Armin Sargut" in body and "162" in body and "2014" in body
        assert "Duru" not in body and "durumuallasargut" not in body
        assert not re.search(r"(?:tel:|\+90|serdararminsargut@gmail\.com)", body, re.I)
        for asset in required_assets:
            assert asset in body, (code, asset)
        for target in EXPECTED:
            assert f'href="./{target}.html"' in body, (code, target)
    print("SERDAR_26_CANDIDATE_STATIC_PASS 26/26")

if __name__ == "__main__":
    main()
