# GND bridge verification (V_bridge)

> Run on 2026-09-30 against the committed boards: Rev 1.0 = `aeb5b39` (as ordered), 1.01 = `3edd0c8`.
> Evidence paths (`A_trim/`, `C_fab/`, `layout/` ...) are under [`../evidence/`](../evidence/), a local-only pack (git-ignored).

Claim under test: cut at y=62 splits power-section GND from main GND; only J7 shell joins.

## Progress log

### Step 1 result (committed board 3edd0c8, saved fills, own method) - CONFIRMED split
Method: V_bridge/bridge.py. Every GND item (150 pads, 69 vias, 52 tracks/arcs, 67 fill islands of zones Z0 F/B + Z1 B) split at y=62 into kept (y>=62) and above pieces; same-layer polygon intersection (items +5 um, island-island pairs inflated too), cross-line contact where both sides touch y=62 at overlapping x, vias/PTH join layers. Saved fills clipped at exactly y=62 (no edge clearance -> optimistic, like a sawn board).
- Uncut board: U3.2 and U4 GND in one copper group (sanity OK).
- Kept board: group A = C25.1 C26.2 C3.2 C4.2 C6.2 H5.1 J7.9(x2 lands) Q1.3 R16.1 R51.2 R77.2 U2.1 U3.2 (13 pads, 12 via pieces, 3 track pieces; islands F.Cu x87.80-97.51 y62.00-79.45 124.4 mm2, B.Cu x81.44-97.30 y65.38-89.00 96.3 mm2, F.Cu x62.88-87.04 y79.95-97.45 72.0 mm2, B.Cu x67.75-82.92 y71.25-88.48 62.1 mm2, F.Cu x78.46-87.45 y86.91-94.62 29.3 mm2, 2 small B.Cu). Group B = 91 GND pads on 75 parts incl. U4, J1, C21, J7.6, other J7.9 lands. Identical to the earlier check's minor cluster.
- The ONLY copper join (uncut): F.Cu GND pour Z0/isl0 in the neck. Group A enters it on F.Cu at y=62, x 87.800-89.105 (between the P+ / 3V3 tracks at x~87.2-87.65 and the slot at x 89.49); group B enters it at x 86.001-86.999 (left of the P+ track). Joining copper = the tongue's F.Cu pour above the line (piece x 85.34-103.76, y 37.48-62.00, 324 mm2) - entirely at y < 62, removed by the cut. A tiny A-only sliver at x 95.37-95.85 y 61.49-62 is a dead end. No A-side crossing on B.Cu. Nothing joins A and B at y >= 62.

### Pre-change board 6871962 - same split (confirmed)
Same group A pad list (13 pads), same single join (F.Cu neck x 87.800-89.105 at y=62 into the tongue pour), same J7 land assignment. Not caused by 3edd0c8.

### Step 3 - J7 lands (committed and pre-change identical; GetFPRelativePosition has y negated vs the given table)
| land (fp) | size | board (x,y) | group |
|---|---|---|---|
| GCT (-6.33,2) | 1.1x2.4 | (56.72,82.60) | B |
| GCT (-6.33,11) | 1.1x2.4 | (56.72,73.60) | B |
| GCT (9.82,2) | 1.1x2.4 | (72.87,82.60) | B |
| GCT (9.82,11) | 1.1x2.4 | (72.87,73.60) | **A** |
| SHOU HAN (-6.15,1) | 1.3x1.6 | (56.90,83.60) | B |
| SHOU HAN (-6.15,10.6) | 1.3x2.3 | (56.90,74.00) | B |
| SHOU HAN (8.45,1) | 1.7x1.6 | (71.50,83.60) | B |
| SHOU HAN (9.35,10.6) | 1.3x2.3 | (72.40,74.00) | **A** (overlaps GCT (9.82,11)) |
| card-detect (-4.95,0) | 0.7x1.6 | (58.10,84.60) | B |
| J7.6 card VSS | 0.7x1.6 | (61.40,84.60) | B |
Both socket options: exactly one shell tab (the rear tab at fp x~9.4-9.8, y~10.6-11) on A, three on B -> either fitted shell joins A and B through that single tab. No socket option is shell-less on A.

### Step 2 - trim artefact audit (partial)
- No footprint anchored above y=62 has a pad reaching y>=62 and none anchored below has a pad above (no FP-STRADDLE); no GND via/PTH straddles the line; no GND track or arc crosses the line (the 12 crossing tracks are P+, 3V3 x2, LED_SW, C-, W-, R62, I2C_SDA/SCL, GPIO3/45/46, all PCB_TRACK) -> trim.py's anchor-based footprint delete, centre-based via delete and whole-arc delete cannot have removed GND copper that belongs below the cut.
- GND zones: Z0 (F+B, prio 0, whole board), Z1 (B.Cu, prio 1, x 46.7-49.1 y 122.5-124.9). Only one island-island contact between zones in the kept board (Z0 B isl14 / Z1, both group B) -> gnd4.py's omission of island-island contacts does not matter here.
- My kept graph uses the saved fills clipped at exactly y=62 with no edge clearance and still splits, so edge-clearance pinching (refill mode) and the notch are not the cause. KiCad's own DRC of cf_fix reports exactly one unconnected item: C21 pad 2 (B) <-> GND zone (A), plus 2 isolated_copper (= my 2 pad-less floating pieces).

