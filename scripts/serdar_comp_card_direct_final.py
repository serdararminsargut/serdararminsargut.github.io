#!/usr/bin/env python3
"""Four-language Serdar Comp Card final PDF design, candidate release only.

Takes the original locally-generated PDFs and writes finalized PDFs to an
independent directory. Does not alter the source, deploy, or contact a server.
The production workflow may copy files only AFTER this exits successfully.
"""
import argparse
import hashlib
import json
from pathlib import Path

import fitz

LANGS=("TR","EN","AR","RU")
BASE="Serdar-Armin-Sargut-Comp-Card-{}.pdf"
SITE="https://serdararminsargut.com/"
COPY={
 "TR":("PORTFÖY ÖZETİ","Oyunculuk  /  Katalog  /  Spor ve yaşam tarzı",("OYUNCULUK","KATALOG","SPOR / YAŞAM TARZI")),
 "EN":("PORTFOLIO OVERVIEW","Acting  /  Catalog  /  Sport & lifestyle",("ACTING","CATALOG","SPORT / LIFESTYLE")),
 "AR":("ملخص الملف الفني","التمثيل  /  الكتالوج  /  الرياضة وأسلوب الحياة",("التمثيل","الكتالوج","الرياضة / أسلوب الحياة")),
 "RU":("ОБЗОР ПОРТФОЛИО","Актёрство  /  Каталог  /  Спорт и стиль",("АКТЁРСТВО","КАТАЛОГ","СПОРТ / СТИЛЬ"))
}
SUBJECT={
 "TR":"Çocuk oyuncu ve model portföyü; profesyonel iletişim veli yönetimindedir.",
 "EN":"Child actor and model portfolio; professional contact managed by parent or guardian.",
 "AR":"ملف أعمال ممثل وعارض أزياء طفل؛ التواصل المهني بإشراف ولي الأمر.",
 "RU":"Портфолио юного актёра и модели; профессиональные контакты через родителей."
}
IVORY=(.94,.93,.90); GOLD=(.78,.67,.46); MUTED=(.65,.64,.63); BORDER=(.25,.22,.18)

def check(v,m):
    if not v: raise AssertionError("SERDAR_DIRECT_PDF_NO_GO: "+m)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def link_set(page):
    return sorted((int(z["kind"]),str(z.get("uri","")),
                   tuple(round(float(x),3) for x in z["from"]))
                  for z in page.get_links() if z.get("uri"))
def same_original_content(before,after,lang):
    check(len(before)==len(after)==2,lang+" page count")
    for i in (0,1):
        a,b=before[i],after[i]
        check(a.rect==b.rect,lang+" page geometry")
        check(len(a.get_images(full=True))==len(b.get_images(full=True)),lang+" image count")
        check(b.get_text().startswith(a.get_text()),lang+" original text")
        check(set(link_set(a)).issubset(set(link_set(b))),lang+" original links")
        clip=a.rect if i==0 else fitz.Rect(0,0,a.rect.width,500)
        pa=a.get_pixmap(matrix=fitz.Matrix(1.5,1.5),clip=clip,alpha=False)
        pb=b.get_pixmap(matrix=fitz.Matrix(1.5,1.5),clip=clip,alpha=False)
        check(pa.samples==pb.samples,lang+" original visual pixels")

