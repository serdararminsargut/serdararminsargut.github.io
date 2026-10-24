#!/usr/bin/env python3
"""Verify PDFs produced from the isolated 26-language candidate, offline."""
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDFS = ROOT / "serdar-26-candidate" / "pdfs"
EXPECTED = ("tr","en","ru","ar","az","de","fr","es","kk","uz","ky","tk","it","pt-br","uk","pl","bg","el","sr-latn","sq","fa","ur","hi","zh-hans","ja","ko")

def main() -> None:
    for code in EXPECTED:
        file = PDFS / f"Serdar-Armin-Sargut-Comp-Card-{code.upper()}.pdf"
        assert file.is_file() and 20_000 < file.stat().st_size < 1_200_000, (code, "missing, tiny or too large for mobile delivery")
        raw = file.read_bytes()
        assert raw.startswith(b"%PDF-"), (code, "not a PDF")
        reader = PdfReader(str(file))
        assert 1 <= len(reader.pages) <= 2, (code, len(reader.pages))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        assert "Serdar" in text and "162" in text and "2014" in text, (code, "required profile facts missing")
    print("SERDAR_26_CANDIDATE_PDF_PASS 26/26")

if __name__ == "__main__":
    main()
