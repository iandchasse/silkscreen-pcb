"""Steady-state thermal model of the board around the frontlight PTC F3, for calibrating the PTC study
(../../audit-2026-10-29/PTC_THERMAL.md). See ../BENCH_THEORY.md section 2.3.

Input: copper.json from export_copper.py.

Model: square cells of dx mm in a window around F3/U10, clipped to the board outline. Each cell has 7 nodes through
the board: the FR-4 is split into sublayers (thin ones at the surfaces), so heat crossing a narrow copper gap at the
surface is not over-counted; copper (35 um) sits on the two outer nodes; plated holes add their barrel to every
vertical link in their cell; both faces lose heat to ambient with a combined convection + radiation coefficient h.
Components' bodies are ignored.

Outputs, per watt (K/W):
  theta_F3   the board seen by F3: mean rise of its two pads with 1 W split between them;
  theta_U10  the board under U10: mean rise of U10's pads with 1 W in them;
  kappa      rise at F3's pads / rise at U10's pads with U10 heating (the study's coupling factor);
  and the same 0603 lands on a bare 1.6 mm board with two 20 mm traces (test-board stand-ins), and tied into
  10 x 10 mm pours (heavy copper).

Usage: python board_thermal_ml.py copper.json [h=12] [kxy=0.8] [kz=0.3] [plating_um=18] [dx=0.1] [win=40]
                                              [keepout=0] [tests=1]
  keepout=m removes pour copper within m mm of F3's pads on both layers (to try a keep-out without editing the board).
Needs numpy, scipy, pyamg, shapely and Pillow. About 2 minutes at win=40, 6 at win=70.
"""
import json, math, sys

import numpy as np
import scipy.sparse as sp
import pyamg
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union

K_CU, T_CU, T_BOARD = 385.0, 35e-6, 1.6e-3
SUB = np.array([0.06, 0.12, 0.25, 0.67, 0.25, 0.12, 0.06]) * 1e-3     # FR-4 sublayers, m (sum 1.53 mm)


def params(argv):
    p = dict(h=12.0, kxy=0.8, kz=0.3, plating=18e-6, dx=0.1, win=40.0, keepout=0.0, tests=1.0)
    for a in argv:
        k, v = a.split("=")
        if k == "plating_um":
            p["plating"] = float(v) * 1e-6
        else:
            p[k] = float(v)
    return p


def item_geom(it):
    if it["kind"] == "track":
        return LineString([(it["x1"], it["y1"]), (it["x2"], it["y2"])]).buffer(it["w"] / 2, cap_style=1, resolution=6)
    return unary_union([Polygon(r[0], r[1]).buffer(0) for r in it["poly"] if len(r[0]) > 2])


class Grid:
    def __init__(self, x0, y0, x1, y1, dx):
        self.x0, self.y0, self.dx = x0, y0, dx
        self.nx, self.ny = int(math.ceil((x1 - x0) / dx)), int(math.ceil((y1 - y0) / dx))

    def mask(self, geom):
        im = Image.new("L", (self.nx, self.ny), 0); d = ImageDraw.Draw(im)
        P = lambda pts: [((x - self.x0) / self.dx, (y - self.y0) / self.dx) for x, y in pts]
        for g in (geom.geoms if hasattr(geom, "geoms") else [geom]):
            if g.geom_type != "Polygon" or g.is_empty:
                continue
            d.polygon(P(g.exterior.coords), fill=255)
            for h in g.interiors:
                d.polygon(P(h.coords), fill=0)
        return np.asarray(im) > 127


