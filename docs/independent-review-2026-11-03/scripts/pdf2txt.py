"""Extract text from datasheet PDFs (one .txt per PDF with '=== page N ===' markers) for searching.

python pdf2txt.py <dir>
"""
import glob
import os
import sys

import fitz

for pdf in glob.glob(os.path.join(sys.argv[1], "*.pdf")):
    txt = pdf[:-4] + ".txt"
    if os.path.exists(txt) and os.path.getmtime(txt) > os.path.getmtime(pdf):
        continue
    try:
        doc = fitz.open(pdf)
    except Exception as e:  # noqa: BLE001
        print("FAIL", pdf, e)
        continue
    with open(txt, "w", encoding="utf-8") as f:
        for i, p in enumerate(doc):
            f.write(f"\n=== page {i + 1} ===\n")
            f.write(p.get_text())
    print(os.path.basename(pdf), doc.page_count, "pages")
