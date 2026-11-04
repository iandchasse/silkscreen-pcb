"""Trace audit for the Silkscreen board: durability and EMI/EMC checks on the exported geometry.

    python audit.py <geometry.json> <drc.json> <out_dir>

geometry.json comes from export_geometry.py (KiCad's Python), drc.json from
`kicad-cli pcb drc --schematic-parity --severity-all --format json`. Writes results.json and figures to out_dir.
All coordinates in mm. Requires shapely, numpy, Pillow.
"""
import json, math, os, sys, collections, heapq
import numpy as np
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, box
from shapely.ops import unary_union, nearest_points
from shapely.strtree import STRtree

GEO, DRC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
G = json.load(open(GEO))
D = json.load(open(DRC))
RES = {}

# ----------------------------------------------------------------------------------------------------------------
# board knowledge (Rev 1.03): net classes, design currents and voltage ranges
POWER = {'3V3', 'LDO_IN', 'B+', 'P+', 'USB_VBUS', 'VBUS_PRE_FUSE', 'PREVGH', 'PREVGL', 'SD_VDD', '/LED_VIN', 'J6_3V3', 'EINK_3V3'}
SW = {'TPS_SW_NODE', 'LED_SW', 'EINK_SW'}
# design current (A) used for trace heating; fault current noted separately
CURRENT = {
    'VBUS_PRE_FUSE': (1.0, 1.95, 'F1 hold / trip'), 'USB_VBUS': (1.0, 1.95, 'F1 hold / trip'),
    'LDO_IN': (1.0, 1.95, 'U2 output, whole board on USB'), 'P+': (1.0, 1.8, 'cell path; fault = N7 trip max'),
    'B+': (1.0, 1.8, 'cell path'), 'Net-(Q3-D)': (1.0, 1.8, 'cell path'), 'Net-(Q8-D)': (1.0, 1.8, 'cell path'),
    'B-': (1.0, 1.8, 'cell return'), '/B-_SENSE': (1.0, 1.8, 'cell return through R85/R86'),
    '/P+_FUSE': (0.75, 1.5, 'F2 hold / trip'), '3V3': (0.87, 0.87, 'U3 current limit (max)'),
    'SD_VDD': (0.2, 0.87, 'card bursts'), 'EINK_3V3': (0.1, 0.3, 'F6 hold; boost start-up peak'),
    'EINK_SW': (0.3, 0.3, 'boost start-up peak'), '/RESE': (0.3, 0.3, 'boost sense'),
    '/LED_VIN': (0.3, 0.3, 'F3 trip'), 'TPS_SW_NODE': (1.0, 2.1, 'inductor peak / U10 switch limit'),
    'LED_SW': (0.1, 0.1, 'LED strings'), 'W-': (0.1, 0.1, 'LED string'), 'C-': (0.1, 0.1, 'LED string'),
    'J6_3V3': (0.1, 0.3, 'F5'), 'PREVGH': (0.02, 0.02, 'gate rail'), 'PREVGL': (0.02, 0.02, 'gate rail'),
}
# (min V, max V) relative to board GND; default 0..3.6
VR = collections.defaultdict(lambda: (0.0, 3.6))
VR.update({
    'GND': (0, 0), '/B-_SENSE': (-0.2, 0.2), 'B-': (-4.2, 0.2), 'Net-(U5-OD)': (-4.2, 4.2), 'Net-(U5-OC)': (-4.2, 4.2),
    'Net-(U5-CS)': (-4.2, 0.5), 'Net-(U5-VCC)': (0, 4.2),
    'USB_VBUS': (0, 6.0), 'VBUS_PRE_FUSE': (0, 6.0), 'CC1': (0, 5.5), 'CC2': (0, 5.5), 'Net-(D2-K)': (0, 6.0),
    'LDO_IN': (0, 6.0), 'P+': (0, 4.2), 'B+': (0, 4.2), 'Net-(Q3-D)': (0, 4.2), 'Net-(Q8-D)': (0, 4.2), '/P+_FUSE': (0, 4.2),
    'CE': (0, 6.0), 'CHRG': (0, 6.0), 'STDBY': (0, 6.0), '/DET_NODE': (0, 6.0), 'ST': (0, 6.0), 'Net-(Q9-G)': (0, 6.0),
    'Net-(Q3-G)': (0, 4.2), '/LED_VIN': (0, 6.0),
    'TPS_SW_NODE': (-0.5, 26.0), 'LED_SW': (0, 26.0), 'W-': (0, 26.0), 'C-': (0, 26.0), 'LED_MONIT': (0, 2.9),
    'EINK_SW': (-0.5, 26.0), 'PREVGH': (0, 25.0), 'PREVGL': (-25.0, 0), 'Net-(D4-K)': (-25.0, 0.5),
    'Net-(C13-Pad2)': (0, 17.0),    # VSH1
    'Net-(C17-Pad2)': (0, 17.0),    # VSH2
    'Net-(C15-Pad2)': (-17.0, 0),   # VSL
    'Net-(C20-Pad2)': (-5.0, 5.0),  # VCOM
    'Net-(C19-Pad2)': (0, 7.5),     # VPP
    'Net-(C18-Pad2)': (0, 3.0),     # VDD (internal regulator)
    '/GDR': (0, 3.6), '/RESE': (0, 1.0),
})
RAIL_NAME = {'Net-(C13-Pad2)': 'VSH1', 'Net-(C17-Pad2)': 'VSH2', 'Net-(C15-Pad2)': 'VSL', 'Net-(C20-Pad2)': 'VCOM',
             'Net-(C19-Pad2)': 'VPP', 'Net-(C18-Pad2)': 'VDD(panel)', 'Net-(D4-K)': 'charge-pump node', 'PREVGH': 'VGH (PREVGH)',
             'PREVGL': 'VGL (PREVGL)'}
