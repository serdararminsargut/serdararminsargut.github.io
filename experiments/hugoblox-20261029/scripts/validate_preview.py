#!/usr/bin/env python3
"""Strict QA checks for generated noindex *test preview* only."""
from pathlib import Path
import re
root=Path('public')
person=Path('site_identity.txt').read_text(encoding='utf-8').strip().lower()
slugs={
  'serdar':['cocuk-giyim-e-ticaret-cekimlerinde-portfoy-secimi','spor-giyim-ayakkabi-katalog-fotograflari','cocuk-oyuncu-casting-sunum-dosyasi'],
  'duru':['tiyatro-deneyiminden-kamera-onu-oyunculuguna','cocuk-oyuncu-self-tape-dosya-duzeni','genc-oyuncu-showreel-sahne-ve-ekran-secimi']
}
assert person in slugs, 'FAIL: unknown test identity'
files=list(root.rglob('*.html'))
assert len(files)>=4, f'FAIL: only {len(files)} HTML files'
for slug in slugs[person]:
    assert (root/'post'/slug/'index.html').is_file(),f'FAIL: missing article {slug}'
for p in files:
    s=p.read_text(encoding='utf-8')
    head=s.lower().split('</head>',1)[0]
    assert '<html' in s.lower() and '</html' in s.lower(), f'FAIL HTML {p}'
    assert len(re.findall(r'<meta\s+name="robots"\s+content="noindex,nofollow,noarchive"', head,flags=re.I))==1, f'FAIL robots count {p}'
    assert 'example.invalid' not in s.lower(), f'FAIL placeholder reference {p}'
    assert not re.search(r'<link\b[^>]*\brel\s*=\s*["\']?canonical(?:["\']|\s|>)', head,re.I),f'FAIL canonical in preview {p}'
    assert not re.search(r'<meta\b[^>]*\bproperty\s*=\s*["\']?og:image(?:["\']|\s|>)', head,re.I),f'FAIL unapproved OG in preview {p}'
    assert not re.search(r'<script\b[^>]*\btype\s*=\s*["\']?application/ld\+json(?:["\']|\s|>)',head,re.I), f'FAIL placeholder JSON-LD {p}'
assert (root/'robots.txt').read_text(encoding='utf-8')=='User-agent: *\nDisallow: /\n'
assert 'X-Robots-Tag: noindex, nofollow' in (root/'_headers').read_text(encoding='utf-8')
assert not list(root.rglob('*.xml')), 'FAIL: preview RSS/sitemap remains'
print(f'PASS: {person} {len(files)} HTML: all slugs + strict noindex, no placeholder head tags, no preview RSS/sitemap')
