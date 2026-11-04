"""Dump board geometry from silkscreen_pcb.kicad_pcb using KiCad's pcbnew module (read-only).

Run with KiCad's Python:
  "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe" board_dump.py <board.kicad_pcb> <out.json>
Coordinates are in mm, KiCad board frame (x right, y down).
"""
import json
import sys

import pcbnew

MM = 1e-6


def pt(p):
    return [round(p.x * MM, 4), round(p.y * MM, 4)]


def poly_set_to_list(ps):
    out = []
    for i in range(ps.OutlineCount()):
        outline = ps.Outline(i)
        ring = [pt(outline.CPoint(j)) for j in range(outline.PointCount())]
        holes = []
        for h in range(ps.HoleCount(i)):
            hole = ps.Hole(i, h)
            holes.append([pt(hole.CPoint(j)) for j in range(hole.PointCount())])
        out.append({"outer": ring, "holes": holes})
    return out


def main(path, out):
    b = pcbnew.LoadBoard(path)
    ds = b.GetDesignSettings()
    data = {"layers": {}, "footprints": [], "tracks": [], "vias": [], "zones": [], "texts": [], "edges": [],
            "copper_layers": b.GetCopperLayerCount(), "thickness_mm": ds.GetBoardThickness() * MM}
    for lid in range(pcbnew.PCB_LAYER_ID_COUNT):
        if b.IsLayerEnabled(lid):
            data["layers"][str(lid)] = b.GetLayerName(lid)
    for fp in b.GetFootprints():
        f = {"ref": fp.GetReference(), "value": fp.GetValue(), "pos": pt(fp.GetPosition()),
             "rot": fp.GetOrientationDegrees(), "layer": b.GetLayerName(fp.GetLayer()),
             "fpid": fp.GetFPIDAsString(), "dnp": bool(fp.IsDNP()), "exclude_bom": bool(fp.IsExcludedFromBOM()),
             "pads": []}
        try:
            cy = fp.GetCourtyard(fp.GetLayer() if fp.GetLayer() == pcbnew.F_CrtYd else pcbnew.B_CrtYd)
        except Exception:
            cy = None
        for lyr in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            try:
                ps = fp.GetCourtyard(lyr)
                if ps.OutlineCount():
                    f.setdefault("courtyard", {})[b.GetLayerName(lyr)] = poly_set_to_list(ps)
            except Exception:
                pass
        for pad in fp.Pads():
            shape = pcbnew.SHAPE_POLY_SET()
            lyrs = [b.GetLayerName(l) for l in pad.GetLayerSet().Seq()]
            cu = [l for l in pad.GetLayerSet().Seq() if pcbnew.IsCopperLayer(l)]
            poly = None
            if cu:
                pad.TransformShapeToPolygon(shape, cu[0], 0, int(0.001 / MM), pcbnew.ERROR_INSIDE)
                poly = poly_set_to_list(shape)
            f["pads"].append({
                "num": pad.GetNumber(), "net": pad.GetNetname(), "pos": pt(pad.GetPosition()),
                "size": [pad.GetSizeX() * MM, pad.GetSizeY() * MM], "attr": int(pad.GetAttribute()),
                "drill": [pad.GetDrillSizeX() * MM, pad.GetDrillSizeY() * MM], "layers": lyrs,
                "poly": poly, "zone_conn": int(pad.GetLocalZoneConnection()),
                "pinfunction": pad.GetPinFunction(),
            })
        data["footprints"].append(f)
    for t in b.GetTracks():
        cls = t.GetClass()
        if cls == "PCB_VIA":
            data["vias"].append({"pos": pt(t.GetPosition()), "drill": t.GetDrillValue() * MM,
                                 "dia": t.GetWidth(pcbnew.F_Cu) * MM, "net": t.GetNetname(),
                                 "netclass": t.GetNetClassName()})
        else:
            d = {"net": t.GetNetname(), "width": round(t.GetWidth() * MM, 4), "layer": b.GetLayerName(t.GetLayer()),
                 "start": pt(t.GetStart()), "end": pt(t.GetEnd()), "len": t.GetLength() * MM, "cls": cls,
                 "netclass": t.GetNetClassName()}
            if cls == "PCB_ARC":
                d["mid"] = pt(t.GetMid())
            data["tracks"].append(d)
    for z in b.Zones():
        zd = {"net": z.GetNetname(), "layers": [b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
              "priority": z.GetAssignedPriority(), "name": z.GetZoneName(), "keepout": bool(z.GetIsRuleArea()),
              "min_thickness": z.GetMinThickness() * MM, "clearance": z.GetLocalClearance() * MM if z.GetLocalClearance() is not None else None,
              "pad_conn": int(z.GetPadConnection()), "thermal_gap": z.GetThermalReliefGap() * MM,
              "spoke_width": z.GetThermalReliefSpokeWidth() * MM,
              "outline": poly_set_to_list(z.Outline()), "filled": {}}
        if z.GetIsRuleArea():
            pours = getattr(z, "GetDoNotAllowZoneFills", None) or getattr(z, "GetDoNotAllowCopperPour", None)
            zd["keepout_flags"] = {"tracks": z.GetDoNotAllowTracks(), "vias": z.GetDoNotAllowVias(),
                                   "pads": z.GetDoNotAllowPads(), "pours": pours() if pours else None,
                                   "footprints": z.GetDoNotAllowFootprints()}
        for l in z.GetLayerSet().Seq():
            if pcbnew.IsCopperLayer(l) and not z.GetIsRuleArea():
                try:
                    zd["filled"][b.GetLayerName(l)] = poly_set_to_list(z.GetFilledPolysList(l))
                except Exception as e:
                    zd["filled"][b.GetLayerName(l)] = str(e)
        data["zones"].append(zd)
    for d in b.GetDrawings():
        cls = d.GetClass()
        lname = b.GetLayerName(d.GetLayer())
        if cls in ("PCB_TEXT", "PCB_TEXTBOX"):
            data["texts"].append({"layer": lname, "text": d.GetText(), "pos": pt(d.GetPosition())})
        elif lname == "Edge.Cuts":
            sh = {"cls": cls, "shape": d.GetShapeStr() if hasattr(d, "GetShapeStr") else "",
                  "start": pt(d.GetStart()), "end": pt(d.GetEnd())}
            try:
                if d.GetShape() == pcbnew.SHAPE_T_ARC:
                    sh["mid"] = pt(d.GetArcMid())
                if d.GetShape() == pcbnew.SHAPE_T_CIRCLE:
                    sh["radius"] = d.GetRadius() * MM
                if d.GetShape() == pcbnew.SHAPE_T_POLY:
                    sh["poly"] = poly_set_to_list(d.GetPolyShape())
            except Exception:
                pass
            data["edges"].append(sh)
    # board outline polygon
    outline = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(outline)
    data["outline"] = poly_set_to_list(outline)
    for fp in b.GetFootprints():
        for item in fp.GraphicalItems():
            if item.GetClass() in ("PCB_TEXT", "PCB_TEXTBOX") and item.IsVisible() if hasattr(item, "IsVisible") else False:
                data["texts"].append({"layer": b.GetLayerName(item.GetLayer()), "text": item.GetText(),
                                      "pos": pt(item.GetPosition()), "fp": fp.GetReference()})
    json.dump(data, open(out, "w"), indent=0)
    print("footprints", len(data["footprints"]), "tracks", len(data["tracks"]), "vias", len(data["vias"]),
          "zones", len(data["zones"]), "texts", len(data["texts"]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
