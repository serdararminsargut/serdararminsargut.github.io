#!/usr/bin/env python3
"""Read-only static SEO checks. No network calls, deployment, or source mutations."""
import argparse
import json
import os
from datetime import date
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET

class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.canonicals = []
        self.alternates = {}
        self.robots = []
        self.meta = {}
        self.json_blocks = []
        self._json = False
        self._buffer = []
        self.images_missing_dimensions = 0

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "html":
            self.lang = (data.get("lang") or "").lower().replace("_", "-")
        if tag == "link":
            rel = (data.get("rel") or "").lower().split()
            href = (data.get("href") or "").strip()
            if "canonical" in rel:
                self.canonicals.append(href)
            if "alternate" in rel and data.get("hreflang"):
                lang = data["hreflang"].lower()
                if lang in self.alternates and self.alternates[lang] != href:
                    self.alternates[lang] = None
                else:
                    self.alternates[lang] = href
        if tag == "meta":
            key = (data.get("name") or data.get("property") or "").lower()
            content = (data.get("content") or "").strip()
            if key and content:
                self.meta[key] = content
            if key == "robots":
                self.robots.append(content.lower())
        if tag == "script" and (data.get("type") or "").lower() == "application/ld+json":
            self._json = True
            self._buffer = []
        # Dynamic lightbox placeholders without src/srcset are not renderable images.
        if tag == "img" and (data.get("src") or data.get("srcset")) and (not data.get("width") or not data.get("height")):
            self.images_missing_dimensions += 1

    def handle_data(self, data):
        if self._json:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._json:
            self.json_blocks.append("".join(self._buffer))
            self._json = False

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--root", required=True)
    cli.add_argument("--origin", required=True)
    args = cli.parse_args()
    root = Path(args.root).resolve()
    origin = args.origin.rstrip("/")
    errors, warnings = [], []
    sitemap_path = root / "sitemap.xml"
    if not sitemap_path.is_file():
        raise SystemExit("FAIL: sitemap.xml not found")
    try:
        tree = ET.parse(sitemap_path)
    except ET.ParseError as exc:
        raise SystemExit(f"FAIL: malformed sitemap.xml: {exc}")
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    if tree.getroot().tag != ns + "urlset":
        errors.append("Sitemap root is not the standard urlset")
    urls = []
    for node in tree.getroot().findall(ns + "url"):
        url = (node.findtext(ns + "loc") or "").strip()
        lastmod = (node.findtext(ns + "lastmod") or "").strip()
        urls.append(url)
        if not lastmod:
            errors.append(f"{url}: sitemap lastmod missing")
        else:
            try:
                date.fromisoformat(lastmod)
            except ValueError:
                errors.append(f"{url}: sitemap lastmod must be ISO date: {lastmod}")
    if not urls:
        errors.append("Sitemap contains no URLs")
    if len(urls) != len(set(urls)):
        errors.append("Sitemap contains duplicate URLs")
    pages = {}

    def page_file(url):
        p = urlsplit(url)
        if p.scheme != "https" or p.netloc != urlsplit(origin).netloc:
            return None
        path = unquote(p.path)
        if ".." in Path(path).parts:
            return None
        entry = root / path.lstrip("/")
        candidates = [entry / "index.html"] if path.endswith("/") else [
            entry / "index.html", entry.with_suffix(".html"), entry]
        for candidate in candidates:
            if candidate.is_file() and candidate.resolve().is_relative_to(root):
                return candidate
        return None

    def page(url):
        if url in pages:
            return pages[url]
        file = page_file(url)
        if file is None:
            return None
        parser = Head()
        try:
            parser.feed(file.read_text(encoding="utf-8"))
            parser.close()
        except (UnicodeError, ValueError) as exc:
            errors.append(f"{url}: invalid HTML encoding/parser input: {exc}")
        pages[url] = parser
        if len(parser.canonicals) != 1 or parser.canonicals[0] != url:
            errors.append(f"{url}: canonical must be unique and self-referencing; found {parser.canonicals}")
        if not parser.lang:
            errors.append(f"{url}: missing <html lang>")
        if any("noindex" in value for value in parser.robots):
            errors.append(f"{url}: indexed sitemap page contains noindex")
        for key in ("description", "og:title", "og:description", "twitter:card"):
            if not parser.meta.get(key):
                errors.append(f"{url}: missing required metadata {key}")
        for pos, data in enumerate(parser.json_blocks, 1):
            try:
                parsed = json.loads(data)
                if not isinstance(parsed, (dict, list)):
                    raise ValueError("JSON-LD root must be an object or array")
            except (ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{url}: JSON-LD block {pos} invalid: {exc}")
        if parser.images_missing_dimensions:
            warnings.append(f"{url}: {parser.images_missing_dimensions} images lack width/height")
        return parser

    for url in urls:
        if not url.startswith(origin + "/") or "#" in url or "?" in url:
            errors.append(f"Invalid sitemap URL: {url}")
            continue
        if page(url) is None:
            errors.append(f"Sitemap URL has no local HTML source: {url}")

    for url in urls:
        source = pages.get(url)
        if not source:
            continue
        for language, destination in source.alternates.items():
            if destination is None:
                errors.append(f"{url}: duplicate conflicting hreflang {language}")
                continue
            if not destination or not destination.startswith(origin + "/"):
                errors.append(f"{url}: hreflang {language} points away from canonical origin: {destination}")
                continue
            target = page(destination)
            if target is None:
                errors.append(f"{url}: hreflang {language} target missing: {destination}")
                continue
            if language == "x-default":
                continue
            if target.lang != language and not target.lang.startswith(language + "-"):
                errors.append(f"{url}: hreflang {language} target has html lang={target.lang}: {destination}")
            if source.lang and target.alternates.get(source.lang) != url:
                errors.append(f"{url}: hreflang {language} not reciprocated by {destination}")
        if source.alternates and source.lang not in source.alternates:
            errors.append(f"{url}: missing self hreflang for {source.lang}")
        if source.alternates and source.alternates.get(source.lang) != url:
            errors.append(f"{url}: self hreflang does not match canonical")

    robots_file = root / "robots.txt"
    if not robots_file.is_file():
        errors.append("robots.txt missing")
    else:
        robots = robots_file.read_text(encoding="utf-8")
        if f"Sitemap: {origin}/sitemap.xml" not in robots:
            errors.append("robots.txt production sitemap declaration missing")
        if "Disallow: /" in robots:
            errors.append("Production robots.txt contains blanket Disallow: /")

    def summary(label, values, limit=40):
        print(f"{label}: {len(values)}")
        for value in values[:limit]:
            print(f"  - {value}")
        if len(values) > limit:
            print(f"  ... and {len(values)-limit} more")

    print(f"Audited {len(urls)} sitemap URLs; {len(pages)} parsed HTML pages")
    summary("FAIL", errors)
    summary("WARNING (report only)", warnings)
    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as out:
            out.write(f"## Static SEO audit\n\nChecked **{len(urls)}** sitemap URLs.\n\n")
            out.write(f"**Failures:** {len(errors)} · **Image dimension warnings:** {len(warnings)}\n\n")
            for item in errors[:60]:
                out.write(f"- FAIL: `{item}`\n")
            for item in warnings[:15]:
                out.write(f"- WARN: `{item}`\n")
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