nm = lambda n: f"{n} [{RAIL_NAME[n]}]" if n in RAIL_NAME else n
# IPC-2221B Table 6-1 (minimum spacing, mm), via EMA/T61 transcriptions (see layout_refs.md):
# B2 = external conductors, uncoated; B4 = external conductors with permanent polymer coating (solder mask is commonly
# treated as B4); A6 = external component leads/terminations, uncoated (exposed pads). The governing value used here:
# A6 when either side is an exposed pad, otherwise B4 (mask-covered copper); B2 is kept as the conservative reference.
B2 = [(15, 0.10), (30, 0.10), (50, 0.60), (100, 0.60)]
B4 = [(15, 0.05), (30, 0.05), (50, 0.13), (100, 0.13)]
A6 = [(15, 0.13), (30, 0.25), (50, 0.40), (100, 0.50)]
req = lambda tab, dv: next((s for v, s in tab if dv <= v), tab[-1][1])
FAST = ['DP', 'DN', 'SD_CLK', 'SD_CMD', 'SD_DAT0', 'SD_DAT1', 'SD_DAT2', 'SD_DAT3', 'SPI_SCK', 'SPI_MOSI', 'EPD_CS', 'EPD_DC',
        'EPD_RST', 'EPD_BUSY', 'I2C_SCL', 'I2C_SDA', 'PWM_LED', 'COLOR_SEL', '/COLOR_SEL_INV', 'TX', 'RX', 'ESP32_EN', 'ESP32_IO0', '/GDR']
AGGR = ['TPS_SW_NODE', 'EINK_SW', 'Net-(D4-K)', '/GDR', '/RESE', 'W-', 'C-', 'SD_CLK', 'SPI_SCK', 'DP', 'DN', 'PWM_LED', 'COLOR_SEL', '/COLOR_SEL_INV']
VICT = ['BAT_MONIT', 'LED_MONIT', 'USB_STAT', 'PWR_BUTTON', 'BUTTON_ADC_1', 'BUTTON_ADC_2', 'TP_INT', 'TP_RST', 'EPD_BUSY',
        'EPD_RST', 'ESP32_EN', 'ESP32_IO0', 'I2C_SCL', 'I2C_SDA', 'CC1', 'CC2', 'Net-(U5-CS)', 'Net-(U11-PROG)', '/DET_NODE', 'CE']

# ----------------------------------------------------------------------------------------------------------------
# geometry
def poly_from(rings):
    return Polygon(rings[0], rings[1:]) if len(rings[0]) > 2 else None


def mpoly(lst):
    ps = [poly_from(r) for r in lst]
    return unary_union([p.buffer(0) for p in ps if p is not None and not p.is_empty])


board = unary_union([poly_from(r) for r in G["outline"]])
edge = board.boundary
LAYERS = ("F.Cu", "B.Cu")
feat = {l: [] for l in LAYERS}   # (geom, net, kind, label)
for t in G["tracks"]:
    a, c, w = tuple(t["s"]), tuple(t["e"]), t["w"]
    g = LineString([a, c]).buffer(w / 2) if a != c else Point(a).buffer(w / 2)
    feat[t["layer"]].append((g, t["net"], "track", dict(s=a, e=c, w=w)))
for v in G["vias"]:
    for l in LAYERS:
        feat[l].append((Point(v["x"], v["y"]).buffer(v["d"] / 2), v["net"], "via", dict(x=v["x"], y=v["y"], d=v["d"])))
pad_geo = {}
for p in G["pads"]:
    for l, rings in p["layers"].items():
        g = mpoly(rings)
        feat[l].append((g, p["net"], "pad", dict(ref=p["ref"], num=p["num"], attr=p["attr"])))
        pad_geo[(p["ref"], p["num"], l)] = g
fill = {l: [] for l in LAYERS}
# teardrops are copper of their pad's/via's net: include them as features (kind "teardrop", spacing class B4 unless the
# other side is an exposed pad)
for z in G["zones"]:
    if z.get("teardrop") and not z["rule_area"]:
        for l, lst in z["fills"].items():
            g = mpoly(lst)
            if not g.is_empty:
                feat[l].append((g, z["net"], "teardrop", dict()))
for z in G["zones"]:
    if z["rule_area"] or z.get("teardrop"):
        continue
    for l, lst in z["fills"].items():
        fill[l].append((z["net"], mpoly(lst)))
gnd_fill = {l: unary_union([g for n, g in fill[l] if n == "GND"]) for l in LAYERS}
fp = {f["ref"]: f for f in G["footprints"]}
pads = {(p["ref"], p["num"]): p for p in G["pads"]}
pc = lambda ref, num: (pads[(ref, num)]["x"], pads[(ref, num)]["y"])


def net_class(n):
    return "SW" if n in SW else ("Power" if n in POWER else "Default")


# IPC-2221 external-layer temperature rise for a track of width w (mm), 1 oz (35 um)
def dT(I, w):
    A = (w / 0.0254) * 1.378
    return (I / (0.048 * A ** 0.725)) ** (1 / 0.44)


def w_for(I, dt=20.0):
    A = (I / (0.048 * dt ** 0.44)) ** (1 / 0.725)
    return A / 1.378 * 0.0254


# ----------------------------------------------------------------------------------------------------------------
# A. current capacity
cur = {}
for n, (I, If, why) in CURRENT.items():
    segs = [t for t in G["tracks"] if t["net"] == n]
    if not segs:
        cur[n] = dict(I=I, note="pour only / no tracks"); continue
    need = w_for(I)
    L = lambda t: math.dist(t["s"], t["e"])
    under = [t for t in segs if t["w"] + 1e-6 < need]
    wmin = min(t["w"] for t in segs)
    lens = collections.Counter()
    for t in segs:
        lens[round(t["w"], 3)] += L(t)
    cur[n] = dict(I=I, I_fault=If, why=why, w_needed_20C=round(need, 3), w_min=wmin, dT_at_wmin=round(dT(I, wmin), 1),
                  dT_fault_at_wmin=round(dT(If, wmin), 1), length_by_width={str(k): round(v, 1) for k, v in sorted(lens.items())},
                  under_len=round(sum(L(t) for t in under), 2),
                  under=[dict(layer=t["layer"], s=t["s"], e=t["e"], w=t["w"], L=round(L(t), 2)) for t in sorted(under, key=L, reverse=True)[:6]])
