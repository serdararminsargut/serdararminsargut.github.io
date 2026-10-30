#!/usr/bin/env python3
"""Stage an isolated HugoBlox export under /rehber/ without overwriting portfolio paths."""
import argparse
import re
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--site-root', required=True)
parser.add_argument('--hugo-root', required=True)
a = parser.parse_args()
site = Path(a.site_root).resolve()
hugo = Path(a.hugo_root).resolve()
assert site.is_dir() and hugo.is_dir()
assert (site / 'index.html').is_file(), 'Missing portfolio homepage'
assert (hugo / 'index.html').is_file()
assert (hugo / 'post/index.html').is_file()
assert len(list((hugo/'post').glob('*/index.html'))) == 3, 'Require exactly 3 draft posts'
mount = 'rehber'
root = site / mount
root.mkdir(exist_ok=True)
for name in ('index.html', 'post', 'css', 'js', 'media'):
    source = hugo / name
    assert source.exists(), 'Missing HugoBlox asset: '+name
    dest = root / name
    assert not dest.exists(), 'Fail closed: would overwrite existing content: '+str(dest)
    shutil.copytree(source, dest) if source.is_dir() else shutil.copy2(source, dest)

pattern = re.compile(r"""(?P<attr>\b(?:href|src|content)\s*=\s*)(?P<q>["'])(?P<url>/(?:post|css|js|media)/[^"']*|/)(?P=q)""", re.I)
new_pages = [root/'index.html'] + list((root/'post').rglob('*.html'))
for page in new_pages:
    body = page.read_text(encoding='utf-8')
    def change(m):
        url = m.group('url')
        return m.group('attr') + m.group('q') + ('/rehber/' if url=='/' else '/rehber'+url) + m.group('q')
    body = pattern.sub(change, body)
    assert '<meta name="robots" content="noindex,nofollow,noarchive">' in body, page
    assert 'example.invalid' not in body, page
    body = body.replace('</head>', '<meta name="x-preview-purpose" content="hugo-staging-noindex"></head>',1)
    page.write_text(body, encoding='utf-8')
for css in (root/'css').rglob('*.css'):
    body=css.read_text(encoding='utf-8')
    body=re.sub(r"""url\((['"]?)/(media|css|js)/""",
                lambda m:'url('+m.group(1)+'/rehber/'+m.group(2)+'/',body)
    css.write_text(body,encoding='utf-8')

# Critical: all Preview URLs, including original portfolio content, stay non-indexable.
(site/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
(site/'_headers').write_text('/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  Cache-Control: no-store\n',encoding='utf-8')
for sitemap in ('sitemap.xml','sitemap-google.xml'):
    (site/sitemap).unlink(missing_ok=True)

files=new_pages
assert len(files)==5, 'Expected homepage, post index, and 3 posts'
for page in files:
    body=page.read_text(encoding='utf-8')
    assert '/rehber/css/' in body or '/rehber/js/' in body
    assert not re.search(r"""(?:href|src)=["']/(?:post|css|js|media)/""",body),page
assert (site/'index.html').is_file(), 'Portfolio baseline not preserved'
print('PASS: HugoBlox mounted at /rehber/ with three articles; portfolio preserved; Preview noindex')
