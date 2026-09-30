# Electrical / schematic audit (2026-09-30)

> Run on 2026-09-30 against the committed boards: Rev 1.0 = `aeb5b39` (as ordered), 1.01 = `3edd0c8`.
> Evidence paths (`A_trim/`, `C_fab/`, `layout/` ...) are under [`../evidence/`](../evidence/), a local-only pack (git-ignored).

> **Erratum (2026-09-30, after this report).** The cut-board GND reading in §4, §5 and §7 is wrong: the "C21 pad 2" item is
> not a ratsnest artefact. Reports [05](05_cut_board_gnd_geometry.md) and [06](06_cut_board_gnd_bridges.md) show, by two independent
> methods, that a cut leaves U3.2, U2.1, Q1.3 and their capacitors (the battery return) joined to the main GND only through one J7
> shell tab. KiCad's own connectivity agrees: on the trimmed 1.01 board the unconnected count is 1; one GND via at (86.48, 68.75),
> (75.03, 74.64) or (80.56, 92.22) takes it to 0, and a control via inside the main GND leaves it at 1
> (`evidence/gnd_via_test.py`). The "islands without a via" list in §4 is correct but does not test connectivity between groups.

Scope: HEAD 3edd0c8 (1.01) vs aeb5b39 (Rev 1.0 as ordered). Findings appended as confirmed.

## 1. Baseline
- Schematic silkscreen_pcb.kicad_sch at HEAD 3edd0c8 is identical to aeb5b39 (git diff empty; byte diff is CRLF only). sym-lib-table, fp-lib-table, .kicad_pro, KiCad/ libs also unchanged. So 1.0 and 1.01 share one netlist; 1.01 differs only in copper.
- ERC (kicad-cli 9, --severity-all) on HEAD copy: 0 errors, 41 warnings = 23 pin_to_pin (third-party symbols with Unspecified pin types), 8 lib_symbol_mismatch, 5 footprint_link_issues (CR1-3, F1, F2 filter metadata), 2 four_way_junction, 2 single_global_label (EINK_SW, TPS_SW_NODE, both real multi-node nets per sec.09), 1 multiple_net_names (TP_RST/PIN_3 on J4.3, FAB-13). Same count/kinds as AUTHOR_TODO round 3-7 ("41 warnings, all the known kinds"). No new item. NOTE only.

