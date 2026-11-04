"""Refill all zones of a COPY of the board (never the original) and report fill-area changes.

KiCad Python: python.exe refill_copy.py <copy.kicad_pcb> <out_refilled.kicad_pcb>
"""
import sys

import pcbnew

src, dst = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(src)


def areas(board):
    out = {}
    for z in board.Zones():
        if z.GetIsRuleArea() or z.IsTeardropArea():
            continue
        for l in z.GetLayerSet().Seq():
            if pcbnew.IsCopperLayer(l):
                out[(z.GetNetname(), board.GetLayerName(l))] = z.GetFilledPolysList(l).Area() * 1e-12
    return out


before = areas(b)
filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
after = areas(b)
for k in sorted(before):
    print(k, "before %.2f mm2" % before[k], "after %.2f mm2" % after.get(k, -1))
pcbnew.SaveBoard(dst, b)
print("saved", dst)