def solve(board, cu_top, cu_bot, barrels, p, sources):
    """barrels: float[ny,nx], full-thickness barrel conductance per cell (W/K). sources: list of lists of
    (surface 'F'|'B', mask, watts). Returns the rise on both surfaces for each source set."""
    L = len(SUB)
    dxm = p["dx"] * 1e-3
    idx = -np.ones(board.shape, dtype=np.int64)
    n = int(board.sum()); idx[board] = np.arange(n)
    N = L * n
    rows, cols, vals = [], [], []
    diag = np.zeros(N)
    for l in range(L):
        g = np.full(board.shape, p["kxy"] * SUB[l])
        if l == 0:
            g = g + np.where(cu_top, K_CU * T_CU, 0.0)
        if l == L - 1:
            g = g + np.where(cu_bot, K_CU * T_CU, 0.0)
        off = l * n
        for dy, dx in ((0, 1), (1, 0)):
            a = board[: board.shape[0] - dy, : board.shape[1] - dx] & board[dy:, dx:]
            ia = idx[: board.shape[0] - dy, : board.shape[1] - dx][a] + off
            ib = idx[dy:, dx:][a] + off
            ga = g[: board.shape[0] - dy, : board.shape[1] - dx][a]; gb = g[dy:, dx:][a]
            G_ = 2 * ga * gb / (ga + gb)
            rows += [ia, ib]; cols += [ib, ia]; vals += [-G_, -G_]
            np.add.at(diag, ia, G_); np.add.at(diag, ib, G_)
    for l in range(L - 1):
        d = (SUB[l] + SUB[l + 1]) / 2
        gz = p["kz"] * dxm * dxm / d + barrels[board] * T_BOARD / d
        a = np.arange(n) + l * n; b = a + n
        rows += [a, b]; cols += [b, a]; vals += [-gz, -gz]
        diag[a] += gz; diag[b] += gz
    diag[:n] += p["h"] * dxm * dxm
    diag[(L - 1) * n:] += p["h"] * dxm * dxm
    rows.append(np.arange(N)); cols.append(np.arange(N)); vals.append(diag)
    A = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(N, N))
    ml = pyamg.smoothed_aggregation_solver(A, symmetry="symmetric", max_coarse=1000)
    outs = []
    for src in sources:
        q = np.zeros(N)
        for (side, m, w) in src:
            sel = idx[m & board]
            q[sel + (0 if side == "F" else (L - 1) * n)] += w / max(len(sel), 1)
        T = ml.solve(q, tol=1e-10, accel="cg", maxiter=600)
        TB = np.full(board.shape, np.nan); TB[board] = T[(L - 1) * n:]
        TF = np.full(board.shape, np.nan); TF[board] = T[:n]
        outs.append({"F": TF, "B": TB})
    return outs


def barrel_map(G, holes, p, shape):
    """Spread each plated barrel's conductance (k_cu * pi * d * t / board thickness) over the cells in its drill."""
    m = np.zeros(shape)
    for (x, y, drill) in holes:
        gtot = K_CU * math.pi * drill * 1e-3 * p["plating"] / T_BOARD
        ci, cj = (x - G.x0) / G.dx, (y - G.y0) / G.dx
        r = max(drill / 2 / G.dx, 0.5)
        cells = [(j, i) for j in range(int(cj - r - 1), int(cj + r + 2)) for i in range(int(ci - r - 1), int(ci + r + 2))
                 if 0 <= j < shape[0] and 0 <= i < shape[1] and (i + 0.5 - ci) ** 2 + (j + 0.5 - cj) ** 2 <= r * r]
        if not cells and 0 <= int(cj) < shape[0] and 0 <= int(ci) < shape[1]:
            cells = [(int(cj), int(ci))]
        for (j, i) in cells:
            m[j, i] += gtot / len(cells)
    return m


