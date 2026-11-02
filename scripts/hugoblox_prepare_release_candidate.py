#!/usr/bin/env python3
"""Build Serdar HugoBlox SEO release candidate OFFLINE from isolated staging.

No push, Cloudflare deployment, DNS changes, or modification of the original
portfolio. Never mix Duru data or Serdar's unapproved dynamic measurements.
"""
import argparse
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from xml.etree import ElementTree as ET

ORIGIN = "https://serdararminsargut.com"
SLUGS = (
    "cocuk-giyim-e-ticaret-cekimlerinde-portfoy-secimi",
    "spor-giyim-ayakkabi-katalog-fotograflari",
    "cocuk-oyuncu-casting-sunum-dosyasi",
)
PAGES = ("index.html", "post/index.html") + tuple(
    "post/" + slug + "/index.html" for slug in SLUGS
)
LEGACY = (
    "rehber/korfez-cocuk-model-portfoyu/index.html",
    "rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/index.html",
)
LOCALES = ("", "en", "ar", "ru", "az", "kk", "uz", "ky")
PREVIEW_ROBOTS = '<meta name="robots" content="noindex,nofollow,noarchive">'
PREVIEW_MARKER = '<meta name="x-preview-purpose" content="hugo-staging-noindex">'
PANEL_START = "<!-- PORTFOLIO_AUTOSYNC_PREVIEW_START -->"
PANEL_END = "<!-- PORTFOLIO_AUTOSYNC_PREVIEW_END -->"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


