"""Track-graph resistance between pads of a net (copper tracks + vias; zones/teardrops ignored).

python net_resistance.py <board.json> <net> <REF.PAD> <REF.PAD> [...more pairs as A>B] [--cu_um 35] [--plating_um 20]
Prints effective DC resistance (mOhm) and the narrowest track width on the lowest-resistance path.
Assumes 1 oz (35 um) outer copper unless --cu_um is given (no stack-up is defined in the board file).
"""
import json
import math
import sys

import networkx as nx
from shapely.geometry import Point, Polygon

RHO = 1.72e-8  # ohm*m, copper at 20 C


def build(b, net, cu_um, plating_um, board_mm=1.6):
    G = nx.Graph()
    t_m = cu_um * 1e-6

    def key(layer, xy):
        return (layer, round(xy[0], 3), round(xy[1], 3))

    segs = [t for t in b["tracks"] if t["net"] == net]
    for t in segs:
        a, c = key(t["layer"], t["start"]), key(t["layer"], t["end"])
        L = t["len"] * 1e-3
        R = RHO * L / (t["width"] * 1e-3 * t_m) if L > 0 else 1e-6
        if G.has_edge(a, c):
            r0 = G[a][c]["R"]
            G[a][c]["R"] = 1 / (1 / r0 + 1 / R)
        else:
            G.add_edge(a, c, R=R, w=t["width"], kind="track")
    # merge coincident endpoints on same layer handled by key rounding; connect T-junctions (endpoint on segment)
    nodes = list(G.nodes)
    for t in segs:
        ax_, ay = t["start"]
        bx, by = t["end"]
        dx, dy = bx - ax_, by - ay
        L2 = dx * dx + dy * dy
        if L2 == 0:
            continue
        for n in nodes:
            if n[0] != t["layer"]:
                continue
            px, py = n[1], n[2]
            u = ((px - ax_) * dx + (py - ay) * dy) / L2
            if 0.001 < u < 0.999:
                qx, qy = ax_ + u * dx, ay + u * dy
                if math.hypot(px - qx, py - qy) < t["width"] / 2:
                    a, c = key(t["layer"], t["start"]), key(t["layer"], t["end"])
                    Ra = RHO * (u * t["len"] * 1e-3) / (t["width"] * 1e-3 * t_m)
                    G.add_edge(a, n, R=Ra, w=t["width"], kind="tee")
    # vias
    for v in b["vias"]:
        if v["net"] != net:
            continue
        rv = RHO * board_mm * 1e-3 / (math.pi * v["drill"] * 1e-3 * plating_um * 1e-6)
        f, bk = key("F.Cu", v["pos"]), key("B.Cu", v["pos"])
        G.add_edge(f, bk, R=rv, w=v["drill"], kind="via")
        # tracks ending inside via pad
        for n in list(G.nodes):
            if n in (f, bk):
                continue
            if math.hypot(n[1] - v["pos"][0], n[2] - v["pos"][1]) <= v["dia"] / 2 + 1e-3:
                G.add_edge(n, f if n[0] == "F.Cu" else bk, R=1e-6, w=99, kind="viapad")
    # pads
    padnodes = {}
    for fp in b["footprints"]:
        for p in fp["pads"]:
            if p["net"] != net or not p["poly"]:
                continue
            name = f"{fp['ref']}.{p['num']}"
            polys = [Polygon(pp["outer"]) for pp in p["poly"]]
            players = [l for l in p["layers"] if l.endswith(".Cu")] or (["F.Cu", "B.Cu"] if "*.Cu" in p["layers"] else [])
            if "*.Cu" in p["layers"]:
                players = ["F.Cu", "B.Cu"]
            pn = ("PAD", name)
            for n in list(G.nodes):
                if n[0] in players and any(P.buffer(0.01).contains(Point(n[1], n[2])) for P in polys):
                    G.add_edge(pn, n, R=1e-6, w=99, kind="pad")
            padnodes.setdefault(name, pn)
            if pn not in G:
                G.add_node(pn)
    return G, padnodes


def eff_res(G, a, c):
    if not nx.has_path(G, a, c):
        return None, None, None
    H = G.subgraph(nx.node_connected_component(G, a)).copy()
    for u, v, d in H.edges(data=True):
        d["g"] = 1.0 / max(d["R"], 1e-9)
    r = nx.resistance_distance(H, a, c, weight="g", invert_weight=False)
    path = nx.shortest_path(H, a, c, weight="R")
    wmin = min(H[path[i]][path[i + 1]]["w"] for i in range(len(path) - 1))
    rpath = sum(H[path[i]][path[i + 1]]["R"] for i in range(len(path) - 1))
    return r, wmin, rpath


def main():
    argv = sys.argv[1:]
    cu = 35.0
    pl = 20.0
    if "--cu_um" in argv:
        i = argv.index("--cu_um"); cu = float(argv[i + 1]); del argv[i:i + 2]
    if "--plating_um" in argv:
        i = argv.index("--plating_um"); pl = float(argv[i + 1]); del argv[i:i + 2]
    b = json.load(open(argv[0]))
    net = argv[1]
    G, pads = build(b, net, cu, pl)
    pairs = [p.split(">") for p in argv[2:]]
    for a, c in pairs:
        if a not in pads or c not in pads:
            print(net, a, c, "pad missing; pads:", sorted(pads))
            continue
        r, wmin, rpath = eff_res(G, pads[a], pads[c])
        if r is None:
            print(f"{net}: {a} -> {c}: NOT CONNECTED by tracks (zone/teardrop only?)")
        else:
            print(f"{net}: {a} -> {c}: R_eff = {r*1e3:.1f} mOhm (single best path {rpath*1e3:.1f} mOhm), narrowest track on best path {wmin:.2f} mm")


if __name__ == "__main__":
    main()