def overlay(original,output,lang,reg,bold,naskh):
    values=COPY[lang]
    fr=fitz.Font(fontfile=str(reg)); fb=fitz.Font(fontfile=str(bold))
    css="@font-face{font-family:Naskh;src:url(NotoNaskhArabic-Regular.ttf)}body,span,p{font-family:Naskh;margin:0;padding:0}p{line-height:1.15}"
    archive=fitz.Archive(str(naskh.parent))
    with fitz.open(original) as d:
        check(len(d)==2 and all(abs(p.rect.width-595.3)<1 and abs(p.rect.height-841.9)<1 for p in d),
              lang+" requires 2 A4 pages")
        p=d[1]
        p.insert_font(fontname="sreg",fontfile=str(reg))
        p.insert_font(fontname="sbold",fontfile=str(bold))
        def label(x,y,s,size=11,color=IVORY,heavy=False):
            p.insert_text((x,y),s,fontname="sbold" if heavy else "sreg",
                          fontsize=size,color=color,overlay=True)
        def centered(y,s,size,color,heavy=False):
            font=fb if heavy else fr
            width=font.text_length(s,fontsize=size)
            check(width<517,lang+" title overflow")
            label((p.rect.width-width)/2,y,s,size,color,heavy)
        def rtl(rect,s,size=13,color=IVORY,align="right"):
            hexcolor="#{:02x}{:02x}{:02x}".format(*(round(v*255) for v in color))
            html=f'<p dir="rtl" style="direction:rtl;text-align:{align};font-size:{size}pt;color:{hexcolor}"><span>{s}</span></p>'
            spare,scale=p.insert_htmlbox(fitz.Rect(*rect),html,css=css,archive=archive,scale_low=1,overlay=True)
            check(spare>=0 and scale==1,lang+" Arabic text does not fit")
        p.draw_line((41,511),(554,511),color=GOLD,width=.9,overlay=True)
        if lang=="AR":
            rtl((293,523,553,547),values[0],14,GOLD)
            rtl((236,548,553,574),values[1],14)
        else:
            label(43,540,values[0],10,GOLD,True)
            label(43,562,values[1],11.5 if lang=="EN" else 10.5)
        chips=tuple(reversed(values[2])) if lang=="AR" else values[2]
        for (x,width),item in zip(((42,151),(200,151),(358,195)),chips):
            p.draw_rect(fitz.Rect(x,591,x+width,635),color=BORDER,fill=(.05,.047,.043),width=.9,overlay=True)
            if lang=="AR":
                rtl((x+5,600,x+width-5,630),item,12.4,GOLD,"center")
            else:
                size=10
                while fb.text_length(item,fontsize=size)>width-12 and size>=7.5:
                    size-=.5
                check(fb.text_length(item,fontsize=size)<width-10,lang+" chip overflow")
                label(x+(width-fb.text_length(item,fontsize=size))/2,618,item,size,GOLD,True)
        centered(704,"SERDAR ARMIN",35,IVORY,True)
        centered(751,"SARGUT",36,GOLD,True)
        p.draw_line((45,766),(550,766),color=BORDER,width=.7,overlay=True)
        centered(787,"serdararminsargut.com",10,MUTED)
        p.insert_link({"kind":fitz.LINK_URI,"from":fitz.Rect(189,773,407,797),"uri":SITE})
        d.set_metadata({"title":f"Serdar Armin Sargut | Comp Card | {lang}",
                        "author":"Serdar Armin Sargut Portfolio",
                        "subject":SUBJECT[lang],
                        "creator":"Serdar Armin Sargut Portfolio",
                        "producer":"Serdar Armin Sargut Portfolio",
                        "keywords":"Serdar Armin Sargut, actor, casting, child model, comp card"})
        d.save(output,garbage=4,deflate=True)
    with fitz.open(original) as old, fitz.open(output) as new:
        same_original_content(old,new,lang)
        check(any(link[1]==SITE for link in link_set(new[1])),lang+" website hyperlink")
        check(any(link[1].startswith("mailto:") for link in link_set(new[1])),lang+" parent contact hyperlink")
        for field in ("title","subject","author","creator","producer"):
            check(bool(new.metadata.get(field)),lang+" metadata missing "+field)
        for forbidden in ("NOT PUBLISHED","YAYINLANMADI","НЕ ОПУБЛИКОВАНО","TEST /"):
            check(forbidden not in new[1].get_text(),lang+" test text remains")

def run(root,out):
    root=root.resolve(strict=True); out=out.resolve()
    check(root.is_dir() and root!=out and root not in out.parents and out not in root.parents,"separate directory required")
    check(not root.is_symlink() and not out.is_symlink(),"symlink roots forbidden")
    check("dist" not in out.parts and "public" not in out.parts and "downloads" not in out.parts,
          "release candidate output cannot be a deploy folder")
    fonts=Path("/usr/share/fonts/truetype")
    reg=fonts/"dejavu/DejaVuSans.ttf"
    bold=fonts/"dejavu/DejaVuSans-Bold.ttf"
    arabic=fonts/"noto/NotoNaskhArabic-Regular.ttf"
    check(all(x.is_file() for x in (reg,bold,arabic)),"required fonts missing")
    originals={lang:root/"downloads"/BASE.format(lang) for lang in LANGS}
    check(all(p.is_file() and not p.is_symlink() for p in originals.values()),"source Comp Card PDF missing")
    out.mkdir(parents=True,exist_ok=True)
    check(not any(out.iterdir()),"output must start empty")
    src_checksums={lang:digest(p) for lang,p in originals.items()}
    results=[]
    for lang in LANGS:
        output=out/BASE.format(lang)
        overlay(originals[lang],output,lang,reg,bold,arabic)
        check(20000<output.stat().st_size<3000000,lang+" size too large")
        results.append({"language":lang,"filename":output.name,"sha256":digest(output),
                        "source_sha256":src_checksums[lang],"pages":2,"bytes":output.stat().st_size,
                        "staging_only":True})
    check(all(digest(originals[l])==src_checksums[l] for l in LANGS),"source was altered")
    (out/"SERDAR_DIRECT_PDF_RELEASE_CANDIDATE_MANIFEST.json").write_text(
       json.dumps({"project":"SERDAR_ONLY","production_approved":False,"deployed":False,"pdfs":results},
                  ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SERDAR_DIRECT_DESIGN_PDF_PREPROD_PASS 4/4, NO DEPLOY",flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    run(args.source_root,args.output_dir)
