"""Compare built artifacts, with explicit preview-only HTML/header exceptions."""
import argparse,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('baseline');p.add_argument('candidate');p.add_argument('--project',required=True);a=p.parse_args()
b=Path(a.baseline);c=Path(a.candidate);assert b.is_dir() and c.is_dir()
def manifest(r):return {str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(r.rglob('*')) if f.is_file()}
bm,cm=manifest(b),manifest(c);assert bm.keys()==cm.keys(),'Artifact paths changed'
protected=[n for n in bm if Path(n).suffix.lower() in ('.pdf','.jpg','.jpeg','.png','.webp','.svg','.mp4','.mp3','.woff','.woff2')]
assert all(bm[n]==cm[n] for n in protected),'Protected asset bytes changed'
pdfs=[n for n in protected if n.endswith('.pdf')]
assert len(pdfs)>=26,'Expected at least the 26 protected language PDFs'
if a.project=='serdar':
    lines=Path('scripts/serdar-comp-card-sha256-20261107.txt').read_text().splitlines()
    assert len(lines)==26,'Language PDF manifest count changed'
    for line in lines:
        expected,name=line.split(None,1);name=name.strip().lstrip('*')
        assert bm.get(name)==expected and cm.get(name)==expected,'Approved language PDF changed: '+name
else:
    assert len(pdfs)==26,'Duru PDF inventory changed'
def body(s):return s.split('</head>',1)[1]
htmls=[n for n in bm if n.endswith('.html')]
link_map=json.loads(Path('scripts/work-seo-link-replacements.json').read_text()) if a.project=='serdar' and Path('scripts/work-seo-link-replacements.json').exists() else {}
def approved_before(n):
    s=(b/n).read_text()
    for old,new in link_map.get(n,{}).items():
        s=re.sub(r'(\bhref\s*=\s*)(?:(["\'])'+re.escape(old)+r'\2|'+re.escape(old)+r'(?=[\s>]))',lambda m:m[1]+(m[2] or '')+new+(m[2] or ''),s)
    return s
assert all(body(approved_before(n))==body((c/n).read_text()) for n in htmls),'HTML body changed outside verified href replacements'
if a.project=='duru':
    for n in htmls:
        def normalize(s):
            s=re.sub(r'<meta\b(?=[^>]*\bname\s*=\s*["\']robots["\'])[^>]*>\s*','',s,flags=re.I)
            return re.sub(r'>\s+<','><',s)
        assert normalize((b/n).read_text())==normalize((c/n).read_text()),'Unexpected Duru head change: '+n
s={'project':a.project,'baseline_files':len(bm),'candidate_files':len(cm),'baseline_bytes':sum(f.stat().st_size for f in b.rglob('*') if f.is_file()),'candidate_bytes':sum(f.stat().st_size for f in c.rglob('*') if f.is_file()),'protected_files':len(protected),'pdfs_sha256_identical':len(pdfs),'html_bodies_preserved_except_verified_hrefs':len(htmls),'approved_href_pages':len(link_map),'changed_paths':[n for n in bm if bm[n]!=cm[n]],'baseline_sha256':bm,'candidate_sha256':cm}
Path('work-evidence').mkdir(exist_ok=True);Path('work-evidence/preservation.json').write_text(json.dumps(s,indent=2));print('PRESERVATION',json.dumps({k:v for k,v in s.items() if not k.endswith('sha256')}))
