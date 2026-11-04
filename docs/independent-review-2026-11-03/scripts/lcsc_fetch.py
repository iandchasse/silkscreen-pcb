"""Fetch LCSC datasheets by LCSC part code (product page -> datasheet.lcsc.com link).

python lcsc_fetch.py <out_dir> C123 C456 ...
Saves <out_dir>/lcsc_<code>.pdf and prints the datasheet URL used (for the Sources list).
"""
import os
import re
import subprocess
import sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def curl(url, out):
    subprocess.run(["curl.exe", "-s", "-L", "-A", UA, "--max-time", "90", "-o", out, url], check=False)


def main(out_dir, codes):
    os.makedirs(out_dir, exist_ok=True)
    for code in codes:
        page = os.path.join(out_dir, f"lcsc_{code}.html")
        curl(f"https://www.lcsc.com/product-detail/{code}.html", page)
        try:
            html = open(page, encoding="utf-8", errors="ignore").read()
        except FileNotFoundError:
            print(code, "NO PAGE")
            continue
        links = sorted(set(re.findall(r"datasheet\.lcsc\.com/datasheet/pdf/[0-9a-f]+\.pdf\?productCode=" + code + r"\b", html)))
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        title = title.group(1).strip()[:120] if title else ""
        if not links:
            print(code, "NO LINK", title)
            continue
        url = "https://" + links[0]
        pdf = os.path.join(out_dir, f"lcsc_{code}.pdf")
        curl(url, pdf)
        ok = open(pdf, "rb").read(5) == b"%PDF-" if os.path.exists(pdf) else False
        print(code, "OK" if ok else "FAIL", url, "|", title)
        os.remove(page)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
