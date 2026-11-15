"""Seal local build output only. No network, publication or source mutation."""
import argparse,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('--csp-report-only',action='store_true');a=p.parse_args()
r=Path(a.root);assert r.name in ('public','dist') and r.is_dir() and not r.is_symlink()
assert not any(x.is_symlink() for x in r.rglob('*'))
header=r/'_headers';s=header.read_text();assert s.startswith('/*\n') and s.count('/*\n')==1
assert not re.search(r'(?im)^\s*X-Robots-Tag\s*:',s)
extra='  X-Robots-Tag: noindex, nofollow, noarchive\n'
if a.csp_report_only:
    assert 'Content-Security-Policy' not in s
    extra+="  Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; media-src 'self' blob:; frame-src https://www.youtube-nocookie.com https://www.youtube.com https://player.vimeo.com; connect-src 'self' https://www.google-analytics.com https://*.google-analytics.com https://cloudflareinsights.com; object-src 'none'; base-uri 'self'; form-action 'self' mailto:;\n"
header.write_text(s.replace('/*\n','/*\n'+extra,1))
for f in r.rglob('*.html'):
    s=f.read_text();s=re.sub(r'<meta\b(?=[^>]*\bname\s*=\s*["\']robots["\'])[^>]*>\s*','',s,flags=re.I)
    s,n=re.subn(r'<head\b[^>]*>',lambda m:m[0]+'\n<meta name="robots" content="noindex,nofollow,noarchive">',s,count=1,flags=re.I)
    assert n==1,f;f.write_text(s)
(r/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
print('SEALED_PREVIEW',len(list(r.rglob('*.html'))),'HTML; noindex response header; production canonical preserved; CSP reporting only',a.csp_report_only)
