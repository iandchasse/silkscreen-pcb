"""Export the board's copper, footprints, zones and settings for the trace audit (run with KiCad's Python).

    "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe" export_geometry.py <board.kicad_pcb> <out.json>

Coordinates in mm (KiCad page coordinates: x right, y down). Polygons are outer rings plus holes.
"""
import json, sys
import pcbnew

mm = pcbnew.ToMM
R = lambda v: round(mm(v), 4)


def ring(chain):
    return [[R(chain.CPoint(k).x), R(chain.CPoint(k).y)] for k in range(chain.PointCount())]


def polys(ps):
    out = []
    for i in range(ps.OutlineCount()):
        out.append([ring(ps.Outline(i))] + [ring(ps.Hole(i, h)) for h in range(ps.HoleCount(i))])
    return out


b = pcbnew.LoadBoard(sys.argv[1])
ds = b.GetDesignSettings()
out = {"meta": {}, "outline": [], "tracks": [], "arcs": [], "vias": [], "pads": [], "footprints": [], "zones": []}
out["meta"] = dict(tent_vias_front=bool(ds.m_TentViasFront), tent_vias_back=bool(ds.m_TentViasBack),
                   mask_expansion=R(ds.m_SolderMaskExpansion), mask_min_web=R(ds.m_SolderMaskMinWidth),
                   copper_edge_clearance=R(ds.m_CopperEdgeClearance),
                   teardrop_zones=sum(1 for z in b.Zones() if z.IsTeardropArea()),
                   copper_layers=ds.GetCopperLayerCount(), board_thickness=R(ds.GetBoardThickness()))
ol = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ol)
out["outline"] = polys(ol)

for t in b.GetTracks():
    net = t.GetNetname()
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        out["vias"].append(dict(x=R(p.x), y=R(p.y), d=R(t.GetWidth(pcbnew.F_Cu)), drill=R(t.GetDrillValue()), net=net,
                                tented=bool(t.IsTented(pcbnew.F_Mask)) if hasattr(t, "IsTented") else None,
                                tent_f=int(t.GetFrontTentingMode()), tent_b=int(t.GetBackTentingMode())))
    elif t.Type() == pcbnew.PCB_ARC_T:
        s, m, e = t.GetStart(), t.GetMid(), t.GetEnd()
        out["arcs"].append(dict(layer=t.GetLayerName(), s=[R(s.x), R(s.y)], m=[R(m.x), R(m.y)], e=[R(e.x), R(e.y)], w=R(t.GetWidth()), net=net))
    else:
        s, e = t.GetStart(), t.GetEnd()
        out["tracks"].append(dict(layer=t.GetLayerName(), s=[R(s.x), R(s.y)], e=[R(e.x), R(e.y)], w=R(t.GetWidth()), net=net))

ATTR = {pcbnew.PAD_ATTRIB_SMD: "smd", pcbnew.PAD_ATTRIB_PTH: "pth", pcbnew.PAD_ATTRIB_NPTH: "npth", pcbnew.PAD_ATTRIB_CONN: "conn"}
for f in b.GetFootprints():
    f.BuildCourtyardCaches()
    p = f.GetPosition()
    fp = dict(ref=f.GetReference(), value=f.GetValue(), lib=str(f.GetFPID().GetLibItemName()), x=R(p.x), y=R(p.y),
              rot=round(f.GetOrientationDegrees(), 2), side="B" if f.GetLayer() == pcbnew.B_Cu else "F",
              dnp=bool(f.IsDNP()) if hasattr(f, "IsDNP") else False,
              crtyd_b=polys(f.GetCourtyard(pcbnew.B_CrtYd)), crtyd_f=polys(f.GetCourtyard(pcbnew.F_CrtYd)),
              rule_areas=[])
    for z in f.Zones():
        if z.GetIsRuleArea():
            fp["rule_areas"].append(dict(layers=[b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
                                         no_tracks=z.GetDoNotAllowTracks(), no_vias=z.GetDoNotAllowVias(), no_pads=z.GetDoNotAllowPads(),
                                         no_pours=(z.GetDoNotAllowZoneFills() if hasattr(z, "GetDoNotAllowZoneFills") else z.GetDoNotAllowCopperPour()),
                                         no_fps=z.GetDoNotAllowFootprints(), poly=polys(z.Outline())))
    out["footprints"].append(fp)
    for pad in f.Pads():
        pp = pad.GetPosition()
        d = dict(ref=f.GetReference(), num=pad.GetNumber(), net=pad.GetNetname(), attr=ATTR.get(pad.GetAttribute(), "?"),
                 x=R(pp.x), y=R(pp.y), sx=R(pad.GetSize().x), sy=R(pad.GetSize().y),
                 drill=R(max(pad.GetDrillSize().x, pad.GetDrillSize().y)), layers={},
                 zone_conn=int(pad.GetLocalZoneConnection()), fp_side=fp["side"])
        for l in ("F.Cu", "B.Cu"):
            lid = b.GetLayerID(l)
            if pad.IsOnLayer(lid):
                ps = pcbnew.SHAPE_POLY_SET(); pad.TransformShapeToPolygon(ps, lid, 0, pcbnew.FromMM(0.005), pcbnew.ERROR_INSIDE)
                d["layers"][l] = polys(ps)
        out["pads"].append(d)

for z in b.Zones():
    if z.GetIsRuleArea():
        out["zones"].append(dict(rule_area=True, name=z.GetZoneName(), layers=[b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
                                 poly=polys(z.Outline())))
        continue
    zd = dict(rule_area=False, net=z.GetNetname(), layers=[b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
              priority=z.GetAssignedPriority(), clearance=R(z.GetLocalClearance() or 0), min_thickness=R(z.GetMinThickness()),
              thermal_gap=R(z.GetThermalReliefGap()), thermal_spoke=R(z.GetThermalReliefSpokeWidth()),
              pad_conn=int(z.GetPadConnection()), island_removal=int(z.GetIslandRemovalMode()), min_island=round(z.GetMinIslandArea() / 1e12, 4),
              teardrop=bool(z.IsTeardropArea()), fills={})
    for lid in z.GetLayerSet().Seq():
        zd["fills"][b.GetLayerName(lid)] = polys(z.GetFilledPolysList(lid))
    out["zones"].append(zd)

json.dump(out, open(sys.argv[2], "w"))
print("tracks", len(out["tracks"]), "arcs", len(out["arcs"]), "vias", len(out["vias"]), "pads", len(out["pads"]),
      "footprints", len(out["footprints"]), "zones", len(out["zones"]))
