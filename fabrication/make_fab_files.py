#!/usr/bin/env python3
"""Build the PCBWay / NextPCB assembly upload files (BOM, placement, assembly drawing).

    python fabrication/make_fab_files.py             # writes production/other_fabs/
    python fabrication/make_fab_files.py --no-tht    # leave through-hole parts out (hand-solder them)

Inputs (nothing is modified; KiCad may stay open):
  - silkscreen_pcb.kicad_pcb  read by `kicad-cli` for placement and the assembly drawing
  - fabrication/part_fields.csv  MPN / Manufacturer / DNP per reference (the "prime" DigiKey-findable parts)
  - fabrication/nextpcb_substitutes.csv  optional MPN swaps for parts NextPCB cannot match; applied to the
                                 NextPCB BOM only (part_fields.csv and the PCBWay BOM keep the prime parts)

Outputs, in production/other_fabs/ (the gerber zip is shared and stays in production/):
  - pcbway_bom.csv               PCBWay turnkey BOM (fitted parts only)
  - nextpcb_bom.csv              NextPCB BOM in NextPCB's own template columns (fitted parts only: DNP parts are left
                                 out, because NextPCB merges lines that share an MPN and drops the DNP mark)
  - placement_bottom_kicad.csv   KiCad's own position export, SMD only (PCBWay centroid)
  - nextpcb_centroid.csv         NextPCB's sample layout (Designator, Mid X, Mid Y, Layer, Rotation, "mm" suffix on the
                                 coordinates). Covers EVERY fitted part in nextpcb_bom.csv, through-hole included:
                                 NextPCB rejects a PnP file whose designators differ from the BOM's
  - assembly_drawing_bottom.pdf  bottom-side drawing (overview + 4 zoomed A3 pages): part outlines and
                                 reference designators only, DNP parts crossed out. Needs KiCad's Python and
                                 Edge/Chrome; skipped with a note if either is missing.

The placement file is the raw KiCad export. It is NOT production/positions.csv: the Fabrication Toolkit
rewrites bottom-side rotations and per-part offsets for JLCPCB's library, which other assemblers do not share.
The CSVs are deterministic, and the PDF is only redrawn when the board or this script is newer than it (the
browser stamps a creation time into it), so re-running on an unchanged board leaves git clean.
"""
import argparse, csv, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PCB = ROOT / "silkscreen_pcb.kicad_pcb"
FIELDS = ROOT / "fabrication" / "part_fields.csv"
SUBS = ROOT / "fabrication" / "nextpcb_substitutes.csv"
OUT = ROOT / "production" / "other_fabs"
DNP_MARKS = {"1", "y", "yes", "x", "dnp", "true"}


