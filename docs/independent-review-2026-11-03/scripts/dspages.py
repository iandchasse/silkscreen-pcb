"""Print selected pages of an extracted datasheet text compactly (short lines joined with ' | ').

python dspages.py <file.txt> <first_page> [last_page] [width]
"""
import re
import sys

path = sys.argv[1]
p0 = int(sys.argv[2])
p1 = int(sys.argv[3]) if len(sys.argv) > 3 else p0
width = int(sys.argv[4]) if len(sys.argv) > 4 else 160
if len(sys.argv) > 5:
    sys.stdout = open(sys.argv[5], "w", encoding="utf-8")
text = open(path, encoding="utf-8").read()
pages = re.split(r"\n=== page (\d+) ===\n", text)
# pages: ['', '1', text1, '2', text2, ...]
d = {int(pages[i]): pages[i + 1] for i in range(1, len(pages) - 1, 2)}
for p in range(p0, p1 + 1):
    if p not in d:
        continue
    lines = [l.strip() for l in d[p].splitlines() if l.strip()]
    out, cur = [], ""
    for l in lines:
        if len(cur) + len(l) + 3 > width:
            out.append(cur)
            cur = l
        else:
            cur = (cur + " | " + l) if cur else l
    if cur:
        out.append(cur)
    print(f"=== page {p} ===")
    print("\n".join(out))
