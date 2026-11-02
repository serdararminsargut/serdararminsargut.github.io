#!/usr/bin/env python3
"""NON-DEPLOY / NON-MUTATING production mirror adapter for HugoBlox guides.

Use the real main-commit production output as the authoritative baseline.
Overlay only the pinned and previously verified 5 HugoBlox HTML pages plus
fingerprinted CSS, JS and media into a new isolated static root. Preserve
all old baseline bytes except the XML sitemap(s) being appended. Fail closed.
Never runs git, deploy, Wrangler, Cloudflare, DNS or production writes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from xml.etree import ElementTree as ET
from verify_frozen_release_handoff import CONFIG, inspect_site, release_paths

NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def gate(condition, message):
    if not condition:
        raise AssertionError('NO_GO: ' + message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def filehashes(root):
    gate(root.is_dir(), f'not a directory: {root}')
    gate(not any(x.is_symlink() for x in root.rglob('*')), 'symlink in input')
    return {str(f.relative_to(root)): sha(f) for f in root.rglob('*') if f.is_file()}


def xml_urls(path):
    gate(path.is_file(), 'sitemap missing: ' + str(path))
    root = ET.parse(path).getroot()
    gate(root.tag == NS+'urlset','invalid sitemap namespace')
    urls = [el.text.strip() for el in root.findall(NS+'url/'+NS+'loc')]
    gate(len(urls) == len(set(urls)), 'duplicate sitemap URL')
    return root, urls


def allowlisted_new_files(project, frozen_root, baseline_root):
    allowed_html = set(release_paths(project))
    gate(len(allowed_html)==5,'expected exactly 5 new guide pages')
    base_guides = {'rehber/korfez-cocuk-model-portfoyu/index.html',
                   'rehber/turk-dunyasi-cocuk-oyuncu-model-portfoyu/index.html'} if project=='SERDAR' else set()
    original = filehashes(frozen_root)
    claimed = {p for p in original if p.startswith('rehber/')}
    gate(claimed >= allowed_html | base_guides, 'HugoBlox frozen root missing guide/old pages')
    new_set = claimed - base_guides
    gate(len(new_set)==12,'Unexpected HugoBlox guide files count: '+str(len(new_set)))
    gate(new_set >= allowed_html,'HugoBlox new HTML files missing')
    for path in new_set:
        if path in allowed_html:
            continue
        gate(bool(re.fullmatch(r'rehber/(?:css/[^/]+\.css|js/[^/]+\.js|media/[^/]+\.(?:png|jpg|webp|svg))',path)),
             'Unexpected file outside guide allowlist: '+path)
        gate(re.search(r'(?:\.[0-9a-f]{64}\.(?:css|js)|/icon_hu_[a-f0-9]+\.(?:png|jpg|webp))$',path) is not None,
             'Guide asset missing fingerprint: '+path)
    for path in new_set:
        gate(not (baseline_root/path).exists(), 'New guide would overwrite production main file: '+path)
    return new_set, base_guides, original


def merge(project, baseline, frozen, output):
    project=project.upper()
    gate(project in CONFIG,'unknown project')
    cfg=CONFIG[project]
    baseline=baseline.resolve();frozen=frozen.resolve();output=output.resolve()
    gate(baseline.is_dir() and frozen.is_dir(),'missing baseline or frozen')
    gate(not output.exists(),'output already exists')
    for a,b in [(baseline,output),(frozen,output),(output,baseline),(output,frozen)]:
        gate(a not in b.parents,'overlapping input/output dirs')
    originals=filehashes(baseline)
    gate('index.html' in originals and 'robots.txt' in originals,'production main baseline missing homepage or robots')
    gate(not any(s.strip().lower()=='disallow: /' for s in (baseline/'robots.txt').read_text().splitlines()),
         'production main robots disallow all')
    if '_headers' in originals:
        gate('X-Robots-Tag: noindex' not in (baseline/'_headers').read_text(),
             'production main header noindex')
    if project=='SERDAR':
        for locale in ('en','ar','ru','az','kk','uz','ky'):
            gate((baseline/locale/'index.html').is_file(),'existing locale missing: '+locale)
        for p in ('korfez-cocuk-model-portfoyu','turk-dunyasi-cocuk-oyuncu-model-portfoyu'):
            gate((baseline/'rehber'/p/'index.html').is_file(),'existing regional guide missing: '+p)
        for lang in ('TR','EN','AR','RU'):
            gate((baseline/f'downloads/Serdar-Armin-Sargut-Comp-Card-{lang}.pdf').is_file(),
                 'production workflow generated Comp Card PDF missing: '+lang)
            gate((baseline/f'downloads/Serdar-Armin-Sargut-Comp-Card-{lang}.pdf').read_bytes()[:5]==b'%PDF-',
                 'generated Comp Card PDF signature invalid: '+lang)
        gate('_headers' in originals and 'sitemap-google.xml' in originals,
             'Serdar production headers / secondary sitemap missing')
    else:
        htmls=list((baseline/'comp-card').glob('*/index.html'))
        pdfs=list((baseline/'comp-card').rglob('*.pdf'))
        gate(len(htmls)==len(pdfs)==26,'Duru 26 HTML / 26 PDF production baseline missing')
        gate(all(p.open('rb').read(5)==b'%PDF-' for p in pdfs),'invalid production PDF')
    base_sm,base_urls=xml_urls(baseline/'sitemap.xml')
    gate(len(base_urls)==cfg['baseline_urls'], 'unexpected production main sitemap URL count')
    gate(all(u.startswith(cfg['site']+'/') for u in base_urls),'unexpected sitemap domain')
    if project=='SERDAR':
        _, google_urls = xml_urls(baseline/'sitemap-google.xml')
        gate(google_urls==base_urls,'existing Google sitemap differs')
    new_paths,legacy_paths,frozen_files=allowlisted_new_files(project,frozen,baseline)
    gate(len(originals) >= 100,'suspiciously incomplete production root')
    # Exact production root always comes from the true pinned main production build.
    shutil.copytree(baseline,output)
    for p in sorted(new_paths):
        target=output/p
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(frozen/p,target)
        gate(sha(target)==frozen_files[p],'guide copied bytes mismatch: '+p)
    new_urls=[cfg['site']+'/'+path.removesuffix('index.html') for path in release_paths(project)]
    gate(not (set(new_urls) & set(base_urls)),'new sitemap URL already present in production')
    xml_files=['sitemap.xml','sitemap-google.xml'] if project=='SERDAR' else ['sitemap.xml']
    for xml_file in xml_files:
        tree, urls=xml_urls(output/xml_file)
        gate(urls==base_urls,'sitemap changed unexpectedly during copy')
        for u in new_urls:
            ET.SubElement(ET.SubElement(tree,NS+'url'),NS+'loc').text=u
        ET.register_namespace('',NS[1:-1])
        ET.ElementTree(tree).write(output/xml_file,encoding='utf-8',xml_declaration=True)
        _,after=xml_urls(output/xml_file)
        gate(after==base_urls+new_urls,'sitemap merge list mismatch')
    # Byte-exact preservation of EVERY preexisting production file outside XML.
    for path, h in originals.items():
        if path in xml_files:
            continue
        gate((output/path).is_file() and sha(output/path)==h,'existing production file changed: '+path)
    result=inspect_site(output,project)
    gate(result['new_routes']==5 and result['sitemap_urls']==cfg['urls'],'merged SEO failed')
    output_files=filehashes(output)
    gate(len(output_files)==len(originals)+len(new_paths),'file count inconsistent')
    overlap_differences=[p for p in sorted(set(originals)&set(frozen_files))
                         if p not in xml_files and originals[p]!=frozen_files[p]]
    report={
        'status':'PRODUCTION_MAIN_MIRROR_NO_DEPLOY_PASS',
        'project':project,'production_published':False,'production_publish_authorized':False,
        'production_root_source':'GITHUB_MAIN_PRODUCTION_BUILD_NOT_STAGING_BASELINE',
        'original_production_files_preserved':len(originals)-len(xml_files),
        'production_total_original_files':len(originals),
        'new_verified_guide_files':len(new_paths),'new_hugo_html':5,
        'final_file_count':len(output_files),'old_sitemap_urls':len(base_urls),
        'new_sitemap_urls':5,'merged_sitemap_urls':result['sitemap_urls'],
        'old_frozen_v_main_common_file_differences':len(overlap_differences),
        'old_frozen_v_main_difference_examples':overlap_differences[:25],
        'serdar_generated_comp_card_pdf_count':4 if project=='SERDAR' else None,
        'duru_locale_html_pdf_count':[26,26] if project=='DURU' else None,
        'output_root_sha256':hashlib.sha256('\n'.join(p+'\t'+h for p,h in sorted(output_files.items())).encode()).hexdigest(),
        'local_only':True,
    }
    receipt=output.parent/(project.lower()+'-production-main-mirror-receipt.json')
    receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(project+'_PRODUCTION_MAIN_MIRROR_NO_DEPLOY_PASS: '+str(len(originals))+' old + '+str(len(new_paths))+
          ' new files; '+str(len(base_urls))+'+5 URLs; all old non-sitemap bytes unchanged')
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--project',choices=CONFIG,required=True)
    ap.add_argument('--production-root',type=Path,required=True)
    ap.add_argument('--frozen-root',type=Path,required=True)
    ap.add_argument('--output-root',type=Path,required=True)
    args=ap.parse_args()
    merge(args.project,args.production_root,args.frozen_root,args.output_root)