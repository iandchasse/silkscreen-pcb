"""Hand-calculation checks used in BOARD_REVIEW.md (all inputs are datasheet values or board measurements).

python calc_budget.py
Measured track resistances come from net_resistance.py (1 oz copper assumed).
"""

# ---------------- Charger (TP4056, LCSC REV 2.4: IBAT = 1100*VPROG/RPROG, VPROG 0.9..1.1 V) ----------
R6 = 10e3
for vprog in (0.9, 1.0, 1.1):
    print(f"TP4056 ICHG with R6=10k, VPROG={vprog}: {1100*vprog/R6*1e3:.0f} mA")
print(f"SparkFun-hosted TP4056 sheet (1200 V/R): {1200/R6*1e3:.0f} mA; table value 130 mA")
print(f"R6 for 234 mA per schematic note: {1100/0.234/1e3:.2f} k (note says 4.7 k)")
print()

# ---------------- DW01A over-current trip (VEDI 130/150/170 mV) ----------------
# sense path: 2x FS8205A (19.5 typ/25 max mOhm @4.5V; 25/31.5 @2.5V) + R85||R86 (50 mOhm 1%) + traces
traces_min, traces_max = 0.006 + 0.004, 0.024 + 0.010  # /B- SENSE (8-24 mOhm) + GND pour/B- stub (est.)
r_min = 2 * 0.0195 * 0.9 + 0.0495 + traces_min
r_max = 2 * 0.0315 * 1.35 + 0.0505 + traces_max  # 2.5 V gate drive, +35 % at 85 C
print(f"DW01A sense resistance {r_min*1e3:.0f}..{r_max*1e3:.0f} mOhm -> OC trip "
      f"{0.130/r_max:.2f} A (min) .. {0.170/r_min:.2f} A (max); typ {0.150/(2*0.0195+0.050+0.015):.2f} A")
print()

# ---------------- Battery path drop / brown-out ----------------
path = {  # ohms, typical (max)
    "J5.2->Q3 trace": (0.018, 0.018), "Q3 AO3401A RDS(on) @-3.7V": (0.050, 0.070),
    "Q3->R27 trace": (0.0165, 0.0165), "R27 0R 0805": (0.010, 0.050), "R27->Q8 trace": (0.0044, 0.0044),
    "Q8 AO3401A": (0.050, 0.070), "P+ Q8->U2 trace": (0.020, 0.020), "TPS2116 RON": (0.040, 0.055),
    "LDO_IN U2->U3": (0.011, 0.011), "Q1 FS8205A x2": (0.045, 0.063), "R85||R86": (0.050, 0.0505),
    "/B-_SENSE + B- traces": (0.024, 0.040), "GND pour (est.)": (0.005, 0.010),
}
r_typ = sum(v[0] for v in path.values())
r_mx = sum(v[1] for v in path.values())
print(f"Board battery-path resistance J5 -> LDO input (incl. return): {r_typ*1e3:.0f} mOhm typ, {r_mx*1e3:.0f} mOhm max")
for i_load in (0.30, 0.50, 0.65):
    for r_cell in (0.15, 0.30):  # 500 mAh LiPo + pack PCM, typ/aged-or-cold
        vdo = 0.215 * i_load / 0.5 + 0.0  # TLV755 3.3 V: 215 mV max @ 500 mA (85 C), ~linear
        need = 3.3 + vdo + i_load * (r_typ + r_cell)
        need_mx = 3.3 + 0.238 * i_load / 0.5 + i_load * (r_mx + r_cell)
        print(f"  I={i_load:.2f} A, Rcell={r_cell:.2f}: cell OCV needed for 3V3 in regulation "
              f"{need:.2f} V (typ) / {need_mx:.2f} V (max)")
print()

# ---------------- LDO current budget (peaks, mA) ----------------
loads = {"ESP32-S3 Wi-Fi TX 802.11b 20.5 dBm (WROOM-1 Tab 6-4)": 355, "microSD write (HS mode, up to)": 100,
         "EPD booster during refresh (est. peak)": 50, "touch + RTC + misc": 10}
tot = sum(loads.values())
print(f"Coincident 3V3 peak {tot} mA vs TLV755 500 mA rating / ICL min 560 mA; with 200 mA SD card {tot+100} mA")
print()

# ---------------- Frontlight boost input current vs F3 (MF-FSMF010X) ----------------
vfb, rset = 0.200, 15.0
iled = vfb / rset
for vled in (14.0, 15.0):
    pout = (vled + vfb) * iled
    for vin in (3.0, 3.3, 3.6, 4.2, 5.0):
        for eff in (0.80,):
            iin = pout / eff / vin
            print(f"  VLED={vled:.0f} V ILED={iled*1e3:.1f} mA VIN={vin:.1f} V eta={eff:.2f}: IIN={iin*1e3:.0f} mA")
