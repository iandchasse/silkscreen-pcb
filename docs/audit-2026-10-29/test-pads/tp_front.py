"""Front-side (F.Cu) test pads: check that each proposed pad keeps clear of the F.SilkS artwork, existing F.Mask openings,
the board edge and other-net copper, and draw a map. Usage (from the repository root):

    python docs/audit-2026-10-29/test-pads/tp_front.py [--pad 1.5]

It exports F.SilkS / F.Mask / Edge.Cuts with kicad-cli into a temporary folder, rasterises them at 20 px/mm, parses copper
from silkscreen_pcb.kicad_pcb, checks every pad in PADS and writes tp_front.png next to this script. Nets that do not
exist yet (LED_VIN, B-_SENSE, EINK_3V3) are checked against everything else. Re-run after the layout changes; KiCad DRC
is still the final word.
"""
import math, os, re, shutil, subprocess, sys, tempfile

import fitz
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
KICAD = r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe'
PCB = 'silkscreen_pcb.kicad_pcb'
PX = 20.0
PAD_R = float(sys.argv[sys.argv.index('--pad') + 1]) / 2 if '--pad' in sys.argv else 0.75
SILK_CLR = MASK_CLR = CU_CLR = 0.20
EDGE_CLR = 1.0
VIA_R, VIA_CLR = 0.30, 0.20

# label, net, x, y, connection
PADS = [
    ('TP6', 'LED_VIN', 46.5, 117.0, 'via in pad, ~2 mm B.Cu stub to the frontlight PTC / C12 node'),
    ('TP7', 'B-_SENSE', 85.4, 69.6, 'via in pad at the Q1 end of Rs (shares the Rs pocket)'),
    ('TP8', 'Net-(U5-OD)', 90.8, 71.5, 'via in pad, ~2.6 mm stub from Q1 pin 6 (crosses the OC trace on B.Cu: route on F.Cu)'),
    ('TP9', 'B-', 91.5, 68.65, 'via in pad on the B- trace'),
    ('TP10', 'SD_VDD', 63.65, 86.2, 'via in pad on the SD_VDD trace by C36'),
    ('TP11', 'USB_VBUS', 82.75, 96.75, 'on the existing F.Cu USB_VBUS trace'),
    ('TP12', 'P+', 90.5, 81.4, 'via in pad on the P+ B.Cu trace'),
    ('TP13', 'LDO_IN', 79.74, 96.66, 'on the existing F.Cu LDO_IN feed'),
    ('TP14', '3V3', 74.6, 85.8, 'on the existing F.Cu 3V3 trace near U3/C6'),
    ('TP15', '3V3', 91.3, 116.0, 'on the F.Cu 3V3 touch feed, upstream of the touch and e-paper PTCs'),
    ('TP16', 'EINK_3V3', 85.25, 115.5, 'via in pad on the new EINK_3V3 feed from the e-paper PTC to J2'),
    ('TP17', '/PIN_2', 92.25, 129.25, 'via in pad on the /PIN_2 B.Cu trace (0.3 mm from "Thank you all")'),
    ('TP18', 'GND', 82.25, 81.25, 'optional: on the F.Cu GND pour in the power cluster'),
]


def export(tmp):
    for layer in ('F.SilkS', 'F.Mask', 'Edge.Cuts'):
        subprocess.run([KICAD, 'pcb', 'export', 'pdf', '--layers', layer, '--mode-single', '--black-and-white',
                        '--output', os.path.join(tmp, layer + '.pdf'), PCB], check=True, capture_output=True)
    subprocess.run([KICAD, 'pcb', 'export', 'pdf', '--layers', 'F.Cu,F.SilkS,F.Mask,Edge.Cuts', '--mode-single',
                    '--output', os.path.join(tmp, 'front.pdf'), PCB], check=True, capture_output=True)


def raster(tmp, layer, px_per_mm=PX, gray=True):
    p = fitz.open(os.path.join(tmp, layer + '.pdf'))[0]
    k = px_per_mm * 25.4 / 72
    pm = p.get_pixmap(matrix=fitz.Matrix(k, k), colorspace=fitz.csGRAY if gray else fitz.csRGB)
    if not gray:
        return Image.frombytes('RGB', (pm.w, pm.h), pm.samples)
    return np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.h, pm.w) < 200


