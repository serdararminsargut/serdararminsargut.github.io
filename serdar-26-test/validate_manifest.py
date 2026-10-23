#!/usr/bin/env python3
"""Offline guardrails for the Serdar-only 26-locale test draft."""
import json
from pathlib import Path

manifest = json.loads(Path(__file__).with_name("locale_manifest.json").read_text(encoding="utf-8"))

assert manifest["project"] == "SERDAR_ONLY"
assert manifest["status"] == "TEST_DRAFT_NOINDEX"
assert len(manifest["target_locales"]) == 26
assert len(set(manifest["target_locales"])) == 26
assert set(manifest["existing_live_home_locales"]).issubset(manifest["target_locales"])
assert set(manifest["existing_live_comp_card_locales"]).issubset(manifest["target_locales"])
assert any(
    "never a claim that serdar speaks that language" in rule.lower()
    for rule in manifest["editorial_rules"]
)
print("SERDAR_26_TEST_MANIFEST_PASS 26/26")