print("  MF-FSMF010X Ihold: 0.10 A @23C, 0.08 @40C, 0.07 @50C, 0.06 @60C; R 0.9..6 ohm; Itrip 0.30 A @23C")
print()

# ---------------- Deep-sleep budget (battery only, uA) ----------------
vbat = 3.8
sleep = {
    "TLV755 IGND (25 typ / 31 max @25C)": (25, 31),
    "ESP32-S3 deep sleep RTC timer (7-8 typ)": (8, 15),
    "DW01A ICC (3 typ / 6 max)": (3, 6),
    "TPS2116 IQ VIN2 (1.35 typ / 3.7 max 85C)": (1.35, 3.7),
    "BAT_MONIT R12+R10 2 MOhm": (vbat / 2.0, 4.2 / 2.0),
    "USB_STAT R70+R17 3 MOhm (ST low)": (3.3 / 3.0, 3.3 / 3.0),
    "R79+R80, R56+R57 (21 MOhm total)": (vbat / 11 + vbat / 10.01, 4.2 / 11 + 4.2 / 10.01),
    "LED_MONIT R39+R41 on LED_SW (~VIN-0.6 V)": ((vbat - 0.6) / 1.12, (4.2 - 0.5) / 1.12),
    "TPS923610 shutdown": (0.13, 0.5),
    "DS3231M on VBAT pin (IBATT 2-3.5 + conv avg 0.6)": (2.6, 4.1),
    "EPD panel deep sleep (Idslp 2-6)": (2, 6),
    "TP4056 BAT pin, VCC absent": (1, 2),
    "74LVC1G04 ICC": (0.1, 10 if False else 4),
}
t_typ = sum(v[0] for v in sleep.values())
t_max = sum(v[1] for v in sleep.values())
for k, v in sleep.items():
    print(f"  {k:52s} {v[0]:6.2f} {v[1]:6.2f}")
print(f"Deep-sleep total (no touch panel): {t_typ:.0f} uA typ, {t_max:.0f} uA max -> 500 mAh lasts "
      f"{500/(t_typ/1000)/24:.0f} d typ / {500/(t_max/1000)/24:.0f} d worst")
print()

# ---------------- USB_STAT divider ----------------
def par(*rs):
    return 1 / sum(1 / r for r in rs)

R70, R17, R67, R71 = 1e6, 2e6, 510e3, 200e3
print("USB_STAT states: batt-only", round(3.3 * R17 / (R70 + R17), 2), "V; charging",
      round(3.3 * R67 / (R70 + R67), 3), "V; done", round(3.3 * R71 / (R70 + R71), 3), "V")
# if TP4056 CHRG/STDBY clamp to an unpowered VCC (~0.5 V) when USB absent
v = (3.3 / R70 + 0 / R17 + 0.5 / R67 + 0.5 / R71) / (1 / R70 + 1 / R17 + 1 / R67 + 1 / R71)
print(f"  if CHRG/STDBY clamp to ~0.5 V when VBUS absent: USB_STAT = {v:.2f} V (would read as 'charging/done')")
print()

# ---------------- TPS2116 switchover ----------------
for vref in (0.92, 1.0, 1.08):
    print(f"TPS2116 PR1 switchover VBUS = {vref*(300+100)/100:.2f} V (VREF {vref})")
print()

# ---------------- ADC ladder levels (ATTEN3 effective range 0..2.9 V, +/-50 mV) ----------------
for name, rpu, taps in (("BUTTON_ADC_1", 10e3, {"RIGHT": 100, "LEFT": 5.6e3, "CONFIRM": 20e3, "BACK": 56e3}),
                        ("BUTTON_ADC_2", 10e3, {"DOWN1": 100, "UP1": 12e3, "DOWN2": 33e3, "UP2": 68e3})):
    print(name, {k: round(3.3 * r / (r + rpu), 3) for k, r in taps.items()}, "idle 3.3")
print()

# ---------------- LDO thermal (USB input) ----------------
for i in (0.05, 0.15, 0.30, 0.50):
    p = (5.25 - 3.3) * i
    print(f"TLV755 from VBUS 5.25 V at {i*1e3:.0f} mA: {p:.2f} W -> dT {p*100.8:.0f}..{p*231.1:.0f} C (RthJA 100.8 EVM .. 231.1 JEDEC)")
