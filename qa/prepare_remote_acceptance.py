import hashlib,json,os
from pathlib import Path
root=Path('dist')
def manifest():return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
expected=json.loads(Path('qa/remote_expected_preview.json').read_text())
assert manifest()==expected,'Accepted 229 preview files changed'
assert not (root/'_qa').exists()
(root/'_qa').mkdir()
for src,dst in [('remote_acceptance.html','index.html'),('acceptance.js','acceptance.js')]:
 text=Path('qa',src).read_text();assert text.count('__SOURCE_SHA__')==1
 (root/'_qa'/dst).write_text(text.replace('__SOURCE_SHA__',os.environ['GITHUB_SHA']))
assert '/_qa/' not in (root/'sitemap.xml').read_text()
final=manifest();assert len(final)==231
Path('work-evidence').mkdir(exist_ok=True)
record={'project':'Serdar','preview_source':os.environ['GITHUB_SHA'],'application_source':'b704a17fd27ab8b7e44871cacb36d5ce29149f19',
 'site_files_identical_to_accepted':229,'preview_total_files':231,'preview_total_bytes':sum(p.stat().st_size for p in root.rglob('*') if p.is_file()),
 'only_extra_paths':['_qa/index.html','_qa/acceptance.js'],'qa_in_sitemap':False,'csp_unchanged':True,'main_or_settings_write':False,'sha256':final}
Path('work-evidence/remote-qa-build.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print('REMOTE_QA_PREPARED',json.dumps({k:v for k,v in record.items() if k!='sha256'}))