# vias carrying current: same-net vias within 2.0 mm count as one parallel group (second vias were placed up to
# about 2 mm away and stitched to the first on both layers)
via_groups = {}
for n, (I, If, why) in CURRENT.items():
    vs = [v for v in G["vias"] if v["net"] == n]
    groups, used = [], set()
    for i, v in enumerate(vs):
        if i in used:
            continue
        grp = [j for j, u in enumerate(vs) if j not in used and math.dist((v["x"], v["y"]), (u["x"], u["y"])) <= 2.0]
        used.update(grp); groups.append([(vs[j]["x"], vs[j]["y"]) for j in grp])
    via_groups[n] = dict(I=I, I_fault=If, vias=len(vs), groups=[dict(at=g[0], n=len(g), A_per_via=round(I / len(g), 2),
                                                                     A_fault_per_via=round(If / len(g), 2)) for g in groups])
RES["current"] = dict(tracks=cur, vias=via_groups)

# ----------------------------------------------------------------------------------------------------------------
# B. spacing versus voltage (copper features on the same layer)
def dV(a, b):
    (a0, a1), (b0, b1) = VR[a], VR[b]
    return max(abs(a1 - b0), abs(b1 - a0))


# closest pad-to-pad gap inside each footprint per net pair: a track leaving one pad of a fine-pitch part (e.g. the
# 0.5 mm-pitch FPC connectors) and passing its neighbour no closer than the footprint's own pads is footprint-limited
fp_gap = {}
for l in LAYERS:
    fpads = collections.defaultdict(list)
    for g, n, k, lab in feat[l]:
        if k == "pad" and n:
            fpads[lab["ref"]].append((g, n))
    for ref, lst in fpads.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                if lst[i][1] != lst[j][1]:
                    kk = (ref, frozenset((lst[i][1], lst[j][1])))
                    fp_gap[kk] = min(fp_gap.get(kk, 9.0), lst[i][0].distance(lst[j][0]))


def fan_out(n_track, pad_lab, n_pad, dist):
    gp = fp_gap.get((pad_lab["ref"], frozenset((n_track, n_pad))))
    return gp is not None and dist + 1e-6 >= gp


pairs = {}
for l in LAYERS:
    geoms = [f[0] for f in feat[l]]
    tree = STRtree(geoms)
    for i, (g, n, k, lab) in enumerate(feat[l]):
        if not n or n.startswith("unconnected"):
            continue
        for j in tree.query(g.buffer(0.8)):
            if j <= i:
                continue
            g2, n2, k2, lab2 = feat[l][j]
            if n2 == n or not n2 or n2.startswith("unconnected"):
                continue
            v = dV(n, n2)
            if v < 10:          # low-voltage pairs are covered by DRC
                continue
            dist = g.distance(g2)
            same_fp = (k == "pad" and k2 == "pad" and lab["ref"] == lab2["ref"])
            fo = (k in ("track", "teardrop") and k2 == "pad" and fan_out(n, lab2, n2, dist)) or (k2 in ("track", "teardrop") and k == "pad" and fan_out(n2, lab, n, dist))
            # closest pair per net pair *and* per spacing class, so a closer mask-covered pair (B4) or a fixed
            # footprint pad gap cannot hide an exposed-pad pair (A6) that is slightly further away
            key = tuple(sorted((n, n2))) + ("footprint" if same_fp else "fan-out" if fo else "pad" if "pad" in (k, k2) else "copper",)
            if key not in pairs or dist < pairs[key]["d"]:
                p1, p2 = nearest_points(g, g2)
                pairs[key] = dict(a=nm(key[0]), b=nm(key[1]), dV=round(v, 1), d=round(dist, 3), layer=l, at=[round((p1.x + p2.x) / 2, 2), round((p1.y + p2.y) / 2, 2)],
                                  kinds=f"{k}-{k2}", where=(f"{lab['ref']}.{lab['num']}" if k == "pad" else k) + " / " + (f"{lab2['ref']}.{lab2['num']}" if k2 == "pad" else k2),
                                  inherent=same_fp or fo, inherent_why=("footprint pad gap" if same_fp else "fan-out within the footprint's own pad gap" if fo else ""))
# GND pour against the high-voltage nets
for l in LAYERS:
    for n in [n for n in VR if dV(n, "GND") >= 10]:
        gs = [f[0] for f in feat[l] if f[1] == n]
        if not gs:
            continue
        u = unary_union(gs); dist = u.distance(gnd_fill[l])
        key = (n, "GND(pour) " + l)
        p1, p2 = nearest_points(u, gnd_fill[l])
        pairs[key] = dict(a=nm(n), b="GND pour", dV=round(dV(n, "GND"), 1), d=round(dist, 3), layer=l,
                          at=[round(p1.x, 2), round(p1.y, 2)], kinds="copper-pour", where="pour", inherent=False)
hv = []
for key, p in pairs.items():
    p["req_B2"] = req(B2, p["dV"]); p["req_B4"] = req(B4, p["dV"]); p["req_A6"] = req(A6, p["dV"])
    p["governing"] = "A6" if "pad" in p["kinds"] else "B4"
    p["req"] = p["req_A6"] if p["governing"] == "A6" else p["req_B4"]
    p["ok"] = p["d"] + 1e-6 >= p["req"]
    p["ok_B2"] = p["d"] + 1e-6 >= p["req_B2"]
    hv.append(p)
hv.sort(key=lambda p: (p["ok"], p["d"] / max(p["req"], 0.01)))
RES["spacing"] = hv

