"""Portable fail-closed SEO release freezer regression, isolated local fixtures only."""
import hashlib
import json
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from hugoblox_freeze_verified_main import PROJECTS, freeze
from hugoblox_seo_discovery_bridge import CONFIG, main as bridge_main

NS='{http://www.sitemaps.org/schemas/sitemap/0.9}'

def write(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(data,str):path.write_text(data,encoding='utf-8')
    else:path.write_bytes(data)

def jwrite(path,data):path.write_text(json.dumps(data),encoding='utf-8')

def fhash(root):
    return hashlib.sha256('\n'.join(f'{f.relative_to(root).as_posix()}\t{hashlib.sha256(f.read_bytes()).hexdigest()}'
                   for f in sorted(root.rglob('*')) if f.is_file()).encode()).hexdigest()

def base_fixture(project,base):
    c=CONFIG[project]; n=PROJECTS[project]['count']; total=PROJECTS[project]['urls']; origin=c['origin']
    homepage=('<html lang="tr"><head><title>Fixture</title><link rel="canonical" href="'
              +origin+'/"/></head><body><h1>Fixture</h1><footer>'+c['needle']+'</footer></body></html>')
    write(base/'index.html',homepage)
    write(base/'robots.txt','User-agent: *\nAllow: /\n')
    write(base/'_headers','/*\n  Referrer-Policy: same-origin\n')
    new=['/rehber/','/rehber/post/']+[f'/rehber/post/example-{i}/' for i in range(3)]
    old=[f'/existing-{i}/' for i in range(total-5)]
    if project=='SERDAR':old[:2]=['/rehber/korfez-cocuk-model-portfoyu/','/rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/']
    sitemap=ET.Element(NS+'urlset')
    for route in old+new:
        ET.SubElement(ET.SubElement(sitemap,NS+'url'),NS+'loc').text=origin+route
    (base/'sitemap.xml').write_bytes(ET.tostring(sitemap,encoding='utf-8'))
    for route in new:write(base/route.lstrip('/')/'index.html','<html><h1>Guide</h1></html>')
    if project=='SERDAR':
        write(base/'casting-card/tr.html','<html>Card</html>')
        for lang in ('TR','EN','AR','RU'):
            write(base/f'downloads/Serdar-Armin-Sargut-Comp-Card-{lang}.pdf',b'%PDF-1.4\nsynthetic fixture')
    else:
        for i in range(26):
            lang=('tr' if i==0 else 'ur' if i==1 else 'ko' if i==2 else f'l{i}')
            write(base/f'comp-card/{lang}/index.html','<html>Comp Card</html>')
            write(base/f'comp-card/pdf/{lang}.pdf',b'%PDF-1.4\nsynthetic fixture')
    count=len([f for f in base.rglob('*') if f.is_file()])
    assert n>=count, (project,n,count)
    for i in range(n-count):write(base/f'padding/{i:03d}.txt','synthetic')
    assert len([f for f in base.rglob('*') if f.is_file()])==n

for project in ('SERDAR','DURU'):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);main=root/'main';main.mkdir()
        base_fixture(project,main)
        config=PROJECTS[project]
        report={'project':project,'status':'PRODUCTION_MAIN_MIRROR_NO_DEPLOY_PASS',
          'production_root_source':'GITHUB_MAIN_PRODUCTION_BUILD_NOT_STAGING_BASELINE',
          'production_published':False,'production_publish_authorized':False,
          'merged_sitemap_urls':config['urls'],'new_verified_guide_files':12,'new_hugo_html':5,
          'final_file_count':config['count'],'output_root_sha256':fhash(main),
          'original_production_files_preserved':config['count']-12}
        rp=root/'receipt.json';jwrite(rp,report)
        hp=root/'http.json';jwrite(hp,{'project':project,'status':'LOCAL_PRODUCTION_MIRROR_HTTP_ACCEPTANCE_PASS'})
        pp=root/'pdf.json' if project=='DURU' else None
        if pp:jwrite(pp,{'project':project,'status':'DURU_26_PDF_RENDER_PARITY_PASS'})
        bridge=root/'bridge.json';candidate=root/'candidate'
        bridge_main(project,main,candidate,bridge)
        qa={'project':project,'status':'SEO_DISCOVERY_MOBILE_QA_PASS','production_published':False,
            'results':[{'width':w,'result':'PASS','link_height':44,'destination':'/rehber/',
                        'horizontal_overflow':False,'h1':1} for w in (360,390,430,1280)]}
        qap=root/'mobile.json';jwrite(qap,qa)
        manifest=freeze(project,candidate,rp,hp,root/'frozen',pp,
                        prebridge_root=main,seo_bridge_receipt=bridge,seo_mobile_qa=qap)
        assert manifest['variant']=='SEO_DISCOVERY_LINK_FINAL_CANDIDATE'
        assert manifest['total_files']==config['count']
        assert manifest['seo_changed_paths']==['index.html']
        assert manifest['production_published'] is False
        # Unapproved mobile QA must fail before any output is written.
        qa['results'][0]['result']='FAIL';jwrite(qap,qa)
        try:freeze(project,candidate,rp,hp,root/'reject-mobile',pp,
                   prebridge_root=main,seo_bridge_receipt=bridge,seo_mobile_qa=qap)
        except RuntimeError as e:assert 'SEO mobile QA contains failure' in str(e)
        else:raise AssertionError(project+': fake QA accepted')
        qa['results'][0]['result']='PASS';jwrite(qap,qa)
        (candidate/'index.html').write_text((candidate/'index.html').read_text()+'\n<!-- tamper -->')
        try:freeze(project,candidate,rp,hp,root/'reject-homepage',pp,
                   prebridge_root=main,seo_bridge_receipt=bridge,seo_mobile_qa=qap)
        except RuntimeError as e:assert 'SEO homepage change differs' in str(e)
        else:raise AssertionError(project+': extra homepage content accepted')
print('SEO_FINAL_FREEZE_GATE_SELFTEST_PASS: both projects, total 302 files, checksum, publish flags, mobile QA tamper and unauthorized HTML tamper rejected')