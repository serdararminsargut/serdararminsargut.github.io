"""Only GET provider metadata; no settings/DNS mutations. Fail closed before preview."""
import argparse,hashlib,json,os,re,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('phase',choices=['before','resolve','after']);p.add_argument('--project',required=True);p.add_argument('--repo',required=True);p.add_argument('--base',required=True);p.add_argument('--branch',required=True);p.add_argument('--production-id',required=True);a=p.parse_args()
assert a.branch.startswith('test/work-seo-') and os.environ['GITHUB_REF_NAME']==a.branch
account=os.environ['CF_ACCOUNT'];m=re.search(r'dash\.cloudflare\.com/([a-fA-F0-9]{32})',account)
if m:account=m[1]
assert re.fullmatch('[a-fA-F0-9]{32}',account)
token=os.environ['CF_TOKEN'];assert token
def get(path,gh=False):
    url=('https://api.github.com/repos/'+a.repo if gh else 'https://api.cloudflare.com/client/v4/accounts/'+account)+path
    req=urllib.request.Request(url,headers={'Authorization':'Bearer '+(os.environ['GH_TOKEN'] if gh else token),'Accept':'application/json','User-Agent':'Portfolio-Read-Only-Acceptance'},method='GET')
    with urllib.request.urlopen(req,timeout=30) as r:d=json.load(r)
    if not gh:assert d.get('success'), 'Cloudflare GET unsuccessful';d=d['result']
    return d
def snapshot():
    project=get('/pages/projects/'+a.project)
    assert project['name']==a.project and project['production_branch']=='main','Wrong project or production branch: refuse preview upload'
    canonical=project.get('canonical_deployment') or {}
    prod=canonical.get('id');assert prod and (a.production_id=='capture' or prod==a.production_id),'Production deployment changed externally; stop for rebase'
    main=get('/branches/main',gh=True)['commit']['sha'];assert main==a.base,'Main changed externally; stop for rebase'
    cfg={k:project.get(k) for k in ('production_branch','build_config','source','deployment_configs','domains')}
    cfg_hash=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
    return {'project':a.project,'production_branch':'main','main_sha':main,'production_deployment_id':prod,'production_commit':canonical.get('deployment_trigger',{}).get('metadata',{}).get('commit_hash'),'config_sha256':cfg_hash}
Path('work-evidence').mkdir(exist_ok=True)
if a.phase=='before':
    s=snapshot();Path('work-evidence/provider-before.json').write_text(json.dumps(s,indent=2));print('PREVIEW_TARGET_GUARD',json.dumps(s))
elif a.phase=='after':
    s=snapshot();old=json.loads(Path('work-evidence/provider-before.json').read_text());assert s==old,'Production metadata changed during preview work'
    Path('work-evidence/provider-after.json').write_text(json.dumps(s,indent=2));print('PRODUCTION_UNCHANGED',json.dumps(s))
    # The broader Access settings review is deliberately last and GET-only.
    access={'result':'NOT VERIFIED','policy_verified':False}
    try:
        apps=get('/access/apps?per_page=100');matches=[]
        for app in apps:
            if a.project not in json.dumps({k:app.get(k) for k in ('name','domain','destinations')}):continue
            policies=get('/access/apps/'+app['id']+'/policies?per_page=100')
            matches.append({'name':app.get('name'),'domain':app.get('domain'),'policies':[{'name':p.get('name'),'decision':p.get('decision'),'include_rule_count':len(p.get('include') or [])} for p in policies]})
        access.update(app_count=len(apps),matching_apps=matches)
        if matches:access['result']='POLICY SUMMARY READ; rule membership not disclosed or inferred'
    except Exception as e:access['error_type']=type(e).__name__;access['http_status']=getattr(e,'code',None)
    Path('work-evidence/access-readonly.json').write_text(json.dumps(access,indent=2));print('ACCESS_READONLY',json.dumps(access))
else:
    d=get('/pages/projects/'+a.project+'/deployments?env=preview&per_page=25')
    matches=[x for x in d if x.get('environment')=='preview' and x.get('deployment_trigger',{}).get('metadata',{}).get('branch')==a.branch and x.get('deployment_trigger',{}).get('metadata',{}).get('commit_hash')==os.environ['GITHUB_SHA'] and x.get('latest_stage',{}).get('status')=='success']
    assert matches,'No successful exact branch/SHA preview deployment'
    x=matches[0];s={'project':a.project,'environment':x['environment'],'branch':a.branch,'commit_sha':os.environ['GITHUB_SHA'],'deployment_id':x['id'],'url':x['url'],'created_on':x['created_on'],'status':x['latest_stage']['status']}
    Path('work-evidence/preview.json').write_text(json.dumps(s,indent=2));print('EXACT_PREVIEW',json.dumps(s))
    with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('url='+x['url']+'\n')