# ----------------------------------------------------------------------------------------------------------------
# C. mechanical durability
mech = {}
# C1 copper near the board edge (outer outline and internal cut-outs)
near_edge = []
for l in LAYERS:
    for g, n, k, lab in feat[l]:
        d = g.distance(edge)
        if d < 0.6:
            near_edge.append(dict(layer=l, net=n, kind=k, d=round(d, 3), what=(f"{lab['ref']}.{lab['num']}" if k == "pad" else
                                  (f"track w{lab['w']}" if k == "track" else k)), at=[round(g.centroid.x, 2), round(g.centroid.y, 2)]))
near_edge.sort(key=lambda r: r["d"])
mech["near_edge"] = near_edge
# C2 copper around mounting holes (M2 DIN965 countersunk head about 3.8 mm; keep 2.5 mm from the hole centre)
holes = []
for f in G["footprints"]:
    if f["ref"].startswith("H"):
        own = {p["net"] for p in G["pads"] if p["ref"] == f["ref"]}
        c = Point(f["x"], f["y"])
        hits = []
        for l in LAYERS:
            for g, n, k, lab in feat[l]:
                if n in own or (k == "pad" and lab["ref"] == f["ref"]):
                    continue
                d = g.distance(c)
                if d < 2.5:
                    hits.append(dict(layer=l, net=n, kind=k, d_from_centre=round(d, 2)))
        holes.append(dict(ref=f["ref"], at=[f["x"], f["y"]], own_net=sorted(own), other_copper_within_2_5mm=sorted(hits, key=lambda h: h["d_from_centre"])[:6]))
mech["mount_holes"] = holes
# C3 traces crossing the optional cut line (y 61.86 / 62.00, x 84.42..104.24)
cut = LineString([(84.42, 61.93), (104.24, 61.93)])
mech["cut_line_crossings"] = sorted({(t["net"], t["layer"], t["w"]) for t in G["tracks"]
                                     if LineString([t["s"], t["e"]]).buffer(t["w"] / 2).intersects(cut.buffer(0.07))})
# C4 acute angles between consecutive same-net segments on a layer (acid traps / stress risers)
ends = collections.defaultdict(list)
for i, t in enumerate(G["tracks"]):
    for a, b in ((t["s"], t["e"]), (t["e"], t["s"])):
        ends[(t["layer"], t["net"], round(a[0], 3), round(a[1], 3))].append((i, b))
acute = []
for (l, n, x, y), lst in ends.items():
    if len(lst) < 2:
        continue
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            (ia, pa), (ib, pb) = lst[i], lst[j]
            v1 = (pa[0] - x, pa[1] - y); v2 = (pb[0] - x, pb[1] - y)
            n1, n2 = math.hypot(*v1), math.hypot(*v2)
            if n1 < 1e-4 or n2 < 1e-4:
                continue
            ang = math.degrees(math.acos(max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))))
            if ang < 89.0:
                acute.append(dict(layer=l, net=n, at=[x, y], angle=round(ang, 1)))
acute.sort(key=lambda a: a["angle"])
mech["acute_angles"] = dict(count=len(acute), under_60=sum(1 for a in acute if a["angle"] < 60), worst=acute[:12])
# C5 teardrop candidates: track meets a pad or via that is much wider than the track; "covered" if a teardrop of the
# same net on that layer overlaps the track
tears = collections.Counter()
td_geo = collections.defaultdict(list)
for l in LAYERS:
    for g, n, k, lab in feat[l]:
        if k == "teardrop":
            td_geo[(l, n)].append(g)
for t in G["tracks"]:
    tg = LineString([t["s"], t["e"]]).buffer(t["w"] / 2) if t["s"] != t["e"] else Point(t["s"]).buffer(t["w"] / 2)
    covered = any(x.intersects(tg) for x in td_geo[(t["layer"], t["net"])])
    for end in (t["s"], t["e"]):
        P = Point(end)
        for v in G["vias"]:
            if v["net"] == t["net"] and math.dist(end, (v["x"], v["y"])) < 0.02 and t["w"] < 0.6 * v["d"]:
                tears["track-via"] += 1
                tears["track-via, teardrop present"] += covered
        for p in G["pads"]:
            g = pad_geo.get((p["ref"], p["num"], t["layer"]))
            if g is not None and p["net"] == t["net"] and g.distance(P) < 0.005:
                if t["w"] < 0.6 * min(p["sx"], p["sy"]):
                    tears["track-pad"] += 1
                    tears["track-pad, teardrop present"] += covered
                break
mech["teardrop_candidates"] = dict(tears)
mech["teardrop_zones_present"] = G["meta"]["teardrop_zones"]
# C6 vias inside SMD pads (solder wicking) and untented vias
vip = []
for v in G["vias"]:
    c = Point(v["x"], v["y"]).buffer(v["drill"] / 2)
    for p in G["pads"]:
        if p["attr"] != "smd":
            continue
        for l, rings in p["layers"].items():
            g = pad_geo[(p["ref"], p["num"], l)]
            if g.intersects(c):
                vip.append(dict(via=[v["x"], v["y"]], net=v["net"], pad=f"{p['ref']}.{p['num']}", pad_net=p["net"]))
mech["via_in_pad"] = vip
mech["via_tenting"] = dict(front=G["meta"]["tent_vias_front"], back=G["meta"]["tent_vias_back"])
# C7 thin necks in the GND pour (places narrower than 0.4 mm that carry return current)
necks = {}
for l in LAYERS:
    gf = gnd_fill[l]
    parts = list(gf.geoms) if hasattr(gf, "geoms") else [gf]
    opened = gf.buffer(-0.2).buffer(0.2)
    lost = gf.difference(opened)
    lost_parts = [g for g in (lost.geoms if hasattr(lost, "geoms") else [lost]) if g.area > 0.15]
    necks[l] = dict(fill_pieces=len(parts), area_mm2=round(gf.area, 1),
                    thin_regions_over_0_15mm2=len(lost_parts),
                    largest=[[round(g.centroid.x, 1), round(g.centroid.y, 1), round(g.area, 2)] for g in sorted(lost_parts, key=lambda g: -g.area)[:8]])
