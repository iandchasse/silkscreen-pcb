| key | severity | status | evidence |
|---|---|---|---|
| cpl-j4-anchor-offset-0p73mm | high | OPEN | production/positions.csv J4 still 92.5,-126.0 rot 0; no anchor/offset field added |
| cpl-rot-u2-tps2116-sot583 | high | WON'T-FIX | owner: JLC DFM handles rotations; U2 still 270 in positions.csv, no FT Rotation Offset field |
| dev-header-table-clipped-by-chamfer | high | WON'T-FIX | owner accepted intentional; text box unchanged |
| f1-cr1-rating-vs-sustained-overvoltage-fault | high | WON'T-FIX | owner accepted sustained VBUS OV; F1/CR1 unchanged |
| stale-production-fab-outputs | high | PARTLY | zip+positions.csv (12:22) geometry == current Gerbers, moved parts match; but production/bom_JLC_upload_v4_optimized.csv (09-17) still L1 22u/C9 1u/R14 3; fabrication/BOM.csv + BOM_handbuild stale too |
| fix4-dead-pack-no-recovery | high | WON'T-FIX | owner accepted 0V pack no-recovery; Q9/R79-82 netlist unchanged |
| j5-battery-polarity-reversed-vs-common-lipo-convention | high | PARTLY | HARDWARE.md:309 states pin1=B-/pin2=B+; no +/- silk near J5 (only G/UP1 texts in area) |
| ldo-battery-headroom-brownout | high | WON'T-FIX | owner accepted LDO headroom |
| tp4056-epad-vias-under-paste | high | OPEN | U11 6 vias 0.5/0.2 at x83.5/84.7/85.9,y93.5/94.9 unchanged; paste windows still cover x83.5 and x85.9 vias |
| 3v3-label-zero-edge-clearance | medium | OPEN | '3v3' text (100.4,59.8) h1.2 unchanged; silk inventory identical |
| adc-button-ladder-exceeds-spec-range | medium | OPEN | R4/R28 10k, R18/19/20 5.6k/20k/56k, R11/35/36 12k/33k/68k unchanged |
| batt-path-traces-vs-ocp | medium | PARTLY | B- still 0.20 mm (35 mm), B+/P+/Q3-D/Q8-D 0.25 mm, R27 still 0R 0603; owner: widening optional |
| battery-path-thin-tracks-r27 | medium | PARTLY | same: B- 0.20, others 0.25, R27 0R 0603 unchanged (widening optional) |
| bottom-row-caret-marks-clipped-by-edge | medium | OPEN | '^' texts at (76,148.4),(88,148.2),(63,148.4),(51,148.4) unchanged |
| c9-led-boost-cout-below-1uf-effective | medium | FIXED | C9 now 4.7u/50V CL21A475KBQNNNE (C513770); BOM.md:94/259 + HARDWARE.md:724-747 still say 1 uF / not applied |
| dev-header-snipoff-live-nets-led-sw-i2c | medium | OPEN | Edge_Cuts Gerber identical to prev; no re-spacing at neck |
| edge-perforation-polys-0p5mm | medium | OPEN | Edge_Cuts Gerber geometry identical to prev; slots still ~0.5-0.6 mm tall |
| epd-boost-l1-r14-vs-panel-reference | medium | FIXED | owner changed L1 22u->47uH TYS5040470M (5x5 footprint), R14 3->2.2; first-article scope check still advisable |
| fix4-ce-pulldown-leakage-margin | medium | OPEN | R81/R82 still 1M; Q2 source still 3V3 |
| fix4-idle-drain-10ua | medium | PARTLY | docs corrected to ~10uA (HARDWARE.md:295); Q2 source/R81 still on 3V3 |
| j7-microsd-retention-peg-slot-clearance-too-tight-lcsc | medium | OPEN | NPTH slots still 2.25x1.5 and 1.05x1.5 |
| l1-switching-loop-sparse-return-vias | medium | OPEN | L1 area re-routed, 4 vias moved; still 1 GND via within 4 mm of L1, 1 near Q4, 0 near D5 |
| ldo-iq-and-divider-dominate-sleep-current | medium | OPEN | R10/R12 1M divider ungated, U3 unchanged |
| near-edge-passive-components | medium | OPEN | C1/R1/R2/R3/D2 not moved (only ref text moved inboard); process item for JLC proof |
| q1-prime-mpn-fs8205a-is-tssop8 | medium | FIXED | Q1 now FS8205A / EVVOSEMI, LCSC C2830320 (SOT-23-6) in part_fields.csv |
| q1-prime-mpn-is-tssop8 | medium | FIXED | same: manufacturer corrected to EVVOSEMI, TECH PUBLIC FS8205A C2830320 |
| r37-sense-return-fragile-not-isolated | medium | OPEN | R37.2 still DRC starved (1 spoke); 0 GND vias within 2.5 mm of R37; C9 GND island 6.1 mm2 unchanged |
| starved-thermal-decoupling-caps | medium | PARTLY | C10 fixed (moved, gone from DRC); C3,C4,C21,C26,C27,C29,C37 still starved (26 total) |
| starved-thermal-u3-ldo-compounds-tj-margin | medium | OPEN | U3.2 still in DRC starved-thermal |
| sw-tact-switch-force-and-life-difference | medium | OPEN | part_fields SW rows unchanged (MJTP1117 vs TS365ZJ); benign |
| tp4056-thermal-via-annular-thin | medium | OPEN | U11 vias still 0.5 pad / 0.2 drill |
| u3-ldo-thermal-on-usb | medium | OPEN | first-article measurement item; no layout change |
| u9-esd-ic-gnd-isolated-island | medium | OPEN | U9.2 B.Cu island 2.4 mm2 unchanged; still starved 1 spoke; no via added |
| usb4085-pad-pitch-zero-margin | medium | OPEN | J1 11 clearance DRC errors (0.15 vs 0.20) unchanged; accepted first-article risk |
| vbus-hotplug-overshoot-not-clamped | medium | OPEN | first-article scope test; C2/CR1/F1 unchanged |
| antenna-keepout-not-drc-enforced-plus-minor-fill-intrusion | low | OPEN | keepout rule area still (copperpour allowed) |
| bat-monit-1m-divider-leakage | low | OPEN | R10/R12 still 1M |
| button-ladder-top-step-near-adc-fullscale | low | OPEN | R36 68k / R20 56k unchanged |
| credits-box-also-overlaps-sw6 | low | OPEN | credits box unchanged; still DRC silk_over_copper at (46.3,118.6) |
| credits-orphan-punctuation-near-sw11 | low | OPEN | credits text identical (orphan ", ." remains) |
| d2-led-note-current-mismatch | low | PARTLY | HARDWARE.md now ~1.3-1.6 mA; schematic note still "2.5mA at 2.0Vf" |
| d3-only-polarised-tvs-check-orientation | low | OPEN | DFM-preview check; D3 unchanged |
| dangling-stub-prevgh | low | OPEN | PREVGH stubs 0.14 mm @ (82.7,127.2), 0.12, 0.04 mm still present |
| dev-header-note-overlaps-h1-sw10pad | low | OPEN | note box unchanged; DRC silk_overlap with PWR text and mask clip remain |
| dev-header-silk-note-clipped | low | OPEN | note box still DRC silk_edge/mask-clipped @84.2,52.5, 0.5/0.10 mm |
| docs-ao3419-vs-ao3401a | low | PARTLY | HARDWARE.md now AO3401A; DESIGN_REVIEW.md:162,235,245 still say AO3419 (199 has clarifying note) |
| dw01a-lockout-q8-gate-gnd | low | OPEN | no re-arm/lockout note found in HARDWARE.md |
| dw01a-no-vcc-series-r | low | OPEN | no series R on U5 VCC (netlist unchanged) |
| dw01a-puolop-vs-fortune | low | OPEN | no PUOLOP threshold documentation found |
| dw01a-vcc-no-series-r | low | OPEN | duplicate of dw01a-no-vcc-series-r; unchanged |
| empty-textbox-off-board-both-layers | low | OPEN | empty text boxes still on F.Silk and B.Silk @83.9,61.6 (DRC silk_edge) |
| epd-spi-inputs-float-in-deep-sleep | low | OPEN | firmware item; no hardware change |
| esd-gnd-pads-single-spoke-far-via | low | OPEN | U6.2,U7.2,U9.2,CR2.2 still starved 1 spoke; no via within 2.5 mm |
| fix4-highz-leakage-margin | low | OPEN | R81/R82 1M unchanged |
| frontlight-ext-led-min-vf-not-stated | low | OPEN | silk note unchanged (only <22V, >=15mA) |
| hardware-md-ce-table-stale | low | FIXED | HARDWARE.md:228 CE row now Q2 drain/R82 Fix-4 detector |
| hardware-md-rtc-lcsc-code-stale | low | FIXED | HARDWARE.md:914 now C107410 |
| j2-mount-pads-oversize-vs-hirose | low | OPEN | J2 unchanged (prototype assembled) |
| j6-header-body-overhangs-board-edge | low | OPEN | J6 unchanged; DRC silk_edge on J6 segments |
| j6-led-rail-next-to-low-voltage-pins | low | OPEN | pin5 LED_SW unchanged; HARDWARE.md:140 lists 24.5 V local net only |
| j6-table-bat-plus-vs-p-plus-naming | low | OPEN | J6 table still 'BAT+' (silk unchanged) |
| j7-microsd-locked-card-recessed-from-board-edge | low | OPEN | usability note; unchanged |
| j7-npth-short-slots | low | OPEN | slots 1.05x1.5 / 2.25x1.5 unchanged |
| l2-isat-below-tps923610-ilim | low | OPEN | L2 10u (same as prev snapshot); finding calls it acceptable |
| led-plus-header-short-unprotected | low | OPEN | no series R/PTC on LED_SW; netlist unchanged |
| mounting-hole-switch-proximity | low | OPEN | SW2/H4 positions unchanged; first-article |
| no-fiducials | low | OPEN | none added |
| post-cutoff-raw-cell-drain | low | OPEN | R56/R57/R79/R80 unchanged |
| protection-docs-and-symbol-metadata-stale | low | OPEN | CR1 symbol datasheet still tsd05c; D3/D8 descs unchanged |
| qr-module-size-inconsistent | low | OPEN | QR silk unchanged |
| refdes-pad-corner-overlaps-aggregate | low | PARTLY | R1/R2/R3/C1 refs moved off edge; U2/C4/R77/C21 overlaps remain (5 silk_overlap); L1 ref now clipped |
| short-tier-unreachable | low | OPEN | battery tracks unchanged; bench-test item |
| silk-clipped-by-soldermask | low | OPEN | J2 x3 segments + R78/R8/R77 refs still DRC silk_over_copper |
| stale-symbol-metadata-docs | low | PARTLY | BOM/HARDWARE now AO3401A; Q2/Q3/Q7/Q8 symbols still IRLML6402 desc/datasheet + Sim.* fields, Q4 desc BSS138 |
| sw11-actuator-inboard-facing-d2 | low | OPEN | SW11/D2 unchanged |
| touch-vdd-ungated-sleep-current | low | OPEN | firmware item; unchanged |
| tps923610-ovp-latch-absent-string | low | OPEN | firmware/docs item; unchanged |
| u12-no-jlc-footprint-model | low | OPEN | U12 rot 90 (270 in CPL) unchanged; check in JLC preview |
| u12-prime-mpn-mismatch-handbuild-bom | low | OPEN | BOM_handbuild_digikey.csv U12 SN74LVC1G04DBVR (TI) vs part_fields 74LVC1G04GV,125 (Nexperia) |
| usb-dp-dn-unreferenced-stretch-near-j1 | low | OPEN | routing unchanged (B.Cu diff only in L1 area) |
| usb-stat-no-battery-state-changed | low | OPEN | schematic note/docs unchanged |
| usb-vbus-c2-10v-rating | low | OPEN | C2 still 10u CL10A106KP8NNNC (10 V) |
| welcome-text-missing-noun | low | OPEN | welcome text unchanged ('12-pin accessory connected on the top...') |
