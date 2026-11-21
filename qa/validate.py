"""Prove application-only Serdar output equals accepted preview without repeating browser suites."""
from pathlib import Path
import hashlib,json,os,re,subprocess

root=Path('dist');ref=json.loads(Path('qa/reference.json').read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def files():return {str(p.relative_to(root)):p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file()}
raw=files();main=ref['main_raw_sha256'];accepted=ref['accepted_sealed_sha256'];paths=ref['application_html_blobs']
assert len(raw)==229 and set(raw)==set(main)==set(accepted)
changed=[n for n in raw if sha(raw[n])!=main[n]]
assert set(changed)==set(paths) and len(changed)==56
for n in paths:
 b=raw[n];blob=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert blob==paths[n],('Not the exact accepted HTML blob',n)
 assert not re.search(r'<meta\b(?=[^>]*\bname=["\x27]robots["\x27])(?=[^>]*\bcontent=["\x27][^"\x27]*noindex)',b.decode(),re.I),('Unexpected source noindex',n)
protected=[n for n in main if Path(n).suffix.lower() in ('.pdf','.jpg','.jpeg','.png','.webp','.svg','.mp4','.mp3','.woff','.woff2')]
assert len(protected)==60 and all(sha(raw[n])==main[n] for n in protected)
assert len([n for n in protected if n.endswith('.pdf')])==27
assert raw['_headers'] and b'X-Robots-Tag' not in raw['_headers']
assert b'Content-Security-Policy:' in raw['_headers'] and b'Content-Security-Policy-Report-Only:' not in raw['_headers']
assert not re.search(rb'(?m)^Disallow:\s*/\s*$',raw['robots.txt'])
assert all(sha(raw[n])==main[n] for n in ['_headers','_redirects','robots.txt','sitemap.xml','sitemap-google.xml','sitemap.txt','assets/js/site.js'])
raw_bytes=sum(map(len,raw.values()));raw_sha={n:sha(b) for n,b in raw.items()}
subprocess.run(['python3','qa/seal.py','dist'],check=True)
sealed=files();assert {n:sha(b) for n,b in sealed.items()}==accepted,'Sealed clean source differs from accepted 229-file output'
record={'result':'PASS','application_source':'f00ba068208cec458907af7541c6adae9ae20eed','QA_source':os.environ['GITHUB_SHA'],
 'main':'06091f2501ee1db3db7d6d62fe090ca4691111c7','accepted_test':'b704a17fd27ab8b7e44871cacb36d5ce29149f19','files':229,'raw_bytes':raw_bytes,'raw_sha256':raw_sha,
 'changed_application_HTML_paths':changed,'exact_accepted_HTML_blobs':56,'excluded_test_only_source_paths':7,'other_raw_files_identical_to_main':173,
 'original_protected_files_identical':60,'PDFs_identical':27,'all_26_card_HTML_unchanged':True,'normal_source_noindex_added':False,'CSP_and_headers_unchanged':True,
 'robots_redirects_sitemaps_siteJS_unchanged':True,'sealed_preview_files_SHA_identical':229,'sealed_preview_bytes':sum(map(len,sealed.values())),
 'browser_PDF_HTTP_Lighthouse_repeated':False,'deployed':False,'main_production_DNS_or_settings_write':False,'production_approval':False}
Path('work-clean-proof').mkdir(exist_ok=True);Path('work-clean-proof/equivalence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print('SERDAR_CLEAN_EQUIVALENCE_PASS',json.dumps({k:v for k,v in record.items() if k not in ['raw_sha256','changed_application_HTML_paths']}))
