"""Prototype the SCH-2 board edit on a scratch copy (never touches the repo).

  * Q2.2 and R81.2 move from 3V3 to USB_VBUS
  * the two short segments that already join them become USB_VBUS
  * the 3V3 tail that fed only those two pads is deleted, and the spine is trimmed back to the 3V3 link
  * one short USB_VBUS stub joins the Q2.2 pad to the USB_VBUS track below it
Usage (KiCad's bundled Python): "C:/Program Files/KiCad/9.0/bin/python.exe" proto_layout.py <src.kicad_pcb> <dst.kicad_pcb>
"""
import sys

import pcbnew

src, dst = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(src)
mm = pcbnew.FromMM
usb = b.FindNet('USB_VBUS')
assert usb is not None

# 1. pads
for ref, num in (('Q2', '2'), ('R81', '2')):
    pad = b.FindFootprintByReference(ref).FindPadByNumber(num)
    assert pad.GetNetname() == '3V3', (ref, pad.GetNetname())
    pad.SetNet(usb)

by_uuid = {}
for t in b.GetTracks():
    by_uuid[t.m_Uuid.AsString()[:8]] = t

# 2. the two short segments between R81.2 and Q2.2 keep their copper, change net
for u in ('08c1c457', '42601ea0'):
    by_uuid[u].SetNet(usb)

# 3. delete the dedicated 3V3 tail (R81.2 -> NE -> down the right side -> spine)
TAIL = ['20328915', '80b6194b', 'de30d9aa', 'ebfafa9e', '6bef1cfc', 'ab780e2a', '93de4fe7', 'a39d2a59', '7431d59c']
removed_len = 0.0
for u in TAIL:
    t = by_uuid[u]
    assert t.GetNetname() == '3V3'
    s, e = t.GetStart(), t.GetEnd()
    removed_len += ((s.x - e.x) ** 2 + (s.y - e.y) ** 2) ** 0.5 / 1e6
    b.Remove(t)
# trim the spine (101.101, 68.561 -> 62.501) back to the 3V3 link junction at y = 64.9
spine = by_uuid['f98f809a']
assert abs(spine.GetStart().y / 1e6 - 68.561462) < 1e-3 and abs(spine.GetEnd().y / 1e6 - 62.501) < 1e-3
removed_len += (68.561462 - 64.9)
spine.SetStart(pcbnew.VECTOR2I(mm(101.101), mm(64.9)))
print(f'3V3 copper removed: {removed_len:.2f} mm')

# 4. new stub: USB_VBUS node (93.57, 89.30) up to the lower edge of the Q2.2 pad (pad y 86.36..88.26)
stub = pcbnew.PCB_TRACK(b)
stub.SetStart(pcbnew.VECTOR2I(mm(93.57), mm(89.30)))
stub.SetEnd(pcbnew.VECTOR2I(mm(93.57), mm(88.26)))
stub.SetWidth(mm(0.25))
stub.SetLayer(pcbnew.B_Cu)
stub.SetNet(usb)
b.Add(stub)

# 5. refill zones so the GND pour respects the new copper
filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.BuildConnectivity()
pcbnew.SaveBoard(dst, b)
print('saved', dst)