class HeadInfo(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.is_head = False
        self.is_title = False
        self.title = ""
        self.description = ""
        self.language = ""
        self.headings = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language = attrs.get("lang", "")
        if tag == "head":
            self.is_head = True
        if tag == "title" and self.is_head:
            self.is_title = True
        if tag == "meta" and self.is_head and attrs.get("name", "").lower() == "description":
            self.description = attrs.get("content", "")
        if tag == "h1":
            self.headings += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.is_title = False
        if tag == "head":
            self.is_head = False

    def handle_data(self, data):
        if self.is_title:
            self.title += data


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_old_social_meta(markup):
    keys = ("og:url", "og:title", "og:description", "og:type", "twitter:card")
    def edit(match):
        tag = match.group(0)
        if any(re.search(
            r'\b(?:name|property)\s*=\s*(?:"' + re.escape(key) + r'"|'
            + "'" + re.escape(key) + r"'" + r'|' + re.escape(key) + r')(?=\s|>|/)',
            tag, re.I
        ) for key in keys):
            return ""
        return tag
    return re.sub(r"<meta\b[^>]*>", edit, markup, flags=re.I)


def main(stage, out):
    stage, out = stage.resolve(), out.resolve()
    if out.exists() or out in stage.parents or stage in out.parents:
        raise SystemExit("BLOCKED: offline output must be a fresh directory separate from staging")
    source = stage / "rehber"
    assert (stage / "index.html").is_file() and (source / "index.html").is_file()
    assert all((source / name).is_file() for name in PAGES), "Missing Serdar guide article"
    assert "Disallow: /" in (stage / "robots.txt").read_text(encoding="utf-8")
    assert "X-Robots-Tag: noindex" in (stage / "_headers").read_text(encoding="utf-8")
    expected = set(PAGES)
    observed = {p.relative_to(source).as_posix()
                for p in source.rglob("*.html")
                if "portfoy-guncel" not in p.parts
                and "korfez-cocuk-model-portfoyu" not in p.parts
                and "turk-dunyasi-cocuk-oyuncu-model-portfoyu" not in p.parts}
    assert observed == expected, "Unexpected new article routes: " + str(sorted(observed ^ expected))
    baseline = {}
    for p in LEGACY:
        assert (stage / p).is_file(), "Existing Serdar regional guide missing: " + p
        baseline[p] = sha(stage / p)
    for locale in LOCALES:
        p = (locale + "/index.html").lstrip("/")
        assert (stage / p).is_file(), "Existing Serdar locale missing: " + p
        baseline[p] = sha(stage / p)
    assert (source / "portfoy-guncel/index.html").is_file(), "Staging diagnostics missing"
    source_hashes = {p: sha(source / p) for p in PAGES}

    out.mkdir(parents=True, exist_ok=False)
    target = out / "rehber"
    target.mkdir()
    shutil.copy2(source / "index.html", target / "index.html")
    for section in ("post", "css", "js", "media"):
        assert (source / section).is_dir(), "Missing compiled asset: " + section
        shutil.copytree(source / section, target / section)

    canonical_urls = []
    for name in PAGES:
        page = target / name
        s = page.read_text(encoding="utf-8")
        assert s.count(PREVIEW_ROBOTS) == 1, "Staging noindex missing or duplicated: " + name
        assert s.count(PREVIEW_MARKER) == 1, "Staging marker missing: " + name
        s = s.replace(PREVIEW_ROBOTS, "").replace(PREVIEW_MARKER, "")
        # The diagnostic panel must never exist in a release candidate.
        # Previously it was removed here; now it is blocked at staging build.
        assert PANEL_START not in s and PANEL_END not in s, (
            "Unapproved diagnostic panel included in Serdar release candidate: " + name
        )
        assert "example.invalid" not in s, "Fake preview origin leaked"
        assert "Duru Mualla Sargut" not in s, "Cross-profile identity leak"
        assert "Dil bağlantıları:" not in s, "Locale diagnostics visible"
        assert "Kaynak sitede gözlenen bilgiler" not in s, "Source diagnostics visible"
        assert "Bu sayfa yalnızca korumalı test" not in s, "Draft notice visible"
        s = strip_old_social_meta(s)
        parsed = HeadInfo()
        parsed.feed(s)
        assert parsed.language.lower().split("-")[0] == "tr", "Incorrect article lang: " + name
        assert parsed.headings >= 1, "No H1 in compiled page: " + name
        title, desc = parsed.title.strip(), parsed.description.strip()
        assert title and "Serdar" in title, "Unbranded title: " + name
        assert len(desc) >= 25, "Meta description missing: " + name
        route = "/rehber/" if name == "index.html" else "/rehber/" + name.removesuffix("index.html")
        canonical = ORIGIN + route
        canonical_urls.append(canonical)
        article = name.startswith("post/") and name != "post/index.html"
        structured = {
            "@context": "https://schema.org",
            "@type": "Article" if article else "CollectionPage",
            "headline" if article else "name": title,
            "description": desc,
            "url": canonical,
            "inLanguage": "tr",
            "isPartOf": {"@type": "WebSite", "url": ORIGIN + "/"},
        }
        if article:
            structured["author"] = {"@type": "Organization", "name": "Sargut Portfolio Team"}
            structured["mainEntityOfPage"] = {"@type": "WebPage", "@id": canonical}
        ldjson = json.dumps(structured, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
        tags = "\n".join((
            '<meta name="robots" content="index,follow">',
            '<link rel="canonical" href="' + escape(canonical, quote=True) + '">',
            '<meta property="og:type" content="' + ("article" if article else "website") + '">',
            '<meta property="og:url" content="' + escape(canonical, quote=True) + '">',
            '<meta property="og:title" content="' + escape(title, quote=True) + '">',
            '<meta property="og:description" content="' + escape(desc, quote=True) + '">',
            '<meta name="twitter:card" content="summary">',
            '<script type="application/ld+json">' + ldjson + '</script>',
        ))
        assert s.count("</head>") == 1, "Invalid head structure"
        s = s.replace("</head>", tags + "\n</head>", 1)
        assert s.count('rel="canonical"') == 1 and s.count('name="robots" content="index,follow"') == 1
        assert "noindex,nofollow,noarchive" not in s and PREVIEW_MARKER not in s
        if name == "index.html":
            for url in (ORIGIN + "/", ORIGIN + "/casting-card/tr.html",
                        "https://www.instagram.com/serdararminsargutt/"):
                assert url in s, "Missing approved casting/conversion link: " + url
        page.write_text(s, encoding="utf-8")

    assert not (target / "portfoy-guncel").exists(), "Unsafe diagnostic route copied"
    assert not (out / "robots.txt").exists() and not (out / "_headers").exists()
    assert not (out / "sitemap.xml").exists(), "Existing multilingual sitemap overwritten"
    assert {p: sha(stage / p) for p in baseline} == baseline, "Existing Serdar pages changed"
    assert {p: sha(source / p) for p in PAGES} == source_hashes, "Staging source was changed"
    ET.register_namespace("", NS)
    root = ET.Element("{" + NS + "}urlset")
    for url in canonical_urls:
        ET.SubElement(ET.SubElement(root, "{" + NS + "}url"), "{" + NS + "}loc").text = url
    ET.ElementTree(root).write(
        out / "rehber-sitemap-candidate.xml",
        encoding="utf-8", xml_declaration=True,
    )
    manifest = {
        "project": "SERDAR_ONLY",
        "status": "OFFLINE_CANDIDATE_NOT_PUBLISHED",
        "production_publish_authorized": False,
        "site_origin": ORIGIN,
        "new_guide_pages": 5,
        "new_articles": 3,
        "candidate_urls": canonical_urls,
        "existing_regional_pages_preserved_in_source": 2,
        "existing_locale_homepages_preserved_in_source": len(LOCALES),
        "serdar_26_locale_expansion_included": False,
        "diagnostic_routes_included": False,
        "sitemap_merged_into_production": False,
        "real_android_validation": "PENDING",
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "SERDAR_HUGOBLOX_OFFLINE_RELEASE_GATE_PASS: 5 canonical guide HTML, "
        "2 pre-existing regional guides + 8 locale homepages unchanged, "
        "dynamic diagnostics excluded; NO DEPLOY",
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    main(args.staging_root, args.output_root)
