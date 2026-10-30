#!/usr/bin/env python3
"""Safe, isolated acceptance for Serdar Turkish single-A4 Comp Card prototype."""
from pathlib import Path
import fitz, hashlib, json
from pypdf import PdfReader
p=Path("dist/downloads/Serdar-Armin-Sargut-Comp-Card-TR.pdf")
raw=p.read_bytes()
assert raw.startswith(b"%PDF-")
doc=PdfReader(str(p))
assert len(doc.pages)==1,f"TR onepage FAIL: {len(doc.pages)} PDF pages"
page=fitz.open(p)[0]
assert abs(page.rect.width-595)<3 and abs(page.rect.height-842)<3,"A4 size mismatch"
text=page.get_text()
for required in ["Serdar","2014","162","37"]:
    assert required in text,f"TR missing required text {required}"
images=len(page.get_images(full=True))
assert images>=5,f"TR missing portfolio/QR images: {images}"
blocks=[b for b in page.get_text("blocks") if b[6]==0]
for b in blocks:
    assert 0<=b[0]<b[2]<=page.rect.width+1 and 0<=b[1]<b[3]<=page.rect.height+1,f"Text clipping {b[:4]}"
page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save("dist/downloads/Serdar-TR-A4-preview.png")
result={"lang":"TR","pages":1,"images":images,"a4":[round(page.rect.width,2),round(page.rect.height,2)],"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"lastTextY":round(max(b[3] for b in blocks),1)}
Path("dist/downloads/serdar-tr-a4-preview-evidence.json").write_text(json.dumps(result,indent=2))
print("SERDAR_TR_ONEPAGE_PRINT_QA_PASS "+json.dumps(result),flush=True)