def real_board(D, p, centre=(48.5, 119.0)):
    outline = Polygon(D["outline"][0][0], D["outline"][0][1])
    w = p["win"] / 2
    win = box(centre[0] - w, centre[1] - w, centre[0] + w, centre[1] + w).intersection(outline)
    G = Grid(*win.bounds, p["dx"])
    board = G.mask(win)
    ko = None
    if p["keepout"] > 0:
        f3p = unary_union([item_geom(i) for i in D["items"] if i["kind"] == "pad" and i["ref"] == "F3"])
        ko = box(*f3p.bounds).buffer(p["keepout"], join_style=2)
    cu = {}
    for lay in ("F", "B"):
        geoms = []
        for it in D["items"]:
            if it["layer"] != lay:
                continue
            g = item_geom(it)
            if ko is not None and it["kind"] == "zone":
                g = g.difference(ko)
            geoms.append(g)
        geoms += [Point(v["x"], v["y"]).buffer(v["d"] / 2) for v in D["vias"]]
        cu[lay] = G.mask(unary_union([g for g in geoms if not g.is_empty and g.intersects(win)]).intersection(win))
    holes = [(v["x"], v["y"], v["drill"]) for v in D["vias"]]
    seen = set()
    for it in D["items"]:
        if it["kind"] == "pad" and it.get("drill", 0) > 0 and (it["ref"], it["pad"]) not in seen:
            seen.add((it["ref"], it["pad"])); c = item_geom(it).centroid; holes.append((c.x, c.y, it["drill"]))
    bar = barrel_map(G, holes, p, board.shape)
    f3 = [G.mask(item_geom(i)) for i in D["items"] if i["kind"] == "pad" and i["ref"] == "F3" and i["layer"] == "B"]
    u10 = G.mask(unary_union([item_geom(i) for i in D["items"] if i["kind"] == "pad" and i["ref"] == "U10" and i["layer"] == "B"]))
    res = solve(board, cu["F"], cu["B"], bar, p, [[("B", f3[0], 0.5), ("B", f3[1], 0.5)], [("B", u10, 1.0)]])
    f3m = f3[0] | f3[1]
    th_f3 = float(np.nanmean(res[0]["B"][f3m])); th_u10 = float(np.nanmean(res[1]["B"][u10]))
    return dict(theta_F3=th_f3, theta_U10=th_u10, kappa=float(np.nanmean(res[1]["B"][f3m])) / th_u10, cells=int(board.sum()))


def test_board(p, w, length=20.0, pours=False):
    """F3's lands (1.05 x 0.95 mm at 1.75 mm pitch) on a bare 1.6 mm board: two w-wide, 20 mm traces to 2 x 2 mm
    terminals, or (pours=True) each pad tied to a 10 x 10 mm copper area on both layers."""
    sx, sy = 2 * (0.875 + length + 1) + 4, 30.0
    G = Grid(0, 0, sx, sy, p["dx"])
    cx, cy = sx / 2, sy / 2
    board = G.mask(box(0, 0, sx, sy))
    pa = box(cx - 1.4, cy - 0.475, cx - 0.35, cy + 0.475); pb = box(cx + 0.35, cy - 0.475, cx + 1.4, cy + 0.475)
    if pours:
        B = [pa, pb, box(cx - 11.7, cy - 5, cx - 1.7, cy + 5), box(cx + 1.7, cy - 5, cx + 11.7, cy + 5),
             box(cx - 1.75, cy - 0.3, cx - 1.35, cy + 0.3), box(cx + 1.35, cy - 0.3, cx + 1.75, cy + 0.3)]
        F = [box(cx - 11.7, cy - 5, cx - 1.7, cy + 5), box(cx + 1.7, cy - 5, cx + 11.7, cy + 5)]
    else:
        B = [pa, pb, LineString([(cx - 0.875, cy), (cx - 0.875 - length, cy)]).buffer(w / 2),
             LineString([(cx + 0.875, cy), (cx + 0.875 + length, cy)]).buffer(w / 2),
             box(cx - 0.875 - length - 1, cy - 1, cx - 0.875 - length + 1, cy + 1),
             box(cx + 0.875 + length - 1, cy - 1, cx + 0.875 + length + 1, cy + 1)]
        F = []
    cuB = G.mask(unary_union(B)); cuF = G.mask(unary_union(F)) if F else np.zeros(board.shape, bool)
    ma, mb = G.mask(pa), G.mask(pb)
    res = solve(board, cuF, cuB, np.zeros(board.shape), p, [[("B", ma, 0.5), ("B", mb, 0.5)]])
    return float(np.nanmean(res[0]["B"][ma | mb]))


if __name__ == "__main__":
    D = json.load(open(sys.argv[1]))
    p = params(sys.argv[2:])
    print("params", p)
    r = real_board(D, p)
    print("board window: theta_F3 %.0f K/W, theta_U10 %.0f K/W, kappa %.2f (%d cells per layer)" % (r["theta_F3"], r["theta_U10"], r["kappa"], r["cells"]))
    if p["tests"]:
        for w in (0.25, 0.5, 1.0):
            print("test-board stand-in, %.2f mm traces: theta %.0f K/W" % (w, test_board(p, w)))
        print("heavy copper (pads into 10 x 10 mm pours): theta %.0f K/W" % test_board(p, 0, pours=True))
