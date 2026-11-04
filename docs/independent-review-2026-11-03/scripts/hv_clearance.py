"""Minimum copper spacing between higher-voltage nets and every other net (same layer), vs IPC-2221B.

python hv_clearance.py <board.json>
Uses track outlines (buffered), pad polygons and via annuli; zones = GND pour fills. Reports the closest
neighbour of each HV net, the worst-case voltage difference assumed, and the IPC-2221B spacing for
B4 (external, solder-mask coated) and A6 (external component terminations, uncoated).
"""
import json
import sys
from collections import defaultdict

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

# worst-case DC level (V) of each net, used for the difference
VMAX = {
    "LED_SW": 25.5, "TPS_SW_NODE": 25.5, "C-": 25.5, "W-": 25.5, "Net-(Q5-S)": 0.2,
    "PREVGH": 22.0, "PREVGL": -22.0, "Net-(D4-K)": -22.0, "EINK_SW": 22.0,
    "Net-(C13-Pad2)": 15.0, "Net-(C15-Pad2)": -15.0, "Net-(C17-Pad2)": 15.0, "Net-(C20-Pad2)": -2.5,
    "Net-(C19-Pad2)": 7.75, "/GDR": 3.6, "/RESE": 1.0,
}
HV = [n for n, v in VMAX.items() if abs(v) >= 7]


def ipc(dv):
    # IPC-2221B Table 6-1: (B4 coated, A6 uncoated termination) in mm
    if dv <= 15:
        return 0.05, 0.13
    if dv <= 30:
        return 0.05, 0.13
    if dv <= 50:
        return 0.13, 0.13
    if dv <= 100:
        return 0.13, 0.13
    return 0.4, 0.4


def main(path):
    b = json.load(open(path))
    geoms = defaultdict(list)  # (layer) -> list of (net, geom, kind)
    for t in b["tracks"]:
        g = LineString([t["start"], t["end"]]).buffer(t["width"] / 2, 8)
        geoms[t["layer"]].append((t["net"], g, "track"))
    for v in b["vias"]:
        g = Point(v["pos"]).buffer(v["dia"] / 2, 16)
        for l in ("F.Cu", "B.Cu"):
            geoms[l].append((v["net"], g, "via"))
    for f in b["footprints"]:
        for p in f["pads"]:
            if not p["poly"]:
                continue
            g = unary_union([Polygon(pp["outer"]) for pp in p["poly"]])
            lays = ["F.Cu", "B.Cu"] if (p["drill"][0] > 0 or "*.Cu" in p["layers"]) else [l for l in p["layers"] if l.endswith(".Cu")]
            for l in lays:
                geoms[l].append((p["net"], g, f"pad {f['ref']}.{p['num']}"))
    for z in b["zones"]:
        if z["keepout"]:
            continue
        for l, polys in z["filled"].items():
            if isinstance(polys, list):
                for pp in polys:
                    geoms[l].append((z["net"], Polygon(pp["outer"], pp["holes"]), "zone"))
    worst = {}
    for l, items in geoms.items():
        tree = STRtree([g for _, g, _ in items])
        for i, (net, g, kind) in enumerate(items):
            if net not in HV:
                continue
            for j in tree.query(g.buffer(1.0)):
                n2, g2, k2 = items[j]
                if n2 == net or n2 == "":
                    continue
                d = g.distance(g2)
                dv = abs(VMAX.get(net, 0) - VMAX.get(n2, 3.3 if n2 not in ("GND",) else 0.0))
                key = (net, n2)
                if key not in worst or d < worst[key][0]:
                    worst[key] = (d, dv, l, kind, k2)
    print(f"{'HV net':16s} {'neighbour':18s} {'min gap mm':>10s} {'dV':>6s} {'IPC B4/A6 mm':>12s}  layer  items")
    for (n1, n2), (d, dv, l, k1, k2) in sorted(worst.items(), key=lambda x: x[1][0]):
        if d > 0.6:
            continue
        b4, a6 = ipc(dv)
        flag = "  <-- below A6" if (d < a6 and ("pad" in k1 or "pad" in k2)) else ("  <-- below B4" if d < b4 else "")
        print(f"{n1:16s} {n2:18s} {d:10.3f} {dv:6.1f} {b4:5.2f}/{a6:4.2f}  {l}  {k1} | {k2}{flag}")


if __name__ == "__main__":
    main(sys.argv[1])