## 2. Netlist checks (HEAD netlist exported with kicad-cli; applies to 1.0 and 1.01 alike)
- USB-C J1: CC1->R3 5.1k->GND, CC2->R2 5.1k->GND (separate Rd, correct sink). VBUS A4/A9/B4/B9 -> CR1 SMF6.5CA -> F1 0805L100WR -> USB_VBUS. Shield 1M||1n to GND. D+/D- both rows -> U4 pin14 IO20 (D+) / pin13 IO19 (D-), U6 TPD4E1U06 on DP/DN/CC1/CC2. OK.
- TPS2116 U2: VIN1=USB_VBUS, VIN2=P+, VOUT(2,7)=LDO_IN, MODE=VIN1, PR1 = R38 300k / R51 100k -> 0.25*VBUS (1.25 V at 5 V; switchover ~4 V). ST -> R17 into the USB_STAT ladder. OK (USB-03 no-hysteresis closed as accepted).
- TLV75533 U3: IN=EN=LDO_IN, OUT=3V3, pin4 NC; C4 22u in, C6+C32 22u out. OK.
- TP4056 U11: TEMP=GND, PROG=R6 4.7k (1200/4.7k = 0.255 A, docs say ~0.23-0.25 A / "0.25 A default": OK), VCC=USB_VBUS, BAT=P+, CE=Q2 drain with R82 1M pull-down. OK.
- CE gate: Q9 BSS138 (S=B-, G=R79 100k from B+ / R80 1M to B-) pulls /DET_NODE to B-; Q2 AO3401A (S=3V3, G=/DET_NODE, R81 1M pull-up) drives CE. Reverse or absent pack -> CE low. Correct. 0 V / tripped pack cannot start charging (REC-A-02/REC-B-01, accepted and documented).
- DW01A U5 + FS8205A Q1: OD->Q1.6 (G1, S1=B-), OC->Q1.4 (G2, S2=GND), CS->R16 1k->GND(P-), GND pin=B-, TD open. New in aeb5b39: R83 100R P+->VCC, C7 0.1u VCC->B-, C34 2.2n CS->B- (CS filter tau 2.2 us, far below the DW01A 10 ms OC delay; does not shift the static CS thresholds). Topology matches the DW01A reference (VCC via 100R from the cell side, caps returned to the DW01A GND pin = B-). OK.
- Reverse-polarity pair: Q3 AO3401A (S=B+, G=R56 10k to B- / R57 10M to B+) and Q8 AO3401A (S=P+, G=GND) back-to-back via R27 0R. R57 10M bleed = 0.37-0.42 uA. OK.
- F2 0805L075WR sits between P+ and /P+_FUSE; /P+_FUSE = J6 pin 12 + CR3 (TSD05) only. So the fuse protects only the header, CR3 is on the header side. Matches HARDWARE.md ("CR3 now on /P+_FUSE"). HMI-01: RESOLVED in aeb5b39.
- USB_STAT ladder (x10 rescale): R70 1M pull-up, R17 2M (ST), R67 510k (CHRG), R71 200k (STDBY), C23 0.1u. Computed: battery-only 2.20 V, charging 1.12 V, done 0.55 V, idle/no charge 3.3 V; all inside the HARDWARE.md 13.1 windows (1.80-2.60 / 0.80-1.35 / 0.35-0.70 / >2.6). Battery-only ladder current 1.1 uA. OK.
- R57 10M present; R15 1M on GDR; C2 10u/25V; R14 2.2R; R83 100R; F2 0805L075WR; U14 RV-8263-C7 DNP + exclude-from-BOM with CLKOE(pin3)=GND, VDD=3V3, VSS=GND, SCL/SDA on the bus, INT/CLKOUT open. H1-H6 exclude-from-BOM. All as AUTHOR_TODO rounds 3-5 describe.
- ESP32-S3 (N16R8 per sec.04): EN = R7 10k / C5 1u (10 ms) + SW11 via R63 100R; IO0 = R13 10k pull-up, SW6 DNP via R64 100R; IO45/IO46/IO3 -> 33R -> J6.3/J6.2/J6.9 behind U8/U9 (HMI-02/MCU-04 LOW, inert on a PSRAM module); IO35-37 unconnected (octal PSRAM safe). ADC pins all ADC1 (IO1, IO2, IO4, IO8, IO9). IO42 -> ADIM (600k internal pull-down; MCU-08 optional external pull-down still open, LOW). OK.
- e-paper J2: pinout matches the Good Display 24-pin standard (2 GDR, 3 RESE, 5 VSH2 cap, 8 BS1=GND 4-wire, 9 BUSY, 10 RST, 11 DC, 12 CS, 13 SCK, 14 MOSI, 15/16 3V3, 17 GND, 18 VDD, 19 VPP, 20 VSH1, 21 PREVGH, 22 VSL, 23 PREVGL, 24 VCOM). Boost L1 47u from 3V3, Q4 IRLML6346 G=GDR S=RESE, R14 2.2R, R15 1M, D5 to PREVGH, C11/D4/D6 negative pump to PREVGL. OK.
- microSD J7: standard pinout; Q7 AO3401A high-side (S=3V3, D=SD_VDD), R40 100k gate pull-up (off by default), R78 1k from IO10, R77 100k bleed; 10k pull-ups to SD_VDD on CMD/DAT0-3; U1+U9 ESD. OK (SD-01 back-feed = firmware contract).
- Front light: U10 VIN=LDO_IN, ADIM=IO42, FB=R37 15R (0.2/15 = 13.3 mA, matches docs), VOUT=LED_SW (J3.1/J3.5, J6.5), Q5/Q6 BSS138 select W-/C- above R37, U12 74LVC1G04 inverter, R75 100k pull-down on COLOR_SEL; D3 SMAJ26A pad1(K)=LED_SW; C9 4.7u/50V; LED_MONIT = R39 1M / R41 120k (25.5 V -> 2.73 V). OK.
- RTC U13 DS3231MZ: VCC pin = GND, VBAT = 3V3 (VBAT-only by design, I2C usable on VBAT); INT/SQW unrouted (HMI-04 closed by design). I2C pull-ups R47/R48 2.2k. OK.
- Touch J4 default: 1 GND, 2 3V3 (R42), 3 TP_RST, 4 TP_INT (R44), 5 SDA (R46), 6 SCL (R52); alternates R43/R45/R58/R66 DNP+excluded. U7 clamps J4 pins 3-6 only (doc claim TRUE).
- Production files (aeb5b39 = HEAD): positions.csv = 165 fitted parts, no DNP part in it (R72, R74, SW6, U14, TP3-5, R43/45/58/66 all absent). jlc_bom.csv carries the DNP refs only as "DNP (standard build)" lines with no LCSC code; 0 LCSC mismatches vs the schematic for all fitted refs. HMI-V01 (exclude-from-BOM on R72/R74/SW6) remains a next-rev tidy-up, harmless as the files stand.

