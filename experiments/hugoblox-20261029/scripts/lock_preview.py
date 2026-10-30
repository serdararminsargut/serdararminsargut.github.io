#!/usr/bin/env python3
"""Lock a generated *isolated test* site against accidental search indexing.

Never run this script against a production build. Its purpose is to remove
placeholder SEO metadata from a non-indexed QA preview. Original sources are
not modified.
"""
from pathlib import Path
import re

out = Path('public')
if not out.is_dir():
    raise SystemExit('FAIL: Hugo did not create public/')


def scrub_metadata(html):
    # Hugo --minify may omit quotes around attribute values, hence tag-level
    # matching rather than patterns requiring quoted HTML attributes.
    def meta_filter(match):
        tag=match.group(0)
        if re.search(r'\bname\s*=\s*["\\\']?robots(?:["\\\']|\s|>)', tag, re.I):
            return ''
        if re.search(r'\b(?:name|property)\s*=\s*["\\\']?(?:og:url|og:image|twitter:url|twitter:image)(?:["\\\']|\s|>)', tag, re.I):
            return ''
        return tag
    def link_filter(match):
        tag=match.group(0)
        if re.search(r'\brel\s*=\s*["\\\']?canonical(?:["\\\']|\s|>)',tag,re.I):
            return ''
        if re.search(r'\bhref\s*=\s*[\"\']?https?://example\.invalid',tag,re.I):
            return ''
        return tag
    html=re.sub(r'<meta\b[^>]*>',meta_filter,html,flags=re.I)
    html=re.sub(r'<link\b[^>]*>',link_filter,html,flags=re.I)
    html=re.sub(r'<script\b(?=[^>]*\btype\s*=\s*["\\\']?application/ld\+json(?:["\\\']|\s|>))[^>]*>[\s\S]*?</script>', '',html,flags=re.I)
    match=re.search(r'</head\s*>',html,flags=re.I)
    if not match:
        raise ValueError('missing head closing tag')
    html=html[:match.start()]+'<meta name="robots" content="noindex,nofollow,noarchive">\n'+html[match.start():]
    # Disable social-share actions on unpublished previews; their targets
    # point at the fake build origin and must never be shared.
    html=re.sub(r'<a\b(?=[^>]*\bid\s*=\s*[\"\']?share-link-[a-z0-9_-]+)[^>]*>[\s\S]*?</a>', '', html, flags=re.I)
    head=html.split('</head>',1)[0]
    if 'example.invalid' in head.lower():
        raise ValueError('unexpected placeholder reference in head')
    if 'example.invalid' in html.lower():
        raise ValueError('unexpected fake preview URL anywhere in HTML')
    return html

count=0
for p in out.rglob('*.html'):
    try:
        original = p.read_text(encoding='utf-8')
        if re.search(r'<meta\b[^>]*http-equiv\s*=\s*[\"\']?refresh', original, re.I) and 'example.invalid' in original.lower().split('</head>',1)[0]:
            p.unlink()  # Drop preview-only redirect pointing to fake origin
            continue
        p.write_text(scrub_metadata(original),encoding='utf-8')
    except ValueError as err:
        raise SystemExit(f'FAIL {p}: {err}')
    count+=1

# An unpublished preview needs neither discoverable RSS/sitemap nor links to a
# deliberately invalid build origin; production sitemap generation is untouched.
removed_feeds=0
for p in out.rglob('*.xml'):
    p.unlink()
    removed_feeds+=1
for p in out.rglob('*.html'):
    html = p.read_text(encoding='utf-8')
    html = re.sub(r'<link\b(?=[^>]*\btype\s*=\s*[\"\']?application/rss\+xml(?:[\"\']|\s|>))[^>]*>', '', html, flags=re.I)
    p.write_text(html,encoding='utf-8')

(out/'robots.txt').write_text('User-agent: *\nDisallow: /\n', encoding='utf-8')
(out/'_headers').write_text('/*\n  X-Robots-Tag: noindex, nofollow\n  Cache-Control: no-store\n', encoding='utf-8')
print(f'PASS: {count} preview HTML protected, {removed_feeds} feeds removed, no deploy')