mech["gnd_pour"] = necks
# C8 DRC findings
vio = D["violations"]
mech["drc_errors"] = [dict(type=v["type"], desc=v["description"], items=[(i["description"], round(i["pos"]["x"], 2), round(i["pos"]["y"], 2)) for i in v["items"]])
                      for v in vio if v["severity"] == "error"]
mech["drc_warning_counts"] = dict(collections.Counter(v["type"] for v in vio if v["severity"] == "warning"))
mech["starved_thermal"] = [[i["description"] for i in v["items"]][-1] for v in vio if v["type"] == "starved_thermal"]
mech["dangling"] = [[(i["description"], round(i["pos"]["x"], 2), round(i["pos"]["y"], 2)) for i in v["items"]] for v in vio if v["type"] == "track_dangling"]
RES["mechanical"] = mech

# ----------------------------------------------------------------------------------------------------------------
# D. EMI / EMC
emi = {}
# D1 hot loops (pad-centre polygons; GND legs assumed through the pour or the listed GND copper)
def loop(name, pts, note):
    poly = Polygon(pts)
    per = sum(math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts)))
    return dict(name=name, area_mm2=round(abs(poly.area), 1), perimeter_mm=round(per, 1), points=[[round(x, 2), round(y, 2)] for x, y in pts], note=note)
loops = []
try:
    loops.append(loop("Frontlight boost, switching (output) loop: U10 SW/VOUT -> C9 -> GND -> U10 GND",
                      [pc("U10", "5"), pc("C9", "2"), pc("C9", "1"), (47.85, 123.05), pc("U10", "4")], "the high di/dt loop of a boost"))
    loops.append(loop("Frontlight boost, input loop: C12 -> L2 -> U10 SW ... U10 GND -> C12 GND",
                      [pc("C12", "2"), pc("L2", "1"), pc("L2", "2"), pc("U10", "6"), pc("U10", "4"), pc("C12", "1")], "continuous current, lower di/dt"))
    loops.append(loop("E-paper boost, switching loop: Q4 drain -> D5 -> C14 -> GND -> R14 -> Q4 source",
                      [pc("Q4", "3"), pc("D5", "2"), pc("D5", "1"), pc("C14", "2"), pc("C14", "1"), pc("R14", "1"), pc("R14", "2"), pc("Q4", "2")],
                      "pulsed high di/dt loop"))
    loops.append(loop("E-paper boost, input loop: C10 -> L1 -> Q4 -> R14 -> GND -> C10",
                      [pc("C10", "2"), pc("L1", "2"), pc("L1", "1"), pc("Q4", "3"), pc("Q4", "2"), pc("R14", "2"), pc("R14", "1"), pc("C10", "1")],
                      "HARDWARE.md quoted 20-27 mm^2"))
    loops.append(loop("E-paper charge pump: Q4 drain -> C11 -> D4 -> C16 -> GND -> D6",
                      [pc("Q4", "3"), pc("C11", "2"), pc("C11", "1"), pc("D4", "1"), pc("D4", "2"), pc("C16", "2"), pc("C16", "1"), pc("D6", "1"), pc("D6", "2")],
                      "negative rail"))
except KeyError as e:
    loops.append(dict(name="error", note=str(e)))
emi["loops"] = loops
# D2 switching-node copper area (antenna area)
area = {}
for n in ("TPS_SW_NODE", "EINK_SW", "Net-(D4-K)", "LED_SW", "W-", "C-", "/GDR"):
    a = 0.0; length = 0.0
    for l in LAYERS:
        u = unary_union([f[0] for f in feat[l] if f[1] == n])
        a += u.area
    length = sum(math.dist(t["s"], t["e"]) for t in G["tracks"] if t["net"] == n)
    area[n] = dict(copper_mm2=round(a, 2), track_length_mm=round(length, 1))
emi["node_area"] = area
# D3 return paths: fraction of each fast net's track length with GND pour directly on the other layer
ret = {}
other = {"F.Cu": "B.Cu", "B.Cu": "F.Cu"}
gaps_all = []
for n in FAST:
    total = covered = 0.0; gaps = []
    for t in G["tracks"]:
        if t["net"] != n:
            continue
        L = math.dist(t["s"], t["e"]); k = max(1, int(L / 0.2))
        run = 0.0; start = None
        for i in range(k + 1):
            x = t["s"][0] + (t["e"][0] - t["s"][0]) * i / k; y = t["s"][1] + (t["e"][1] - t["s"][1]) * i / k
            ok = gnd_fill[other[t["layer"]]].contains(Point(x, y))
            step = L / k if i < k else 0
            total += step; covered += step if ok else 0
            if not ok:
                run += step; start = start or (x, y)
            else:
                if run >= 1.0:
                    gaps.append(dict(layer=t["layer"], from_=[round(start[0], 2), round(start[1], 2)], to=[round(x, 2), round(y, 2)], mm=round(run, 1)))
                run = 0.0; start = None
        if run >= 1.0:
            gaps.append(dict(layer=t["layer"], from_=[round(start[0], 2), round(start[1], 2)], to=[round(t["e"][0], 2), round(t["e"][1], 2)], mm=round(run, 1)))
    if total:
        ret[n] = dict(length_mm=round(total, 1), referenced_pct=round(100 * covered / total, 0), unreferenced_runs=sorted(gaps, key=lambda g: -g["mm"])[:4],
                      vias=sum(1 for v in G["vias"] if v["net"] == n))
        gaps_all += [dict(net=n, **g) for g in gaps]
