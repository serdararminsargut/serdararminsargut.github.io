"""Compare built artifacts, with explicit preview-only HTML/header exceptions."""
import argparse,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('baseline');p.add_argument('candidate');p.add_argument('--project',required=True);a=p.parse_args()
b=Path(a.baseline);c=Path(a.candidate);assert b.is_dir() and c.is_dir()
def manifest(r):return {str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(r.rglob('*')) if f.is_file()}
bm,cm=manifest(b),manifest(c);assert bm.keys()==cm.keys(),'Artifact paths changed'
protected=[n for n in bm if Path(n).suffix.lower() in ('.pdf','.jpg','.jpeg','.png','.webp','.svg','.mp4','.mp3','.woff','.woff2')]
assert all(bm[n]==cm[n] for n in protected),'Protected asset bytes changed'
pdfs=[n for n in protected if n.endswith('.pdf')];assert len(pdfs)==26,'Expected 26 protected PDFs'
def body(s):return s.split('</head>',1)[1]
htmls=[n for n in bm if n.endswith('.html')]
assert all(body((b/n).read_text())==body((c/n).read_text()) for n in htmls),'HTML body changed'
if a.project=='duru':
    for n in htmls:
        def normalize(s):
            s=re.sub(r'<meta\b(?=[^>]*\bname\s*=\s*["\']robots["\'])[^>]*>\s*','',s,flags=re.I)
            return re.sub(r'>\s+<','><',s)
        assert normalize((b/n).read_text())==normalize((c/n).read_text()),'Unexpected Duru head change: '+n
s={'project':a.project,'baseline_files':len(bm),'candidate_files':len(cm),'baseline_bytes':sum(f.stat().st_size for f in b.rglob('*') if f.is_file()),'candidate_bytes':sum(f.stat().st_size for f in c.rglob('*') if f.is_file()),'protected_files':len(protected),'pdfs_sha256_identical':len(pdfs),'html_bodies_identical':len(htmls),'changed_paths':[n for n in bm if bm[n]!=cm[n]],'baseline_sha256':bm,'candidate_sha256':cm}
Path('work-evidence').mkdir(exist_ok=True);Path('work-evidence/preservation.json').write_text(json.dumps(s,indent=2));print('PRESERVATION',json.dumps({k:v for k,v in s.items() if not k.endswith('sha256')}))
