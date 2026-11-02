import importlib.util
import tempfile
from pathlib import Path
import json
import hashlib
from xml.etree import ElementTree as ET
p=Path(__file__).with_name('hugoblox_freeze_verified_main.py')
spec=importlib.util.spec_from_file_location('freeze',p); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def treehash(root):
    data='\n'.join(f'{f.relative_to(root).as_posix()}\t{hashlib.sha256(f.read_bytes()).hexdigest()}' for f in sorted(root.rglob('*')) if f.is_file())
    return hashlib.sha256(data.encode()).hexdigest()
for project,nfile,nurl in [('SERDAR',174,95),('DURU',128,36)]:
 with tempfile.TemporaryDirectory() as tmp:
    t=Path(tmp);site=t/'site';site.mkdir()
    base=m.PROJECTS[project]['site']
    new=['/rehber/','/rehber/post/']+[f'/rehber/post/example-{i}/' for i in range(3)]
    legacy=[f'/old-{i}/' for i in range(nurl-5)]
    if project=='SERDAR':legacy[0]='/rehber/korfez-cocuk-model-portfoyu/';legacy[1]='/rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/'
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'
    root=ET.Element('{'+ns+'}urlset')
    for u in legacy+new:ET.SubElement(ET.SubElement(root,'{'+ns+'}url'),'{'+ns+'}loc').text=base+u
    ET.ElementTree(root).write(site/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    (site/'robots.txt').write_text('User-agent: *\nAllow: /\n')
    (site/'_headers').write_text('/*\n  Referrer-Policy: strict-origin-when-cross-origin\n')
    for u in new:
        d=site/u.lstrip('/');d.mkdir(parents=True);(d/'index.html').write_text('<h1>Test fixture</h1>')
    if project=='SERDAR':
        for lang in ('TR','EN','AR','RU'):
            d=site/'downloads';d.mkdir(exist_ok=True);(d/f'Serdar-Armin-Sargut-Comp-Card-{lang}.pdf').write_bytes(b'%PDF-1.4\n%synthetic')
    else:
        for lang in range(26):
            p=site/'comp-card'/f'l{lang}'/'index.html';p.parent.mkdir(parents=True);p.write_text('Test only')
            d=site/'comp-card/pdf';d.mkdir(exist_ok=True,parents=True);(d/f'l{lang}.pdf').write_bytes(b'%PDF-1.4\n%synthetic')
    for i in range(nfile-len([x for x in site.rglob('*') if x.is_file()])):
        q=site/'padding'/f'{i:03d}.txt';q.parent.mkdir(exist_ok=True);q.write_text('fixture')
    assert len(list(x for x in site.rglob('*') if x.is_file()))==nfile
    receipt={'project':project,'status':'PRODUCTION_MAIN_MIRROR_NO_DEPLOY_PASS','production_root_source':'GITHUB_MAIN_PRODUCTION_BUILD_NOT_STAGING_BASELINE','production_published':False,'production_publish_authorized':False,'merged_sitemap_urls':nurl,'new_verified_guide_files':12,'new_hugo_html':5,'final_file_count':nfile,'output_root_sha256':treehash(site),'original_production_files_preserved':nfile-12}
    rp=t/'receipt.json';rp.write_text(json.dumps(receipt))
    hp=t/'http.json';hp.write_text(json.dumps({'project':project,'status':'LOCAL_PRODUCTION_MIRROR_HTTP_ACCEPTANCE_PASS'}))
    if project=='DURU':
        pp=t/'parity.json';pp.write_text(json.dumps({'project':'DURU','status':'DURU_26_PDF_RENDER_PARITY_PASS'}))
    else:pp=None
    m.freeze(project,site,rp,hp,t/'frozen',pp)
    # Any unexpected original change invalidates the release receipt and must be blocked.
    (site/'padding/000.txt').write_text('TAMPERED')
    try:m.freeze(project,site,rp,hp,t/'reject',pp)
    except RuntimeError as e:assert 'filetree SHA mismatch' in str(e)
    else:raise AssertionError('TAMPER not rejected')
    # Approval is NEVER a valid state for a prepublication freeze.
    (site/'padding/000.txt').write_text('fixture')
    receipt['production_publish_authorized']=True;rp.write_text(json.dumps(receipt))
    try:m.freeze(project,site,rp,hp,t/'reject-2',pp)
    except RuntimeError as e: assert 'prohibit publication' in str(e)
    else:raise AssertionError('Publication flag not rejected')
print('SYNTHETIC_FREEZE_TEST_PASS: Serdar 174 files, Duru 128 files, both tamper and publish flag fail-closed')