def copper():
    s = open(PCB, encoding='utf-8').read()
    netname = {m.group(1): m.group(2) for m in re.finditer(r'\(net (\d+) "([^"]*)"\)', s)}
    cu = {'F.Cu': [], 'B.Cu': []}
    for m in re.finditer(r'\(segment\s+\(start ([\d.-]+) ([\d.-]+)\)\s+\(end ([\d.-]+) ([\d.-]+)\)\s+\(width ([\d.]+)\)\s+'
                         r'\(layer "([^"]+)"\)\s+\(net (\d+)\)', s):
        x1, y1, x2, y2, w, l, n = m.groups()
        if l in cu:
            cu[l].append(('seg', (float(x1), float(y1), float(x2), float(y2), float(w) / 2), netname[n]))
    for m in re.finditer(r'\(via\s+\(at ([\d.-]+) ([\d.-]+)\)\s+\(size ([\d.]+)\).*?\(net (\d+)\)', s, re.S):
        for l in cu:
            cu[l].append(('circ', (float(m.group(1)), float(m.group(2)), float(m.group(3)) / 2), netname[m.group(4)]))
    for blk in s.split('\n\t(footprint ')[1:]:
        at = re.search(r'\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)', blk).groups()
        x0, y0, rot = float(at[0]), float(at[1]), float(at[2] or 0)
        side = re.search(r'\(layer "([^"]+)"\)', blk).group(1)
        for pb in blk.split('(pad ')[1:]:
            m = re.match(r'"([^"]*)" (smd|thru_hole|np_thru_hole) (\w+)\s*\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)\s*'
                         r'\(size ([\d.]+) ([\d.]+)\)', pb)
            if not m:
                continue
            x, y, a = float(m.group(4)), float(m.group(5)), math.radians(-rot)
            X, Y = x0 + x * math.cos(a) - y * math.sin(a), y0 + x * math.sin(a) + y * math.cos(a)
            nm = re.search(r'\(net \d+ "([^"]*)"\)', pb)
            for l in (['F.Cu', 'B.Cu'] if m.group(2) != 'smd' else [side]):
                cu[l].append(('circ', (X, Y, max(float(m.group(7)), float(m.group(8))) / 2), nm.group(1) if nm else ''))
    return cu


def dist(kind, g, x, y):
    if kind == 'circ':
        return math.hypot(x - g[0], y - g[1]) - g[2]
    x1, y1, x2, y2, hw = g
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / L2))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy)) - hw


def margin(img, x, y):
    """Distance (mm) from (x, y) to the nearest set pixel within 4 mm."""
    r = int(4 * PX)
    i, j = int(round(y * PX)), int(round(x * PX))
    ys, xs = np.nonzero(img[i - r:i + r + 1, j - r:j + r + 1])
    return float(np.min(np.hypot(ys - r, xs - r))) / PX if len(ys) else 99.0


def main():
    tmp = tempfile.mkdtemp()
    try:
        export(tmp)
        silk, mask, edge = raster(tmp, 'F.SilkS'), raster(tmp, 'F.Mask'), raster(tmp, 'Edge.Cuts')
        lab, _ = ndimage.label(~ndimage.binary_dilation(edge, iterations=2))
        board = lab == lab[int(120 * PX), int(75 * PX)]
        edge_d = ndimage.distance_transform_edt(board) / PX
        cu = copper()
        ok_all = True
        print(f'pad diameter {PAD_R * 2:.1f} mm; margins are pad edge (via edge for B.Cu) to the nearest obstacle, mm')
        for tp, net, x, y, how in PADS:
            ms, mm_ = margin(silk, x, y) - PAD_R, margin(mask, x, y) - PAD_R
            me = edge_d[int(round(y * PX)), int(round(x * PX))] - PAD_R
            mf = min((dist(k, g, x, y) for k, g, n in cu['F.Cu'] if n != net), default=99) - PAD_R
            mb = min((dist(k, g, x, y) for k, g, n in cu['B.Cu'] if n != net), default=99) - VIA_R
            needs_via = 'via' in how
            ok = ms >= SILK_CLR and mm_ >= MASK_CLR and me >= EDGE_CLR and mf >= CU_CLR and (mb >= VIA_CLR or not needs_via)
            ok_all &= ok
            print(f'{tp:5s} {net:12s} ({x:6.2f},{y:6.2f})  silk {ms:4.2f}  mask {mm_:4.2f}  edge {me:4.1f}  '
                  f'F.Cu {mf:4.2f}  B.Cu {mb:4.2f}  {"OK" if ok else "CHECK"}')
        k = 8.0
        im = raster(tmp, 'front', px_per_mm=k, gray=False)
        d = ImageDraw.Draw(im)
        for tp, net, x, y, how in PADS:
            r = PAD_R * k * 1.6
            col = (0, 170, 255) if net == 'GND' else (40, 255, 40)
            d.ellipse([x * k - r, y * k - r, x * k + r, y * k + r], outline=col, width=3)
            d.text((x * k + r + 2, y * k - 6), tp, fill=(255, 255, 255))
        im.crop((int(43 * k), int(36 * k), int(105.5 * k), int(149 * k))).save(os.path.join(HERE, 'tp_front.png'),
                                                                                optimize=True)
        print('all pads clear' if ok_all else 'some pads need checking')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
