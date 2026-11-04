"""Export the board's copper for the thermal model (run with KiCad 9's Python).

Usage: "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe" export_copper.py <board.kicad_pcb> <copper.json>

Writes every F.Cu/B.Cu track, pad and zone fill (with holes), every via (diameter and drill), each footprint's
reference, side, position and courtyard, and the board outline with its cut-outs. Refill the zones in KiCad first:
the model uses the fills as saved.
"""
import json, sys

import pcbnew

mm = pcbnew.ToMM; FM = pcbnew.FromMM
LAYERS = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu}


def polys(ps, holes=True):
    out = []
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        ring = [[round(mm(o.CPoint(k).x), 4), round(mm(o.CPoint(k).y), 4)] for k in range(o.PointCount())]
        hs = []
        if holes:
            for j in range(ps.HoleCount(i)):
                h = ps.Hole(i, j)
                hs.append([[round(mm(h.CPoint(k).x), 4), round(mm(h.CPoint(k).y), 4)] for k in range(h.PointCount())])
        out.append([ring, hs])
    return out


def main(board_path, out_path):
    b = pcbnew.LoadBoard(board_path)
    D = {"items": [], "fps": [], "vias": []}
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            D["vias"].append(dict(net=t.GetNetname(), x=mm(p.x), y=mm(p.y), d=mm(t.GetWidth(pcbnew.F_Cu)), drill=mm(t.GetDrillValue())))
            continue
        for ln, lid in LAYERS.items():
            if t.GetLayer() == lid:
                s, e = t.GetStart(), t.GetEnd()
                D["items"].append(dict(kind="track", layer=ln, net=t.GetNetname(), x1=mm(s.x), y1=mm(s.y), x2=mm(e.x), y2=mm(e.y), w=mm(t.GetWidth())))
    for f in b.GetFootprints():
        f.BuildCourtyardCaches()
        crt = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd)
        D["fps"].append(dict(ref=f.GetReference(), value=f.GetValue(), side="B" if f.IsFlipped() else "F",
                             x=mm(f.GetPosition().x), y=mm(f.GetPosition().y), rot=f.GetOrientationDegrees(), crt=polys(crt, False)))
        for p in f.Pads():
            for ln, lid in LAYERS.items():
                if not p.IsOnLayer(lid):
                    continue
                ps = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(ps, lid, 0, FM(0.005), pcbnew.ERROR_INSIDE)
                D["items"].append(dict(kind="pad", layer=ln, net=p.GetNetname(), ref=f.GetReference(), pad=p.GetNumber(),
                                       drill=mm(p.GetDrillSize().x), poly=polys(ps, False)))
    for z in b.Zones():
        if z.GetIsRuleArea():
            continue
        for ln, lid in LAYERS.items():
            if z.IsOnLayer(lid):
                fp = z.GetFilledPolysList(lid)
                if fp.OutlineCount():
                    D["items"].append(dict(kind="zone", layer=ln, net=z.GetNetname(), teardrop=z.IsTeardropArea(), poly=polys(fp)))
    ol = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ol)
    D["outline"] = polys(ol)
    json.dump(D, open(out_path, "w"))
    print("items", len(D["items"]), "vias", len(D["vias"]), "footprints", len(D["fps"]), "outline cut-outs", [len(o[1]) for o in D["outline"]])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