emi["return_paths"] = ret
# D4 GND stitching: distance from the board's interior to the nearest GND via / GND through-hole pad
stitch = [(v["x"], v["y"]) for v in G["vias"] if v["net"] == "GND"] + [(p["x"], p["y"]) for p in G["pads"] if p["net"] == "GND" and p["attr"] in ("pth",)]
st = np.array(stitch)
both = gnd_fill["F.Cu"].intersection(gnd_fill["B.Cu"])
xmin, ymin, xmax, ymax = board.bounds
samples = []
for x in np.arange(xmin + 0.5, xmax, 1.0):
    for y in np.arange(ymin + 0.5, ymax, 1.0):
        if both.contains(Point(x, y)):
            d = np.min(np.hypot(st[:, 0] - x, st[:, 1] - y)); samples.append((d, x, y))
ds = np.array([s[0] for s in samples])
perim = []
inner = board.buffer(-1.0)
for ring in ([inner.exterior] if inner.geom_type == "Polygon" else [g.exterior for g in inner.geoms]):
    L = ring.length
    for s in np.arange(0, L, 1.0):
        p = ring.interpolate(s); d = np.min(np.hypot(st[:, 0] - p.x, st[:, 1] - p.y)); perim.append((d, p.x, p.y))
emi["stitching"] = dict(gnd_vias=sum(1 for v in G["vias"] if v["net"] == "GND"), points_sampled=len(samples),
                        max_distance_mm=round(float(ds.max()), 1), p95_mm=round(float(np.percentile(ds, 95)), 1),
                        worst=[[round(x, 1), round(y, 1), round(d, 1)] for d, x, y in sorted(samples, reverse=True)[:6]],
                        perimeter_max_mm=round(max(perim)[0], 1),
                        perimeter_worst=[[round(x, 1), round(y, 1), round(d, 1)] for d, x, y in sorted(perim, reverse=True)[:6]])
# D5 ESP32 antenna keep-out (footprint rule area)
ka = []
for f in G["footprints"]:
    for r in f["rule_areas"]:
        kp = unary_union([poly_from(rr) for rr in r["poly"]]).intersection(board)
        hits = []
        for l in LAYERS:
            for g, n, k, lab in feat[l]:
                if g.intersects(kp) and not (k == "pad" and lab["ref"] == f["ref"]):
                    hits.append(dict(layer=l, net=n, kind=k))
            fa = gnd_fill[l].intersection(kp).area
            hits.append(dict(layer=l, net="GND pour", kind="fill", area_mm2=round(fa, 1)))
        ka.append(dict(ref=f["ref"], keepout_on_board_mm2=round(kp.area, 1), keepout_bounds=[round(v, 1) for v in kp.bounds],
                       flags={k: r[k] for k in ("no_tracks", "no_vias", "no_pours", "no_pads")}, copper=hits))
emi["antenna_keepout"] = ka
# copper graph for routed path lengths
class Graph:
    def __init__(self):
        self.adj = collections.defaultdict(list)

    def add(self, a, b, w):
        self.adj[a].append((b, w)); self.adj[b].append((a, w))

    def dist(self, srcs, dsts):
        dsts = set(dsts); best = {s: 0.0 for s in srcs}; q = [(0.0, s) for s in srcs]
        while q:
            d, u = heapq.heappop(q)
            if u in dsts:
                return d
            if d > best.get(u, 1e9):
                continue
            for v, w in self.adj[u]:
                if d + w < best.get(v, 1e9):
                    best[v] = d + w; heapq.heappush(q, (d + w, v))
        return None


def net_graph(n):
    """Copper connectivity graph of one net. Nodes: segment end points (per layer), via centres, pads.
    Copper that touches is connected (overlapping ends, T-junctions, tracks running through pads or vias)."""
    gr = Graph()
    key = lambda l, p: (l, round(p[0], 3), round(p[1], 3))
    tr = [t for t in G["tracks"] if t["net"] == n]
    geo = [LineString([t["s"], t["e"]]) if t["s"] != t["e"] else Point(t["s"]) for t in tr]
    for t in tr:
        gr.add(key(t["layer"], t["s"]), key(t["layer"], t["e"]), math.dist(t["s"], t["e"]))

    def attach(node, at, t):
        """Connect a node located at point `at` to segment t (split at the projection of `at`)."""
        ls = LineString([t["s"], t["e"]]) if t["s"] != t["e"] else None
        if ls is None:
            gr.add(node, key(t["layer"], t["s"]), math.dist(at, t["s"])); return
        d0 = ls.project(Point(at)); q = ls.interpolate(d0)
        off = math.dist(at, (q.x, q.y))
        gr.add(node, key(t["layer"], t["s"]), off + d0)
        gr.add(node, key(t["layer"], t["e"]), off + (ls.length - d0))

    # segment end touching another segment of the same layer (overlap or T-junction)
    for i, t in enumerate(tr):
        for e in (t["s"], t["e"]):
            for j, u in enumerate(tr):
                if i == j or u["layer"] != t["layer"]:
                    continue
                if geo[j].distance(Point(e)) <= (t["w"] + u["w"]) / 2 - 1e-4:
                    attach(key(t["layer"], e), e, u)
    for v in G["vias"]:
        if v["net"] != n:
            continue
        vf, vb = key("F.Cu", (v["x"], v["y"])), key("B.Cu", (v["x"], v["y"]))
        gr.add(vf, vb, 1.6)
        for j, t in enumerate(tr):
            if geo[j].distance(Point(v["x"], v["y"])) <= v["d"] / 2 + t["w"] / 2 - 1e-4:
                attach(key(t["layer"], (v["x"], v["y"])), (v["x"], v["y"]), t)
    pnodes = collections.defaultdict(list)
    for idx, p in enumerate(G["pads"]):
        if p["net"] != n:
            continue
        node = ("PAD", p["ref"], p["num"], idx); pnodes[(p["ref"], p["num"])].append(node)
        for l in p["layers"]:
            g = pad_geo[(p["ref"], p["num"], l)]
            for j, t in enumerate(tr):
                if t["layer"] == l and geo[j].distance(g) <= t["w"] / 2 - 1e-4:
                    attach(node, (p["x"], p["y"]), t)
            for v in G["vias"]:
                if v["net"] == n and g.distance(Point(v["x"], v["y"])) < v["d"] / 2:
                    gr.add(node, key(l, (v["x"], v["y"])), math.dist((p["x"], p["y"]), (v["x"], v["y"])))
    return gr, pnodes


