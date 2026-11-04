"""Rasterise board-layer PDFs (exported by kicad-cli) cropped to the board outline.

python render_pcb.py <in.pdf> <out.png> <px_per_mm> [x0 y0 x1 y1 board-mm crop] [--mirror]
Board-mm crop uses KiCad board coordinates; with --mirror the x axis is mirrored about the page centre.
"""
import sys

import fitz

PT_PER_MM = 72 / 25.4


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mirror = "--mirror" in sys.argv
    pdf, out, ppm = args[0], args[1], float(args[2])
    doc = fitz.open(pdf)
    page = doc[0]
    if len(args) >= 7:
        x0, y0, x1, y1 = map(float, args[3:7])
    else:
        x0, y0, x1, y1 = 44.0, 36.8, 104.5, 148.5
    W = page.rect.width
    if mirror:
        # kicad mirrors around the page centre for -m plots
        X0 = W - x1 * PT_PER_MM
        X1 = W - x0 * PT_PER_MM
    else:
        X0, X1 = x0 * PT_PER_MM, x1 * PT_PER_MM
    clip = fitz.Rect(X0, y0 * PT_PER_MM, X1, y1 * PT_PER_MM)
    pix = page.get_pixmap(matrix=fitz.Matrix(ppm / PT_PER_MM, ppm / PT_PER_MM), clip=clip)
    pix.save(out)
    print(out, pix.width, pix.height)


if __name__ == "__main__":
    main()