## 3. Doc-claim spot checks (50732e2, 6871962) -- all hold against the schematic values
- Ladder levels: IO1: SW2 0.033 V, SW3 1.19, SW8 2.20, SW9 2.80; IO4: SW1 0.033, SW4 1.80, SW5 2.53 (worst-case +/-1% = 2.521 V, 46 mV above 0.75*VDD), SW7 2.88. SW10: 3.0 V pressed (R62 10k/R76 100k), IO18 is an RTC GPIO. Only SW1/SW2/SW10 give a guaranteed GPIO wake: TRUE.
- R72 + R36 both fitted: IO18 idles at 3.3*100k/(10k+68k+10k+100k) = 1.76 V: TRUE. Order "remove R36 and R73, then fit R72 and R74": correct (avoids R73+R74 3V3-GND short and the 1.76 V idle).
- Open-load: OVP 24.25-25.5 V vs SMAJ26A VBR(min) 28.9 V, C9 is 50 V, tau = 4.7u x 1.12M = 5.3 s: TRUE.
- Sleep budget arithmetic: rows sum to 58.0 typ / 94.9 max; detector row = R81 3.3 + R82 3.3 + R79/R80 3.4 uA, BAT_MONIT 1.85, USB_STAT 1.1, R56/R57 0.37, LED_MONIT 2.9: all match the netlist values.
- IO47/IO48 = EPD_RST (R33, with R5 10k pull-up) / EPD_BUSY (R34): matches the first-article-check text.

## 4. Simulated x3 cut (y = 61.86; everything above removed: J6, U8, H1, F2, CR3, CR2, D8, SW10, D3; tracks with an end above removed; zone fills clipped; kicad-cli DRC unconnected items)
- Uncut 1.0 and uncut 1.01: 0 unconnected.
- Cut 1.0 (aeb5b39): 3V3 island {Q2.2 (+R81.2)} cut off from 3V3 -> CE can never go high on a cut-down 1.0 board = the known "x3 trim cuts charge enable" item (then noted in an untracked NOTICE.md, deleted in `3edd0c8`). Plus a dead 3V3 B.Cu stub (6.06 mm at 101.1,68.6) and one GND zone-to-zone island.
- Cut 1.01 (HEAD): Q2/R81 3V3 island GONE (the 1.01 trace works). Remaining: a dead 3V3 B.Cu stub (2.10 mm at 101.1,64.6, reported track-to-polygon) and GND: "C21 pad 2" reported unconnected from the GND zone (see follow-up below).
- Follow-up on the cut-board GND item: GND fill islands without a via are IDENTICAL in cut 1.0 and cut 1.01 (23 each, same bboxes/areas). New after the cut: two pad-less slivers (F.Cu 2.5 mm2 at x102.6-103.8 y61.9-64.4; B.Cu 5.7 mm2 at x83.7-87.2 y61.9-67.4) and a 130 mm2 F.Cu region tied only through H5's plated hole. No pad loses GND; C21.2 reaches the main F.Cu pour through its via, so the "C21 pad 2" pairing in the 1.01 DRC is only where the ratsnest drew the line to a pad-less sliver. Conclusion: cut-board GND is the same in 1.0 and 1.01 (see the erratum above), and 1.01 fixes the Q2/R81 3V3 island. The 2.1 mm dead 3V3 stub at the cut face (was 6.1 mm in 1.0) is part of the known "live nets cross the cut" hazard (MEC-02/LAY-02).
- 1.0 vs 1.01 diff (text-level): one GND via moved (99.30,65.60) -> (98.60,67.40); 3V3 B.Cu re-route along y 64.2-65.1 from x 82.9 to 101; PWR_BUTTON B.Cu re-route along y 65.9; LED_SW F.Cu jog near (98.7-102.9, 64.8-69.4). Nothing else in copper nets.
- Uncut DRC (project rules, errors+warnings): 1.0 and 1.01 identical (12 J1 clearance errors, same silk/thermal warnings, 0 unconnected, 0 parity) EXCEPT one new 1.01 warning: track_dangling, 3V3 B.Cu 0.141 mm segment (100.90,64.80)-(101.00,64.90); the next segment starts at (101.001,64.9) = 1 um endpoint mismatch. Copper overlaps (0.25 mm track), 0 unconnected, so electrically continuous. Cosmetic.

