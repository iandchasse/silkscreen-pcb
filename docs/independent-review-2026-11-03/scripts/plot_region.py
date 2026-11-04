"""Plot a region of the board (x-ray view from the front, KiCad coordinates, y down) with readable labels.

python plot_region.py <board.json> <out.png> x0 y0 x1 y1 [net1,net2,...] [--layers F|B|FB] [--scale px_per_mm]
Highlighted nets are drawn in colour with their track widths annotated; others grey.
"""
import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon as MPoly, Circle  # noqa: E402
from shapely.geometry import Polygon, box  # noqa: E402

COLORS = ["#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#e377c2", "#8c564b", "#bcbd22", "#1f77b4",
          "#7f0000", "#004d00", "#000080"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = {sys.argv[i]: sys.argv[i + 1] for i in range(len(sys.argv) - 1) if sys.argv[i].startswith("--")}
    args = [a for a in args if a not in opts.values()]
    bj, out = args[0], args[1]
    x0, y0, x1, y1 = map(float, args[2:6])
    hl = args[6].split(",") if len(args) > 6 and args[6] else []
    layers = opts.get("--layers", "B")
    scale = float(opts.get("--scale", "40"))
    b = json.load(open(bj))
    view = box(x0, y0, x1, y1)
    fig = plt.figure(figsize=((x1 - x0) * scale / 100, (y1 - y0) * scale / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    ax.set_aspect("equal")
    ax.axis("off")
    col = {n: COLORS[i % len(COLORS)] for i, n in enumerate(hl)}
    # outline
    for o in b["outline"]:
        ring = o["outer"]
        ax.add_patch(MPoly(ring, closed=True, fill=False, ec="k", lw=1.2))
        for h in o["holes"]:
            ax.add_patch(MPoly(h, closed=True, fill=True, fc="white", ec="k", lw=1.0))
    # GND pours
    for z in b["zones"]:
        if z["net"] != "GND" or z["keepout"]:
            continue
        for l, polys in z["filled"].items():
            if not isinstance(polys, list) or l[0] not in layers:
                continue
            fc = "#cfe2ff" if l == "B.Cu" else "#ffd9d9"
            for p in polys:
                P = Polygon(p["outer"], p["holes"])
                if not P.intersects(view):
                    continue
                ax.add_patch(MPoly(p["outer"], closed=True, fc=fc, ec="none", alpha=0.6 if l == "B.Cu" else 0.4))
                for h in p["holes"]:
                    ax.add_patch(MPoly(h, closed=True, fc="white", ec="none", alpha=0.8))
    # tracks
    for t in b["tracks"]:
        if t["layer"][0] not in layers:
            continue
        xs, ys = (t["start"][0], t["end"][0]), (t["start"][1], t["end"][1])
        if max(xs) < x0 or min(xs) > x1 or max(ys) < y0 or min(ys) > y1:
            continue
        c = col.get(t["net"], "#555555" if t["layer"] == "B.Cu" else "#aa7777")
        ls = "-" if t["layer"] == "B.Cu" else (0, (3, 1))
        lw_pts = t["width"] * scale * 0.72  # mm -> points at this scale
        ax.plot(xs, ys, color=c, lw=max(lw_pts, 0.6), solid_capstyle="round", ls=ls,
                alpha=0.95 if t["net"] in col else 0.55)
        if t["net"] in col and t["len"] > 1.2:
            ax.text((xs[0] + xs[1]) / 2, (ys[0] + ys[1]) / 2, f"{t['width']:.2f}", fontsize=5, color="k",
                    ha="center", va="center", bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.7))
    # pads
    for f in b["footprints"]:
        fx, fy = f["pos"]
        inside = x0 - 3 < fx < x1 + 3 and y0 - 3 < fy < y1 + 3
        for p in f["pads"]:
            if not p["poly"]:
                continue
            for poly in p["poly"]:
                c = col.get(p["net"], "#888888")
                ax.add_patch(MPoly(poly["outer"], closed=True, fc=c, ec="k", lw=0.3,
                                   alpha=0.85 if p["net"] in col else 0.45))
        if inside and x0 < fx < x1 and y0 < fy < y1:
            ax.text(fx, fy, f["ref"], fontsize=7, color="navy", ha="center", va="center", weight="bold",
                    bbox=dict(boxstyle="round,pad=0.1", fc="yellow", ec="none", alpha=0.6))
    for v in b["vias"]:
        if x0 <= v["pos"][0] <= x1 and y0 <= v["pos"][1] <= y1:
            c = col.get(v["net"], "#444444")
            ax.add_patch(Circle(v["pos"], v["dia"] / 2, fc=c, ec="k", lw=0.3, alpha=0.9))
            ax.add_patch(Circle(v["pos"], v["drill"] / 2, fc="white", ec="none"))
    # legend
    for i, n in enumerate(hl):
        ax.text(x0 + 0.5, y0 + 0.8 + i * 1.0, n, color=col[n], fontsize=7, weight="bold",
                bbox=dict(fc="white", ec="none", alpha=0.8))
    # grid ticks (mm) along edges
    import math
    for gx in range(math.ceil(x0), int(x1) + 1):
        if gx % 5 == 0:
            ax.text(gx, y1 - 0.3, str(gx), fontsize=5, ha="center", color="gray")
    for gy in range(math.ceil(y0), int(y1) + 1):
        if gy % 5 == 0:
            ax.text(x1 - 0.3, gy, str(gy), fontsize=5, ha="right", va="center", color="gray")
    fig.savefig(out)
    print(out)


if __name__ == "__main__":
    main()