# D6 ESD protection placement: connector pin -> ESD device vs connector pin -> rest of the net
ESD = {"U1", "U6", "U7", "U8", "U9", "CR1", "CR2", "CR3", "D3", "D8"}
CONN = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
esd = []
for n in sorted({p["net"] for p in G["pads"] if p["ref"] in CONN}):
    if not n or n.startswith("unconnected") or n in ("GND",):
        continue
    members = [p for p in G["pads"] if p["net"] == n]
    cps = [p for p in members if p["ref"] in CONN]
    eps = [p for p in members if p["ref"] in ESD]
    others = [p for p in members if p["ref"] not in CONN and p["ref"] not in ESD]
    if not eps:
        esd.append(dict(net=n, connector=sorted({p["ref"] for p in cps}), esd=None, note="no ESD device on this net")); continue
    if n in ("3V3", "LDO_IN", "P+", "USB_VBUS", "SD_VDD"):
        continue
    gr, pn = net_graph(n)
    src = [x for p in cps for x in pn[(p["ref"], p["num"])]]
    d_esd = gr.dist(src, [x for p in eps for x in pn[(p["ref"], p["num"])]])
    loads = [p for p in others if p["ref"][0] in "UQ" or p["ref"] in ("F1", "F2", "F4", "F5")]
    d_oth = gr.dist(src, [x for p in loads for x in pn[(p["ref"], p["num"])]]) if loads else None
    esd.append(dict(net=n, connector=sorted({p["ref"] for p in cps}), esd=sorted({p["ref"] for p in eps}),
                    conn_to_esd_mm=round(d_esd, 1) if d_esd is not None else None, straight_conn_to_esd_mm=round(min(math.dist((a["x"], a["y"]), (b["x"], b["y"])) for a in cps for b in eps), 1), conn_to_load_mm=round(d_oth, 1) if d_oth is not None else None,
                    esd_first=(d_esd is not None and (d_oth is None or d_esd <= d_oth))))
# ESD device ground: GND pad -> nearest GND via
gv = [(v["x"], v["y"]) for v in G["vias"] if v["net"] == "GND"]
esd_gnd = []
for ref in sorted(ESD):
    for p in G["pads"]:
        if p["ref"] == ref and p["net"] == "GND":
            d = min(math.dist((p["x"], p["y"]), v) for v in gv)
            esd_gnd.append(dict(ref=ref, pad=p["num"], nearest_gnd_via_mm=round(d, 2)))
emi["esd"] = dict(nets=esd, gnd=esd_gnd)
# D7 decoupling distance: IC supply pin -> nearest capacitor pad on the same net (routed)
SUPPLY = [("U4", "3V3"), ("U13", "3V3"), ("U12", "3V3"), ("U14", "3V3"), ("U3", "3V3"), ("U3", "LDO_IN"), ("U2", "LDO_IN"),
          ("U2", "USB_VBUS"), ("U2", "P+"), ("U11", "USB_VBUS"), ("U11", "P+"), ("U10", "/LED_VIN"), ("J2", "EINK_3V3"),
          ("U5", "Net-(U5-VCC)"), ("L1", "EINK_3V3")]
dec = []
for ref, n in SUPPLY:
    pins = [p for p in G["pads"] if p["ref"] == ref and p["net"] == n]
    caps = [p for p in G["pads"] if p["net"] == n and p["ref"].startswith("C")]
    if not pins or not caps:
        continue
    gr, pn = net_graph(n)
    best = None
    for c in caps:
        d = gr.dist([x for p in pins for x in pn[(p["ref"], p["num"])]], pn[(c["ref"], c["num"])])
        if d is not None and (best is None or d < best[0]):
            best = (d, c["ref"])
    straight = min(math.dist((p["x"], p["y"]), (c["x"], c["y"])) for p in pins for c in caps)
    dec.append(dict(ic=ref, net=n, nearest_cap=best[1] if best else None, routed_mm=round(best[0], 1) if best else None, straight_mm=round(straight, 1)))
emi["decoupling"] = dec
# D8 parallel runs (crosstalk): same layer, near-parallel, edge gap <= 0.5 mm, aggressor vs victim
segs = [(t, LineString([t["s"], t["e"]])) for t in G["tracks"]]
by_layer = collections.defaultdict(list)
for t, ls in segs:
    by_layer[t["layer"]].append((t, ls))
pairs_x = collections.defaultdict(float)
where_x = {}
for l, lst in by_layer.items():
    tree = STRtree([ls for t, ls in lst])
    for i, (t, ls) in enumerate(lst):
        if t["net"] not in AGGR:
            continue
        for j in tree.query(ls.buffer(0.6)):
            u, lu = lst[j]
            if u["net"] not in VICT or u["net"] == t["net"]:
                continue
            a1 = math.atan2(t["e"][1] - t["s"][1], t["e"][0] - t["s"][0]); a2 = math.atan2(u["e"][1] - u["s"][1], u["e"][0] - u["s"][0])
            da = abs((math.degrees(a1 - a2) + 180) % 180)
            da = min(da, 180 - da)
            if da > 10:
                continue
            gap = ls.distance(lu) - t["w"] / 2 - u["w"] / 2
            if gap > 0.5:
                continue
            # overlap length of the projections
            ux = ((t["e"][0] - t["s"][0]), (t["e"][1] - t["s"][1])); L = math.hypot(*ux)
            if L < 1e-6:
                continue
            ux = (ux[0] / L, ux[1] / L)
            pr = lambda p: (p[0] - t["s"][0]) * ux[0] + (p[1] - t["s"][1]) * ux[1]
            lo, hi = sorted((pr(u["s"]), pr(u["e"])))
            ov = max(0.0, min(L, hi) - max(0.0, lo))
            if ov <= 0:
                continue
            key = (t["net"], u["net"], l)
            pairs_x[key] += ov
            if key not in where_x or gap < where_x[key][0]:
                where_x[key] = (gap, [round((t["s"][0] + t["e"][0]) / 2, 1), round((t["s"][1] + t["e"][1]) / 2, 1)])
