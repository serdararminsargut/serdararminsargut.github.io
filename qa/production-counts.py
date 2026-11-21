"""Explain provider upload totals by comparing existing production baselines; GET only."""
import hashlib,json,os,re,urllib.request
from pathlib import Path
c=json.loads(Path('qa/production-verification-config.json').read_text())
assert os.environ['GITHUB_REF_NAME']==c['qa_branch']
account=os.environ['CF_ACCOUNT'];m=re.search(r'dash\.cloudflare\.com/([a-fA-F0-9]{32})',account)
if m:account=m[1]
assert re.fullmatch('[a-fA-F0-9]{32}',account)
def get(suffix):
    req=urllib.request.Request('https://api.cloudflare.com/client/v4/accounts/'+account+'/pages/projects/'+c['project']+suffix,headers={'Authorization':'Bearer '+os.environ['CF_TOKEN'],'Accept':'application/json'},method='GET')
    with urllib.request.urlopen(req,timeout=30) as r:d=json.load(r)
    assert d.get('success');return d['result']
p=get('');ident=p['canonical_deployment']['id']
assert p['production_branch']=='main'
result={'person':c['person'],'scope':'GET ONLY — prior/current provider upload log count comparison; no HTTP/visual/PDF/Lighthouse suite repeated','normal_bundle':c['normal_bundle'],'source_type':(p.get('source') or {}).get('type'),'project_build_config':{k:(p.get('build_config') or {}).get(k) for k in ('build_command','destination_dir','root_dir')},'production_unchanged_during_read':True,'snapshots':[]}
for label,deploy_id in [('previous',c['previous_production_id']),('current',ident)]:
    d=get('/deployments/'+deploy_id)
    md=d.get('deployment_trigger',{}).get('metadata',{})
    assert d['environment']=='production'
    if label=='current':assert md.get('commit_hash')==c['main']
    logs=get('/deployments/'+deploy_id+'/history/logs')
    lines=[str(x.get('line') or '') for x in (logs.get('data') or [])]
    text='\n'.join(lines)
    totals=[int(x) for x in re.findall(r'Uploading[^\n]*\(\s*\d+\s*/\s*(\d+)\s*\)',text,re.I)]
    # Only upload progress strings; never persist general logs or environment values.
    selected=[re.sub(r'\x1b\[[0-9;]*m','',line) for line in lines if re.search(r'Uploading.*\(\s*\d+\s*/\s*\d+\s*\)|Success! Uploaded',line,re.I)]
    result['snapshots'].append({'label':label,'deployment_id':deploy_id,'commit':md.get('commit_hash'),'created_on':d.get('created_on'),'status':d.get('latest_stage',{}).get('status'),'upload_progress_total':max(totals) if totals else None,'upload_progress_lines':selected[-6:],'file_inventory_exposed':False,'total_bytes':'ölçülemedi'})
previous,current=result['snapshots']
result['unchanged_provider_upload_total']=previous['upload_progress_total'] is not None and previous['upload_progress_total']==current['upload_progress_total']
result['result']='OBSERVED_SAME_TOTAL' if result['unchanged_provider_upload_total'] else 'NEEDS_INTERPRETATION'
Path('work-release-counts').mkdir(exist_ok=True)
Path('work-release-counts/provider-upload-count-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
