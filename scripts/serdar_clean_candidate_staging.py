#!/usr/bin/env python3
"""Produce Serdar clean visual PDF candidates only into a detached staging artifact.

Does NOT replace production PDFs or modify original watermarked files.
Requires an explicitly test-only input manifest and performs structural/pixel/link checks.
"""
import argparse, hashlib, json
from pathlib import Path
import fitz

LANGS=("TR","EN","AR","RU")
PREFIX="SERDAR_COMP_CARD_{}_LAYOUT_TEST_20261103.pdf"
OUT_PREFIX="SERDAR_COMP_CARD_{}_CLEAN_CANDIDATE_NOT_PUBLISHED.pdf"
URI="https://serdararminsargut.com/"


def need(condition, detail):
    if not condition: raise AssertionError("SERDAR_CLEAN_STAGING_NO_GO: " + detail)


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def get_uri_links(page):
    return [(int(v.get('kind',-1)), v.get('uri'), tuple(round(float(x),2) for x in v.get('from',()))) for v in page.get_links() if v.get('uri')]


def make(input_dir, output_dir):
    a=input_dir.resolve(strict=True)
    b=output_dir.resolve()
    need(a.is_dir() and a!=b and a not in b.parents and b not in a.parents, "output must be independent from input directory")
    need(not a.is_symlink() and not b.is_symlink(), "symlinked path")
    need('dist' not in b.parts and 'public' not in b.parts and 'downloads' not in b.parts, "never write into deploy output")
    manifest_path=a/'SHA256_AND_TEST_RESULTS.json'
    need(manifest_path.is_file() and not manifest_path.is_symlink(),"test manifest missing")
    evidence=json.loads(manifest_path.read_text(encoding='utf-8'))
    need(evidence.get('project')=='SERDAR_ONLY' and evidence.get('test_only') is True and evidence.get('approved_for_production') is False,"only original test-only preview inputs accepted")
    expected={x['lang']:x for x in evidence['results']}
    need(set(expected)==set(LANGS),"expected four languages only")
    b.mkdir(parents=True, exist_ok=True)
    need(not any(b.iterdir()),"output must be empty")
    outputs=[]
    for lang in LANGS:
        original=a/PREFIX.format(lang)
        dest=b/OUT_PREFIX.format(lang)
        need(original.is_file() and not original.is_symlink(),f'{lang}: preview absent')
        need(digest(original)==expected[lang]['preview_sha256'],f'{lang}: preview SHA mismatch')
        src=fitz.open(original)
        try:
            need(len(src)==2 and src[1].rect.width>590 and src[1].rect.width<600,f'{lang}: A4 two-page source required')
            baseline_links=get_uri_links(src[1]);need(any(l[1]==URI for l in baseline_links),f'{lang}: portfolio URI absent')
            baseline_text_page1=src[0].get_text(); baseline_text_page2=src[1].get_text()
            need('SERDAR ARMIN' in baseline_text_page2 and 'SARGUT' in baseline_text_page2,f'{lang}: name footer absent')
            need('serdararminsargut.com' in baseline_text_page2,f'{lang}: URL footer absent')
            # Confine redaction to the small test stamp in the lower-right white-space area.
            # No images/graphics are affected; links are checked and restored if needed.
            src[1].add_redact_annot(fitz.Rect(389,793,559,818), fill=(9/255,9/255,9/255))
            src[1].apply_redactions(images=0, graphics=0, text=0)
            links_after=get_uri_links(src[1])
            for link in src[1].get_links():
                pass
            for kind,uri,rect in baseline_links:
                if (kind,uri,rect) not in links_after:
                    need(uri==URI and kind==fitz.LINK_URI,"unexpected lost link")
                    src[1].insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(rect),'uri':uri})
            metadata=src.metadata
            metadata['title']=f'Serdar Armin Sargut | {lang} Comp Card visual candidate - NOT PUBLISHED'
            metadata['subject']='Visual candidate only - NOT APPROVED for production'
            src.set_metadata(metadata)
            src.save(dest,garbage=3,deflate=True)
        finally:
            src.close()
        with fitz.open(original) as old, fitz.open(dest) as new:
            need(len(new)==2,f'{lang}: wrong page count')
            need(all(old[i].rect==new[i].rect for i in range(2)),f'{lang}: page geometry changed')
            need(old[0].get_text()==new[0].get_text(),f'{lang}: page 1 text changed')
            need(old[1].get_text().split('SERDAR ARMIN')[0]==new[1].get_text().split('SERDAR ARMIN')[0],f'{lang}: second page prior text changed')
            need('SERDAR ARMIN' in new[1].get_text() and 'SARGUT' in new[1].get_text(),f'{lang}: footer name missing')
            need('serdararminsargut.com' in new[1].get_text(),f'{lang}: footer URI missing')
            for i in range(2):
                need(len(old[i].get_images(full=True))==len(new[i].get_images(full=True)),f'{lang}: source image count changed')
                clip=old[i].rect if i==0 else fitz.Rect(0,0,old[i].rect.width,790)
                pix_old=old[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5),clip=clip,alpha=False)
                pix_new=new[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5),clip=clip,alpha=False)
                need(pix_old.samples==pix_new.samples,f'{lang}: original visible pixels changed at page {i+1}')
            after_links=get_uri_links(new[1]); need(set(after_links)==set(baseline_links),f'{lang}: URI link annotations changed')
            need('NOT PUBLISHED' not in new[1].get_text() and 'YAYINLANMADI' not in new[1].get_text() and 'НЕ ОПУБЛИКОВАНО' not in new[1].get_text(),f'{lang}: watermarked text remains')
            result={'language':lang,'source_sha256':digest(original),'clean_sha256':digest(dest),'page_count':2,'first_page_pixel_identity':'PASS','second_page_upper_pixel_identity':'PASS','link_annotations_preserved':'PASS','source_images_preserved':'PASS','published':False,'filename':dest.name,'size_bytes':dest.stat().st_size}
            outputs.append(result)
            print('SERDAR_CLEAN_STAGING_PDF_PASS '+json.dumps(result),flush=True)
    (b/'SERDAR_CLEAN_CANDIDATES_NO_PUBLISH_MANIFEST.json').write_text(json.dumps({'project':'SERDAR_ONLY','stage_only':True,'approved_for_production':False,'results':outputs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('SERDAR_CLEAN_CANDIDATES_STAGING_PASS 4/4, NO DEPLOY',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-dir',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    cfg=ap.parse_args()
    make(cfg.input_dir,cfg.output_dir)