def find_kicad_cli(explicit):
    for c in (explicit, os.environ.get("KICAD_CLI"), shutil.which("kicad-cli"),
              r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"):
        if c and Path(c).is_file():
            return c
    sys.exit("kicad-cli not found: pass --kicad-cli PATH or set KICAD_CLI")


def refs_of(s):
    return [x for x in re.split(r"[,\s]+", s) if x]


def nat(ref):
    m = re.match(r"([A-Za-z]+)(\d+)", ref)
    return (m.group(1), int(m.group(2))) if m else (ref, 0)


def short_pkg(pkg):
    """C_0603_1608Metric_Pad... -> 0603; anything else is kept as KiCad names it."""
    m = re.match(r"^[A-Z]+_(\d{4})_\d{4}Metric", pkg)
    return m.group(1) if m else pkg


def num(x):
    return f"{x:.6f}".rstrip("0").rstrip(".")


def export_pos(cli, out, smd_only=False, exclude_dnp=True):
    cmd = [cli, "pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "-o", str(out)]
    if exclude_dnp:
        cmd.append("--exclude-dnp")
    if smd_only:
        cmd.append("--smd-only")
    subprocess.run(cmd + [str(PCB)], check=True, capture_output=True)
    with open(out, newline="", encoding="utf-8-sig") as f:
        return {r["Ref"]: r for r in csv.DictReader(f)}


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


HIDE_VALUES = """
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
for fp in b.GetFootprints():
    fp.Value().SetVisible(False)
pcbnew.SaveBoard(sys.argv[2], b)
"""


def pcbnew_python(cli):
    """A Python that can `import pcbnew`: this one, KiCad's bundled one beside kicad-cli, or python3."""
    for c in (sys.executable, str(Path(cli).with_name("python.exe")), str(Path(cli).with_name("python3")), "python3"):
        try:
            if subprocess.run([c, "-c", "import pcbnew"], capture_output=True).returncode == 0:
                return c
        except OSError:
            pass
    return None


def find_browser():
    for c in (os.environ.get("CHROMIUM"),
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              *(shutil.which(n) for n in ("msedge", "google-chrome", "chromium", "chromium-browser", "chrome"))):
        if c and Path(c).is_file():
            return c
    return None


def svg_bounds(svg):
    """Bounding box (x0, y0, x1, y1) of the paths, circles and rects in a KiCad SVG."""
    n = r"-?\d+(?:\.\d+)?"
    xs, ys = [], []
    for d in re.findall(r'\sd="([^"]*)"', svg):
        toks, i, cmd = re.findall(r"[MLAZmlaz]|" + n, d), 0, None
        while i < len(toks):
            if toks[i].isalpha():
                cmd, i = toks[i].upper(), i + 1
            elif cmd in ("M", "L"):
                xs.append(float(toks[i])); ys.append(float(toks[i + 1])); i += 2
            elif cmd == "A":
                xs.append(float(toks[i + 5])); ys.append(float(toks[i + 6])); i += 7
            else:
                i += 1
    for cx, cy, r in re.findall(rf'<circle[^>]*cx="({n})"[^>]*cy="({n})"[^>]*r="({n})"', svg):
        cx, cy, r = float(cx), float(cy), float(r)
        xs += [cx - r, cx + r]; ys += [cy - r, cy + r]
    return min(xs), min(ys), max(xs), max(ys)


def drawing_html(svg):
    """Overview page plus 2 x 2 zoomed A3 pages of the bottom-side fab layer (one SVG, drawn with <use>)."""
    x0, y0, x1, y1 = svg_bounds(svg)
    x0, y0, x1, y1 = x0 - 1, y0 - 1, x1 + 1, y1 + 1
    w, h = x1 - x0, y1 - y0
    pw, ph, m, head, ov = 297, 420, 6, 9, 3            # A3 portrait, margin, header height, tile overlap (mm)
    aw, ah = pw - 2 * m, ph - 2 * m - head
    tw, th = w / 2 + ov, h / 2 + ov
    s = min(aw / tw, ah / th)                          # zoom factor
    tiles = [(x0 + i * (w - tw), y0 + j * (h - th)) for j in range(2) for i in range(2)]
    inner = svg[svg.index("</desc>") + 7:svg.rindex("</svg>")]
    k = min(aw / w, ah / h)
    boxes = "".join(
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{tw:.2f}" height="{th:.2f}" fill="none" stroke="#c00" '
        f'stroke-width="0.35" stroke-dasharray="2 1"/><text x="{x + 1.5:.2f}" y="{y + 5:.2f}" font-size="5" '
        f'fill="#c00" font-family="sans-serif">{n}</text>' for n, (x, y) in enumerate(tiles, 1))
    pages = [f'<div class="page"><div class="head">Overview: BOTTOM side, seen from below (mirrored). '
             f'Red boxes are detail pages 2-5. Crossed-out parts are not fitted.</div>'
             f'<svg width="{w * k:.1f}mm" height="{h * k:.1f}mm" viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}">'
             f'<use href="#b"/>{boxes}</svg></div>']
    for n, (x, y) in enumerate(tiles, 1):
        pages.append(f'<div class="page"><div class="head">Detail {n} of 4: BOTTOM side, seen from below '
                     f'(mirrored), x{s:.1f}. Crossed-out parts are not fitted.</div>'
                     f'<svg width="{tw * s:.1f}mm" height="{th * s:.1f}mm" '
                     f'viewBox="{x:.3f} {y:.3f} {tw:.3f} {th:.3f}"><use href="#b"/></svg></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{pw}mm {ph}mm;margin:0}}'
            f'html,body{{margin:0;background:#fff}}.page{{width:{pw}mm;height:{ph}mm;box-sizing:border-box;'
            f'padding:{m}mm;page-break-after:always;overflow:hidden}}.head{{height:{head}mm;'
            f'font:4.2mm/{head}mm sans-serif}}svg{{display:block}}</style></head><body>'
            f'<svg width="0" height="0" style="position:absolute"><defs><g id="b">{inner}</g></defs></svg>'
            + "".join(pages) + "</body></html>")


def render_drawing(cli, pdf):
    """Bottom-side assembly drawing: reference designators and part outlines only, zoomed so they can be read.
    KiCad's own PDF plot is 1:1 with 0.5 mm labels and every value string on top, which is unreadable."""
    py, browser = pcbnew_python(cli), find_browser()
    if not py or not browser:
        return "skipped (needs KiCad's Python with pcbnew and Edge/Chrome; the other files are unaffected)"
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        subprocess.run([py, "-c", HIDE_VALUES, str(PCB), str(t / "novalue.kicad_pcb")], check=True, capture_output=True)
        subprocess.run([cli, "pcb", "export", "svg", "-l", "B.Fab,Edge.Cuts", "--mirror", "--black-and-white",
                        "--page-size-mode", "2", "--exclude-drawing-sheet", "--sketch-pads-on-fab-layers",
                        "--crossout-DNP-footprints-on-fab-layers", "-o", str(t / "b.svg"), str(t / "novalue.kicad_pcb")],
                       check=True, capture_output=True)
        (t / "d.html").write_text(drawing_html((t / "b.svg").read_text(encoding="utf-8")), encoding="utf-8")
        tmp_pdf = t / "d.pdf"
        proc = subprocess.Popen([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                                 f"--user-data-dir={t / 'profile'}", f"--print-to-pdf={tmp_pdf}",
                                 (t / "d.html").as_uri()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        last, stable = -1, 0
        for _ in range(180):                               # wait for the PDF to appear and stop growing
            time.sleep(0.5)
            size = tmp_pdf.stat().st_size if tmp_pdf.exists() else -1
            stable = stable + 1 if size == last and size > 0 else 0
            last = size
            if stable >= 3:
                break
        proc.kill()
        if stable < 3:
            return "failed (browser produced no PDF)"
        shutil.copyfile(tmp_pdf, pdf)
    return "redrawn"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--no-tht", action="store_true", help="leave through-hole parts out of the BOMs")
    ap.add_argument("--split", action="store_true",
                    help="also write separate SMD-only and through-hole-only NextPCB BOM+centroid pairs to other_fabs/split/")
    ap.add_argument("--skip-drawing", action="store_true", help="do not (re)draw assembly_drawing_bottom.pdf")
    ap.add_argument("--kicad-cli", help="path to kicad-cli (default: PATH, $KICAD_CLI, KiCad 9 install)")
    args = ap.parse_args()
    cli = find_kicad_cli(args.kicad_cli)

    with open(FIELDS, newline="", encoding="utf-8-sig") as f:
        fields = {}
        for r in csv.DictReader(f):
            dnp = r["DNP"].strip().lower() in DNP_MARKS
            for ref in refs_of(r["Refs"]):
                fields[ref] = {**r, "dnp": dnp}

    tmp = Path(tempfile.mkdtemp())
    try:
        placed = export_pos(cli, tmp / "all.csv")
        smd = export_pos(cli, tmp / "smd.csv", smd_only=True)
        # incl. DNP parts: package and SMD/THT lookup (SMD-only export drops DNP parts)
        every = export_pos(cli, tmp / "every.csv", exclude_dnp=False)
        every_smd = export_pos(cli, tmp / "every_smd.csv", smd_only=True, exclude_dnp=False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    problems = [f"{r}: no row in part_fields.csv" for r in placed if r not in fields]
    problems += [f"{r}: blank MPN in part_fields.csv" for r in placed if r in fields and not fields[r]["MPN"].strip()]
    if problems:
        sys.exit("cannot build BOM:\n  " + "\n  ".join(problems))

    def part(ref, r):
        pkg = short_pkg(every[ref]["Package"]) if ref in every else ""
        return {"ref": ref, "mpn": r["MPN"].strip(), "mfr": r["Manufacturer"].strip(), "value": r["Value"].strip(),
                "pkg": pkg, "type": "SMD" if ref in every_smd else "THT", "dnp": r["dnp"]}

    # fitted parts come from the board (so KiCad's DNP flag decides what is placed). DNP parts are NOT written to
    # any BOM: NextPCB merged our DNP 0-ohm/10k lines into the fitted lines with the same MPN and dropped the DNP
    # mark, which would have fitted R74 next to R73 (3V3 shorted to GND) and R43/R45/R58/R66/R72.
    parts = [part(ref, fields[ref]) for ref in placed]

    # NextPCB-only substitutes: parts it cannot match are swapped for ones it can (fabrication/nextpcb_substitutes.csv)
    subs = {}
    if SUBS.exists():
        with open(SUBS, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                for ref in refs_of(r["Refs"]):
                    subs[ref] = r
    unknown = sorted(r for r in subs if r not in placed)
    if unknown:
        sys.exit(f"nextpcb_substitutes.csv names references that are not fitted on the board: {unknown}")
    nx_parts = [{**p, "mpn": subs[p["ref"]]["MPN"].strip(), "mfr": subs[p["ref"]]["Manufacturer"].strip()}
                if p["ref"] in subs else p for p in parts]
    if args.no_tht:
        parts = [p for p in parts if p["type"] == "SMD"]
        nx_parts = [p for p in nx_parts if p["type"] == "SMD"]

    def group(items):
        g = {}
        for p in items:
            g.setdefault((p["mpn"], p["mfr"], p["value"], p["pkg"], p["type"], p["dnp"]), []).append(p["ref"])
        return sorted(g.items(), key=lambda kv: nat(sorted(kv[1], key=nat)[0]))

    OUT.mkdir(parents=True, exist_ok=True)

    pw_rows = []
    for i, ((mpn, mfr, val, pkg, typ, _), refs) in enumerate(group(parts), 1):
        refs = sorted(refs, key=nat)
        pw_rows.append([i, len(refs), ",".join(refs), mpn, f"{val} {pkg}".strip(), pkg, typ, mfr, mpn, ""])
    write_csv(OUT / "pcbway_bom.csv",
              ["Item", "Quantity", "Reference Designator", "Part Number", "Part Description", "Package", "Type",
               "Manufacturer", "Manufacturer Part Number", "Distributor Part Number"], pw_rows)

    # NextPCB's own BOM template (the quote page's "Download BOM Template"): S/N, Designator*, Quantity*,
    # Manufacturer Part Number*, Procurement Type, Customer Note. Fitted parts only (see the note above); the
    # Procurement Type column stays empty (DNP = do not fit, C = customer supplied, which Rev0 does not accept).
    NX_BOM_HEADER = ["S/N", "Designator", "Quantity", "Manufacturer Part Number", "Procurement Type", "Customer Note"]

    def nx_bom_rows(plist):
        rows = []
        for n, ((mpn, mfr, val, pkg, typ, dnp), refs) in enumerate(group(plist), 1):
            refs = sorted(refs, key=nat)
            was = subs[refs[0]]["Replaces"].strip() if refs[0] in subs else ""
            rows.append([n, ",".join(refs), len(refs), mpn, "",
                         f"{mfr} | {val} | {pkg} | {typ}" + (f" | substitute for {was}" if was else "")])
        return rows

    nx_rows = nx_bom_rows(nx_parts)
    write_csv(OUT / "nextpcb_bom.csv", NX_BOM_HEADER, nx_rows)

    write_csv(OUT / "placement_bottom_kicad.csv",
              ["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"],
              [[ref, r["Val"], r["Package"], num(float(r["PosX"])), num(float(r["PosY"])),
                num(float(r["Rot"]) % 360), r["Side"].capitalize()]
               for ref, r in sorted(smd.items(), key=lambda kv: nat(kv[0]))])

    # NextPCB's own sample centroid (Rev0_Centroid.csv): plain ASCII, LF line ends, no BOM, coordinates with an
    # "mm" suffix (4 decimals, trailing zeros trimmed), integer rotation, layer as Top/Bottom. Same numbers as above.
    def mm4(x):
        t = f"{x:.4f}".rstrip("0").rstrip(".")
        return "0mm" if t in ("-0", "") else f"{t}mm"

    def rot(x):
        return str(int(round(x))) if abs(x - round(x)) < 1e-6 else f"{x:.4f}".rstrip("0").rstrip(".")

    def nx_centroid(path, refs):
        with open(path, "w", newline="", encoding="ascii") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
            w.writerows([ref, mm4(float(placed[ref]["PosX"])), mm4(float(placed[ref]["PosY"])),
                         placed[ref]["Side"].capitalize(), rot(float(placed[ref]["Rot"]) % 360)] for ref in refs)

    cen_refs = sorted((p["ref"] for p in parts), key=nat)      # same set as the fitted lines of nextpcb_bom.csv
    nx_centroid(OUT / "nextpcb_centroid.csv", cen_refs)

    if args.split:
        # matched pairs (BOM designators == centroid designators) for an SMD-only and a through-hole-only NextPCB order
        (OUT / "split").mkdir(exist_ok=True)
        for kind in ("SMD", "THT"):
            sub = [p for p in nx_parts if p["type"] == kind]
            write_csv(OUT / "split" / f"nextpcb_bom_{kind.lower()}.csv", NX_BOM_HEADER, nx_bom_rows(sub))
            nx_centroid(OUT / "split" / f"nextpcb_centroid_{kind.lower()}.csv", sorted((p["ref"] for p in sub), key=nat))

    # The browser stamps a creation time into the PDF, so only redraw it when the board or this script is newer
    # (avoids git churn on an unchanged board)
    pdf = OUT / "assembly_drawing_bottom.pdf"
    if args.skip_drawing:
        drawing = "not touched (--skip-drawing)"
    elif pdf.exists() and pdf.stat().st_mtime >= max(PCB.stat().st_mtime, Path(__file__).stat().st_mtime):
        drawing = "up to date (board unchanged)"
    else:
        drawing = render_drawing(cli, pdf)

    # cross-check against the JLC set when it is present: both must cover the same parts
    jlc = ROOT / "production" / "positions.csv"
    note = ""
    if jlc.exists():
        with open(jlc, newline="", encoding="utf-8-sig") as f:
            jrefs = {r["Designator"] for r in csv.DictReader(f)}
        if jrefs != set(placed):
            note = (f"\nWARNING: production/positions.csv (JLC) and this board disagree: only-JLC "
                    f"{sorted(jrefs - set(placed))}, only-board {sorted(set(placed) - jrefs)}. "
                    f"Regenerate the Toolkit set.")

    n_tht = sum(1 for p in parts if p["type"] == "THT")
    print(f"placed parts: {len(placed)} ({len(smd)} SMD, {len(placed) - len(smd)} through-hole)")
    print(f"pcbway_bom.csv: {len(pw_rows)} lines{'  (through-hole left out)' if args.no_tht else f'  ({n_tht} through-hole parts included)'}")
    print(f"nextpcb_bom.csv: {len(nx_rows)} lines, fitted parts only (DNP parts left out); "
          f"{len(subs)} references use a NextPCB substitute ({', '.join(sorted({r['MPN'] for r in subs.values()}))})")
    print(f"placement_bottom_kicad.csv: {len(smd)} SMD rows;  nextpcb_centroid.csv: {len(cen_refs)} rows (all fitted parts, matches the BOM)")
    print(f"assembly_drawing_bottom.pdf {drawing}")
    print(f"-> {OUT}\nUpload with the gerber zip from production/ (Silkscreen_Reader_PCB_*.zip).{note}")


if __name__ == "__main__":
    main()