## 5. Findings
- [FIX-NOW] (1.01) 3V3 B.Cu route end at (101.001,64.9) vs (101.00,64.90): DRC track_dangling (new vs 1.0). No electrical effect; snap the endpoint when the board is next opened (no need to regenerate gerbers for it).
- [FIX-NEXT-REV] (1.0/1.01) Feed Q2 pin 2 (source) and R81 pin 2 from USB_VBUS instead of 3V3. Today, on battery, CE is driven to 3.3 V into the unpowered TP4056 (PWR-V02 back-feed path, covered only by a bring-up check) and R81 + R82 burn 3.3 uA each (6.6 uA = ~11% of the 58 uA floor, HARDWARE.md sleep table "Fix 4 detector" row). With a USB_VBUS source CE can only be high while the charger is powered, the reverse/absent-pack gating is unchanged (Q9 still decides), and a cut-down board no longer depends on a 3V3 trace to Q2/R81.
- [NOTE] (docs) HARDWARE.md has no first-article line for the TP4056 back-feed check (PWR-06/PWR-V02; sec.03 item 8; AUTHOR_TODO F): on battery only, USB_VBUS ~0 V, D2 dark, USB_STAT ~2.2 V. If the unpowered TP4056 status pins clamp, the battery-only USB_STAT reading falls to ~0.7-1.2 V (decodes as done/charging) and firmware cannot tell battery-only from USB. Add it beside the IO47/IO48 first-article check.
- [NOTE] (1.0 cut-down only) Simulated cut confirms the known x3 issue: Q2/R81 lose 3V3 -> no charging on a cut 1.0 board; 1.01 fixes it (verified).
- [NOTE] (both) Cut-board GND islands identical in 1.0 and 1.01; only pad-less slivers orphaned. See the erratum above.

## 6. Prior-review status (electrical)
RESOLVED in current files: HMI-01 (F2 0805L075WR on /P+_FUSE), BAT-02 (R83 100R + C7 0.1u), BOM-01 (R14 LCSC C22939), BOM-02 (C4/C6/C32 GRM21BR61E226ME44L / C45783), BOM-05/FAB-22/FAB-10 (bom.csv has no duplicate LCSC lines; v3 deleted), USB-01 (note >2.60 V; idle 3.3 V), round-3 "LED current wording" (13.3 mA in sch note and silk), U14 CLKOE (pin 3 = GND), R15 1M, C2 25 V, R57 10M, USB_STAT x10 rescale, PWR_FLAG on U5 VCC (ERC 0 errors).
ACCEPTED/DOCUMENTED: BAT-03, BAT-V04, USB-02/V02, USB-03, USB-04/V01, USB-05, PWR-01, PWR-07, SD-01, SD-02, SD-04, LED-02 (HARDWARE.md:865), LED-14, LED-V02, HMI-02, HMI-03, HMI-04, HMI-07, MCU-01, MCU-04, MCU-13, MCU-14, REC-B-03 (HARDWARE.md:1392), REC-A-01, REC-A-02/REC-B-01.
STILL OPEN: HMI-V01 (R72/R74/SW6 not exclude-from-BOM; harmless in current files), FAB-13 (PIN_3/TP_RST double label), MCU-08 (optional PWM_LED pull-down), BOM-06 (D8 NRND, kept), BOM-07 (DS3231MZ still fitted; RV-8263-C7 alternate DNP), PWR-06/PWR-V02/PWR-18 (bring-up measurement), LED-12 (J3 map, diode test), sleep budget unmeasured.

## 7. Addendum (after hand-off; background copper listing finished)
- GND copper around C21 (pads U3.2, C21.2, R77.2, J7.9; vias at 73.6,80.8 and 77.8,84.1) is identical in 1.0 and 1.01, which confirms that the C21 pairing in the cut DRC is a ratsnest artifact.
- Correction to the track_dangling detail: the new 1.01 3V3 route ends (100.90,64.80)->(101.00,64.90)->(101.001,64.90)->(101.101,65.00). That includes a separate 1 um segment, and the route T-joins the vertical (101.101,68.56)-(101.101,64.60) partway along it rather than at an endpoint. The vertical still continues (101.101,64.60)->(101.101,62.50) into the tongue (the 2.10 mm stub left on a cut board). Copper is continuous and DRC shows 0 unconnected, so this is cosmetic. Clean-up: delete the 1 um segment and end the route on a segment endpoint.