### Fab-data cross-check (gerb_match.py)
All 15 F.Cu and 52 B.Cu saved GND fill islands match a G36/G37 region in the committed fab gerbers (C_fab/zip_new) by bbox (0.01 mm) and area (identical totals 3935.490 / 2687.282 mm2). The only unmatched gerber region is on B.Cu at x 89.8-103.5 y 40.0-44.1 (above the cut, not a fill). So the saved fills ARE the fabricated copper and the split is real on a sawn board.

### Where exactly the join is (uncut board, neck.py)
A's F.Cu reaches the line only at x 87.800-89.105 (1.3 mm neck between the F.Cu P+ track (87.40, 59.30)-(87.40, 66.90) w0.4 and the Edge.Cuts slot x 89.49-94.99 y 61.3-62.6). Restricting the F.Cu fill to a window y_top..62, A's neck and B's neck (x 86.00-87.00) first join for y_top between 59.0 and 58.5, i.e. the pour passes over the P+ via at (87.40, 59.30); widening the window to x 104.5 gives no earlier join. The GND via (89.50, 59.20) is also above the line. So every A-B path runs through copper at y < 59.0 (at least 3 mm above the cut), all removed. Side note: on the FULL board too, the power-section GND reaches the rest of GND only through this 1.3 mm F.Cu neck.

### Step 4 - severity
Battery path: J5.1 B- -> Q1 (FS8205A) pad 1; Q1 pad 3 = GND is in A. J5.2 B+ -> Q3 -> R27 (0R) -> Q8 (gate on GND[B]) -> P+ -> U2 VIN2 / U11 BAT. Loads and charger are in B: U4, EPD J2, SD J7.6, touch J4, RTC U13/U14, front-light driver U10 (TPS923610, GND pad 4 in B), charger U11 (TP4056, GND 1/3/EP in B, R6 = 4.7k, about 0.25 A), USB J1.
With either socket fitted, current through the one A-side shell tab and the steel shell:
1. all battery discharge return current (everything that runs from battery, incl. ESP32 Wi-Fi bursts and the front light; roughly 0.3-0.6 A peaks),
2. the full charge current (about 0.25 A continuous) while USB charges the battery,
3. the ground-pin current of LDO U3 and mux U2 plus the ripple and transient return of the A-side caps C3, C4, C6 (3V3 output), C25, C26. The LDO regulates against A, so the ESP32's 3V3 is referenced through the shell.
USB-only load current returns to J1 inside B and does not cross.
A shell of a few milliohms will probably work, but one solder tab carries all battery current. Neither socket option gives a dead board. The cut board is dead if J7 is not fitted or that tab is open: no battery return (no battery run, no charging), and U2/U3 ground floats (3V3 undefined even on USB).

### Step 5 - tie suggestion (not applied)
Drop GND vias (for example 0.6/0.3 mm) where A copper on one layer lies over B copper on the other layer, below the cut. Each point is the deepest point of the overlap and is at least the stated distance inside both fills:
- (87.1, 68.4): A B.Cu power pour over B F.Cu main pour, about 0.8 mm clear. About 3.6 mm from Q1 (86.45, 72.0), so it is the shortest tie for battery and charge return.
- (75.4, 75.0) (about 1.0 mm clear) or (74.7, 72.1) (about 0.85 mm clear): A B.Cu LDO-area island over B F.Cu. This ties the U3/C6 reference. The largest overlap's deepest point, (73.0, 77.8) at about 1.25 mm clear, sits under J7's body edge, so avoid it.
- Optional: (65.8, 96.05), A F.Cu over B B.Cu, about 1.1 mm clear, near J7 and U4. Also (89.4, 63.9), A F.Cu neck island over B's thin B.Cu strip, about 0.85 mm clear, 1.9 mm from the cut edge (weaker).
All points are the same net, so on the uncut board they are just extra stitching. Check for B.Cu part bodies, then refill and run DRC in the GUI.
Same-layer ties are not open space. The closest A-B approaches are 0.13 mm on B.Cu at (84.45, 92.8), where U11's EP is next to STDBY pad U11.6, and 0.19 mm on F.Cu at (73.55, 89.05), where the USB_STAT via (73.20, 88.70) and the SD_ACTIVATE track are in the way.

## VERDICT: CONFIRMED
The claim holds in full on 3edd0c8 and on 6871962. It was checked with an independent polygon method, KiCad's own DRC on the trimmed board and the fab gerbers. No surviving copper bridge exists. The only join is the J7 shell, and each socket option has exactly one tab on the isolated side.

