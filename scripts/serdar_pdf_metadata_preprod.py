#!/usr/bin/env python3
"""Serdar 4-language preproduction PDF metadata clean-up; isolated artifact only.
No Cloudflare, GitHub write, production dist mutation, network or deployment.
"""
import argparse
import fitz
import hashlib
import json
import re
from pathlib import Path

LANGS=('TR','EN','AR','RU')
TITLE='Serdar Armin Sargut | Comp Card | {}'
SUBJECTS={
 'TR':'Çocuk oyuncu ve model portföyü; profesyonel iletişim veli yönetimindedir.',
 'EN':'Child actor and model portfolio; contact managed by a parent or guardian.',
 'AR':'ملف أعمال ممثل وعارض أزياء طفل؛ التواصل المهني بإشراف ولي الأمر.',
 'RU':'Портфолио юного актёра и модели; профессиональные контакты под управлением родителей.',
}
def require(ok,reason):
 if not ok: raise AssertionError('SERDAR_METADATA_PREPROD_NO_GO: '+reason)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def links(page):
 return sorted((int(x['kind']),str(x.get('uri','')),tuple(round(float(v),3) for v in x.get('from',()))) for x in page.get_links())

def run(input_root,output_root):
 a=input_root.resolve(strict=True); b=output_root.resolve()
 require(a.is_dir() and a!=b and a not in b.parents and b not in a.parents,'input/output isolation')
 require(not a.is_symlink() and not b.is_symlink(),'symlink root')
 require(not any(x in b.parts for x in ('dist','public','downloads')),'output may not be a deploy path')
 manifest=a/'SERDAR_CLEAN_CANDIDATES_NO_PUBLISH_MANIFEST.json'
 require(manifest.is_file() and not manifest.is_symlink(),'clean-source manifest missing')
 source=json.loads(manifest.read_text(encoding='utf-8'))
 require(source.get('project')=='SERDAR_ONLY' and source.get('stage_only') is True and source.get('approved_for_production') is False,'source must be staging-only')
 known={x['language']:x for x in source['results']}
 require(set(known)==set(LANGS),'unexpected source locale list')
 b.mkdir(parents=True,exist_ok=True)
 require(not any(b.iterdir()),'output must be empty')
 results=[]
 for lang in LANGS:
  old=a/known[lang]['filename']
  new=b/f'SERDAR_COMP_CARD_{lang}_FINAL_PREPROD_NOT_PUBLISHED.pdf'
  require(old.is_file() and not old.is_symlink() and sha(old)==known[lang]['clean_sha256'],lang+': source SHA incorrect')
  meta={'title':TITLE.format(lang),'author':'Serdar Armin Sargut Portfolio','subject':SUBJECTS[lang],
        'keywords':'Serdar Armin Sargut, casting, actor, child model, portfolio, comp card',
        'creator':'Serdar Armin Sargut Portfolio','producer':'Serdar Armin Sargut Portfolio'}
  with fitz.open(old) as doc:
   require(len(doc)==2,lang+': input not two pages')
   doc.set_metadata(meta)
   doc.save(new,garbage=4,deflate=True)
  with fitz.open(old) as before,fitz.open(new) as after:
   require(len(after)==len(before)==2,lang+': page count')
   require(all(before[i].rect==after[i].rect for i in range(2)),lang+': page geometry')
   require(all(before[i].get_text()==after[i].get_text() for i in range(2)),lang+': text modified')
   require(all(links(before[i])==links(after[i]) for i in range(2)),lang+': URI or clickable region changed')
   require(all(len(before[i].get_images(full=True))==len(after[i].get_images(full=True)) for i in range(2)),lang+': photos altered')
   for key,value in meta.items():require(after.metadata.get(key)==value,lang+': metadata '+key)
   require(not re.search('test|not published|not approved|candidate|preview',str(after.metadata),re.I),lang+': test metadata')
   require(any(x[1]=='https://serdararminsargut.com/' for x in links(after[1])),lang+': website link')
   require(any(x[1].startswith('mailto:') for x in links(after[1])),lang+': email link')
   for page_number in range(2):
    pm1=before[page_number].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
    pm2=after[page_number].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
    require(pm1.samples==pm2.samples,lang+': visible image changed page '+str(page_number+1))
  results.append({'language':lang,'filename':new.name,'sha256':sha(new),'bytes':new.stat().st_size,'pages':2,'metadata':'PASS','pixels':'PASS','links':'PASS','published':False})
  print('SERDAR_FINAL_PREPROD_METADATA_PASS '+json.dumps(results[-1]),flush=True)
 (b/'SERDAR_METADATA_PREPROD_SHA256.json').write_text(json.dumps({'project':'SERDAR_ONLY','publish_authorized':False,'published':False,'results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 require(len(results)==4,'missing language')
 print('SERDAR_METADATA_PREPROD_CI_PASS: 4/4 PDFs, pixels, URI, metadata; NO DEPLOY',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('--input-root',type=Path,required=True)
 ap.add_argument('--output-root',type=Path,required=True)
 x=ap.parse_args()
 run(x.input_root,x.output_root)