emi["parallel_runs"] = sorted([dict(aggressor=k[0], victim=k[1], layer=k[2], parallel_mm=round(v, 1), min_gap_mm=round(where_x[k][0], 3), at=where_x[k][1])
                               for k, v in pairs_x.items() if v >= 2.0], key=lambda r: -r["parallel_mm"])
# D9 fast signals near the board edge
emi["fast_near_edge"] = sorted([dict(net=t["net"], layer=t["layer"], d=round(LineString([t["s"], t["e"]]).distance(edge) - t["w"] / 2, 2),
                                     at=[round((t["s"][0] + t["e"][0]) / 2, 1), round((t["s"][1] + t["e"][1]) / 2, 1)])
                                for t in G["tracks"] if t["net"] in FAST and LineString([t["s"], t["e"]]).distance(edge) - t["w"] / 2 < 1.0],
                               key=lambda r: r["d"])[:15]
# D10 USB pair
usb = {}
for n in ("DP", "DN"):
    tr = [t for t in G["tracks"] if t["net"] == n]
    usb[n] = dict(length_mm=round(sum(math.dist(t["s"], t["e"]) for t in tr), 2), widths=sorted({t["w"] for t in tr}),
                  vias=sum(1 for v in G["vias"] if v["net"] == n), layers=sorted({t["layer"] for t in tr}))
dp = unary_union([LineString([t["s"], t["e"]]) for t in G["tracks"] if t["net"] == "DP"])
dn = unary_union([LineString([t["s"], t["e"]]) for t in G["tracks"] if t["net"] == "DN"])
samples = [dp.interpolate(s) for s in np.arange(0, dp.length, 0.25)]
gaps = [p.distance(dn) for p in samples]
usb["centre_spacing_mm"] = dict(min=round(min(gaps), 3), median=round(float(np.median(gaps)), 3),
                                coupled_pct=round(100 * sum(1 for g in gaps if g < 0.6) / len(gaps), 0))
usb["skew_mm"] = round(abs(usb["DP"]["length_mm"] - usb["DN"]["length_mm"]), 2)
emi["usb"] = usb
RES["emi"] = emi
json.dump(RES, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=str)

# ----------------------------------------------------------------------------------------------------------------
# figures (back view = mirrored x, matching the 3D renders)
from PIL import Image, ImageDraw, ImageFont
S = 14.0
X0, Y0, X1, Y1 = board.bounds
W, H = int((X1 - X0) * S) + 40, int((Y1 - Y0) * S) + 40
P = lambda x, y: ((X1 - x) * S + 20, (y - Y0) * S + 20)
try:
    FNT = ImageFont.truetype("arial.ttf", 13); FB = ImageFont.truetype("arialbd.ttf", 15)
except OSError:
    FNT = FB = ImageFont.load_default()


def base(title):
    im = Image.new("RGB", (W, H + 70), (250, 250, 248)); d = ImageDraw.Draw(im, "RGBA")
    for l, col in (("F.Cu", (238, 214, 214)), ("B.Cu", (214, 222, 238))):
        g = gnd_fill[l]
        for p in (g.geoms if hasattr(g, "geoms") else [g]):
            d.polygon([P(*c) for c in p.exterior.coords], fill=col + (130,))
    for t in G["tracks"]:
        d.line([P(*t["s"]), P(*t["e"])], fill=(150, 150, 150) if t["layer"] == "B.Cu" else (200, 160, 160), width=max(1, int(t["w"] * S)))
    d.line([P(*c) for c in board.exterior.coords], fill=(0, 0, 0), width=2)
    d.text((10, H + 8), title, fill=(0, 0, 0), font=FB)
    return im, d


# figure 1: return-path gaps for fast nets + stitching worst spots + antenna keep-out
im, d = base("Fast signals: track runs >= 1 mm with no GND pour on the other layer (red); worst stitching gaps (blue rings); ESP32 antenna keep-out (purple)")
for g in gaps_all:
    d.line([P(*g["from_"]), P(*g["to"])], fill=(220, 0, 0), width=4)
for x, y, dd in emi["stitching"]["worst"]:
    cx, cy = P(x, y); r = dd * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 90, 255), width=2)
for f in G["footprints"]:
    for r in f["rule_areas"]:
        kp = unary_union([poly_from(rr) for rr in r["poly"]]).intersection(board)
        for p in (kp.geoms if hasattr(kp, "geoms") else [kp]):
            if not p.is_empty:
                d.polygon([P(*c) for c in p.exterior.coords], outline=(150, 0, 200), fill=(150, 0, 200, 40))
im.save(os.path.join(OUT, "fig_return_paths.png"), optimize=True)

# figure 2: high-voltage spacing hot spots + hot loops
im, d = base("High-voltage spacing below IPC-2221B (A6 for exposed pads, B4 for mask-covered copper; red) and switching loops (orange)")
for p in hv:
    if not p["ok"]:
        cx, cy = P(*p["at"]); d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=(220, 0, 0), width=3)
for lp in emi["loops"]:
    if "points" in lp:
        d.polygon([P(*c) for c in lp["points"]], outline=(255, 140, 0), width=3)
im.save(os.path.join(OUT, "fig_spacing_loops.png"), optimize=True)
print("done:", len(hv), "HV pairs,", sum(1 for p in hv if not p["ok"]), "below IPC (A6/B4),", sum(1 for p in hv if not p["ok_B2"]), "below B2;", len(near_edge), "near-edge items;", len(gaps_all), "unreferenced runs")
