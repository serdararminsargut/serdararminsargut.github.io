#!/usr/bin/env python3
"""Four-language Serdar Comp Card visual QA, ISOLATED TEST ONLY; never deploy."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
import fitz

LANGS=("TR","EN","AR","RU")
BASE="Serdar-Armin-Sargut-Comp-Card-{}.pdf"
ORIGIN="https://serdararminsargut.com/"
COPY={
 "TR":("PORTFÖY ÖZETİ","Oyunculuk  /  Katalog  /  Spor ve yaşam tarzı",("OYUNCULUK","KATALOG","SPOR / YAŞAM TARZI"),"TEST / YAYINLANMADI"),
 "EN":("PORTFOLIO OVERVIEW","Acting  /  Catalog  /  Sport & lifestyle",("ACTING","CATALOG","SPORT / LIFESTYLE"),"TEST / NOT PUBLISHED"),
 "AR":("ملخص الملف الفني","التمثيل  /  الكتالوج  /  الرياضة وأسلوب الحياة",("التمثيل","الكتالوج","الرياضة / أسلوب الحياة"),"نسخة تجريبية / غير منشورة"),
 "RU":("ОБЗОР ПОРТФОЛИО","Актёрство  /  Каталог  /  Спорт и стиль",("АКТЁРСТВО","КАТАЛОГ","СПОРТ / СТИЛЬ"),"ТЕСТ / НЕ ОПУБЛИКОВАНО"),
}
IVORY=(.94,.93,.90); GOLD=(.78,.67,.46); MUTED=(.65,.64,.63); BORDER=(.25,.22,.18)

def check(ok,reason):
 if not ok: raise AssertionError("SERDAR_PDF_TEST_NO_GO: "+reason)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def compare(old,new):
 with fitz.open(old) as a, fitz.open(new) as b:
  check(len(a)==len(b)==2,"page count")
  for j in range(2):
   check(a[j].rect==b[j].rect and len(a[j].get_images(full=True))==len(b[j].get_images(full=True)),"geometry/images changed")
   check(b[j].get_text().startswith(a[j].get_text()),"original selectable text altered")
   clip=a[j].rect if j==0 else fitz.Rect(0,0,a[j].rect.width,500)
   x=a[j].get_pixmap(matrix=fitz.Matrix(1.5,1.5),clip=clip,alpha=False)
   y=b[j].get_pixmap(matrix=fitz.Matrix(1.5,1.5),clip=clip,alpha=False)
   check(x.width==y.width and x.height==y.height and x.samples==y.samples,"original visible pixels altered")
  check(any(link.get("uri")==ORIGIN for link in b[1].get_links()),"portfolio hyperlink")
  check("SERDAR ARMIN" in b[1].get_text(),"footer name")
  check(any(790<=block[1]<820 and len(block[4].strip())>=6 for block in b[1].get_text("blocks") if len(block)>4),"preview watermark")

def overlay(old,new,lang,reg,bold,naskh):
 shutil.copy2(old,new)
 values=COPY[lang]; f_reg=fitz.Font(fontfile=str(reg)); f_bold=fitz.Font(fontfile=str(bold))
 css="@font-face{font-family:Naskh;src:url(NotoNaskhArabic-Regular.ttf)}body,span,p{font-family:Naskh;margin:0;padding:0}p{line-height:1.15}"
 archive=fitz.Archive(str(naskh.parent))
 with fitz.open(new) as doc:
  check(len(doc)==2 and all(abs(p.rect.width-595.3)<1 and abs(p.rect.height-841.9)<1 for p in doc),"not two A4 pages")
  p=doc[1]
  p.insert_font(fontname="sreg",fontfile=str(reg))
  p.insert_font(fontname="sbold",fontfile=str(bold))
  def label(x,y,t,size=11,color=IVORY,heavy=False):
   p.insert_text((x,y),t,fontname="sbold" if heavy else "sreg",fontsize=size,color=color,overlay=True)
  def centered(y,t,size,color,heavy=False):
   font=f_bold if heavy else f_reg; width=font.text_length(t,fontsize=size)
   check(width<517,"footer overflow")
   label((p.rect.width-width)/2,y,t,size,color,heavy)
  def rtl(rect,t,size=13,color=IVORY,align="right"):
   hexc="#{:02x}{:02x}{:02x}".format(*(round(v*255) for v in color))
   html=f'<p dir="rtl" style="direction:rtl;text-align:{align};font-size:{size}pt;color:{hexc}"><span>{t}</span></p>'
   spare,scale=p.insert_htmlbox(fitz.Rect(*rect),html,css=css,archive=archive,scale_low=1,overlay=True)
   check(spare>=0 and scale==1,"Arabic glyph or box overflow")
  p.draw_line((41,511),(554,511),color=GOLD,width=.9,overlay=True)
  if lang=="AR":
   rtl((293,523,553,547),values[0],14,GOLD)
   rtl((236,548,553,574),values[1],14)
  else:
   label(43,540,values[0],10,GOLD,True)
   label(43,562,values[1],11.5 if lang=="EN" else 10.5)
  chips=tuple(reversed(values[2])) if lang=="AR" else values[2]
  for (x,w),v in zip(((42,151),(200,151),(358,195)),chips):
   p.draw_rect(fitz.Rect(x,591,x+w,635),color=BORDER,fill=(.05,.047,.043),width=.9,overlay=True)
   if lang=="AR": rtl((x+5,600,x+w-5,630),v,12.4,GOLD,"center")
   else:
    size=10
    while f_bold.text_length(v,fontsize=size)>w-12 and size>=7.5: size-=.5
    check(f_bold.text_length(v,fontsize=size)<w-10,"category label overflow")
    label(x+(w-f_bold.text_length(v,fontsize=size))/2,618,v,size,GOLD,True)
  centered(704,"SERDAR ARMIN",35,IVORY,True)
  centered(751,"SARGUT",36,GOLD,True)
  p.draw_line((45,766),(550,766),color=BORDER,width=.7,overlay=True)
  centered(787,"serdararminsargut.com",10,MUTED)
  if lang=="AR": rtl((397,797,553,816),values[3],9.5,MUTED)
  else:
   label(554-f_reg.text_length(values[3],fontsize=6.5),808,values[3],6.5,MUTED)
  p.insert_link({"kind":fitz.LINK_URI,"from":fitz.Rect(189,773,407,797),"uri":ORIGIN})
  doc.set_metadata({**doc.metadata,"title":f"Serdar Armin Sargut | {lang} Comp Card | TEST ONLY","subject":"Local preview only; no publishing authorization"})
  doc.saveIncr()
 compare(old,new)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source-root",required=True,type=Path)
 ap.add_argument("--output-dir",required=True,type=Path)
 z=ap.parse_args()
 root=z.source_root.resolve(); out=z.output_dir.resolve()
 check(root.is_dir() and root!=out and root not in out.parents and out not in root.parents,"output path must be isolated from static build")
 check(not root.is_symlink() and not out.is_symlink(),"symlink root forbidden")
 fontroot=Path("/usr/share/fonts/truetype")
 reg=fontroot/"dejavu/DejaVuSans.ttf"; bold=fontroot/"dejavu/DejaVuSans-Bold.ttf"; naskh=fontroot/"noto/NotoNaskhArabic-Regular.ttf"
 check(all(x.is_file() for x in (reg,bold,naskh)),"missing OS fonts")
 originals=[root/"downloads"/BASE.format(lang) for lang in LANGS]
 check(all(x.is_file() and not x.is_symlink() for x in originals),"missing approved source PDFs")
 out.mkdir(parents=True,exist_ok=True)
 check(not any(out.iterdir()),"output directory must start empty")
 result=[]
 for lang,old in zip(LANGS,originals):
  new=out/f"SERDAR_COMP_CARD_{lang}_LAYOUT_TEST_20261103.pdf"
  overlay(old,new,lang,reg,bold,naskh)
  result.append({"lang":lang,"pages":2,"original_sha256":sha(old),"preview_sha256":sha(new),"size":new.stat().st_size,"pdf":new.name,"published":False})
 report={"project":"SERDAR_ONLY","approved_for_production":False,"test_only":True,"main_untouched":True,"results":result}
 (out/"SHA256_AND_TEST_RESULTS.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("SERDAR_COMP_CARD_LAYOUT_TEST_PASS: 4 x 2-page A4, original pixels/text/images unchanged, NO DEPLOY",flush=True)
if __name__=="__main__": main()
