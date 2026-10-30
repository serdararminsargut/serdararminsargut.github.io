#!/usr/bin/env python3
"""Fail-closed isolated acceptance for four languages, never production deploy."""
from pathlib import Path
import fitz,hashlib,json
from pypdf import PdfReader

results=[]
for lang in ("TR","EN","AR","RU"):
    p=Path("dist/downloads")/f"Serdar-Armin-Sargut-Comp-Card-{lang}.pdf"
    raw=p.read_bytes()
    assert raw.startswith(b"%PDF-") and 20000<len(raw)<1200000, f"{lang} invalid PDF size"
    reader=PdfReader(str(p))
    assert len(reader.pages)==1,f"{lang} A4 FAIL: {len(reader.pages)} pages"
    document=fitz.open(p)
    page=document[0]
    assert abs(page.rect.width-595)<3 and abs(page.rect.height-842)<3,f"{lang} wrong A4"
    text=page.get_text()
    assert all(value in text for value in ("Serdar","2014","162","37")),f"{lang} missing verified data"
    if lang=="AR":
        assert any("\u0600"<=c<="\u06ff" for c in text),"Arabic text missing"
    if lang=="RU":
        assert any("\u0400"<=c<="\u04ff" for c in text),"Cyrillic text missing"
    images=len(page.get_images(full=True))
    assert images>=5,f"{lang}: lost portfolio or QR image ({images})"
    boxes=[b for b in page.get_text("blocks") if b[6]==0]
    assert boxes,f"{lang}: no text"
    for b in boxes:
        assert 0<=b[0]<b[2]<=page.rect.width+1 and 0<=b[1]<b[3]<=page.rect.height+1, f"{lang}: clipped text {b[:4]}"
    preview=Path("dist/downloads")/f"Serdar-{lang}-A4-preview.png"
    page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(str(preview))
    item={"lang":lang,"pages":1,"a4":[round(page.rect.width,2),round(page.rect.height,2)],"images":images,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"lastTextY":round(max(b[3] for b in boxes),1)}
    results.append(item)
    print("SERDAR_FOUR_A4_PRINT_QA_PASS "+json.dumps(item),flush=True)
Path("dist/downloads/serdar-four-a4-preview-evidence.json").write_text(json.dumps({"scope":"ISOLATED_TEST_BRANCH","productionUntouched":True,"results":results},indent=2)+"\n")
print("SERDAR_ALL_FOUR_ONEPAGE_A4_PASS 4/4",flush=True)
