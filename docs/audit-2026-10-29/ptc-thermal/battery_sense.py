"""DW01A over-current threshold with an added sense resistor Rs between Q1 pin 3 (S2) and the GND pour.

The DW01A trips (opens OD after 10-20 ms) when V(CS) - V(B-) > V_OIP = 120 / 150 / 180 mV. Today CS sees only Q1's two
channels plus ~10 mOhm of B- trace inside the loop (BAT-08). R16 already lands on the pour, i.e. after Rs, so
V(CS) = I x (R_Q1 + Rs). Usage: python battery_sense.py  -> battery_sense.json + printed tables.
"""
import json, pathlib

import numpy as np

HERE = pathlib.Path(__file__).parent
VOIP = (0.120, 0.150, 0.180)
VSIP_MIN = 1.00
# Q1 FS8205A: 19.5 typ / 25 max mOhm per FET at 4.5 V gate, 25 typ / 31.5 max at 2.5 V; the DW01A drives the gates at
# the cell voltage. Low corner: 0.8 x typ at 4.2 V plus 8 mOhm of trace. High corner: max at 3.0 V, x1.15 for 60 C,
# plus 12 mOhm of trace.
RQ_LO = 2 * 0.8 * 19.5e-3 + 8e-3
RQ_HI = 2 * 31.5e-3 * 1.15 + 12e-3
R_PATH = 0.40          # cell ESR + Q3 + Q8 + Q1 + trace up to P+ (Rs comes on top)
PEAK = 0.60            # coincident Wi-Fi + SD + frontlight + base on battery, the largest legitimate >10 ms draw
WORST_LEGIT = 0.96     # U3 at its 0.87 A max limit plus the frontlight: brief (inrush, card insertion), well under 10 ms


def inrush_cs_peak(v_cell, r_loop, rs, rq, c_p=11e-6, tau_f=1e3 * 2.2e-9):
    """Peak CS-B- voltage when a cell is plugged onto the empty P+ caps (C3 + C26), through R16 x C34."""
    r = r_loop + rs
    i0, tau_in = v_cell / r, r * c_p
    t = np.linspace(0, 20 * max(tau_in, tau_f), 20001)
    i = i0 * np.exp(-t / tau_in)
    v = np.zeros_like(t)
    dt = t[1] - t[0]
    for k in range(1, len(t)):
        v[k] = v[k - 1] + dt * (i[k - 1] * (rq + rs) - v[k - 1]) / tau_f
    return i0, float(v.max())


def study(rs):
    i_min = VOIP[0] / (RQ_HI + rs)
    i_typ = VOIP[1] / ((RQ_LO + RQ_HI) / 2 + rs)
    i_max = VOIP[2] / (RQ_LO + rs)
    rp = R_PATH + rs
    out = dict(rs=rs, i_trip_min=i_min, i_trip_typ=i_typ, i_trip_max=i_max,
               margin_peak=i_min / PEAK,
               drop_peak_mV=PEAK * rs * 1e3,
               # every short at or below this always trips (lowest cell 3.0 V, highest threshold)
               r_sure_trip=3.0 / i_max - rp,
               # every short above this never trips (4.2 V cell, lowest threshold)
               r_never_trip=4.2 / i_min - rp,
               # the most power a never-tripped short can take (at its window edge, 4.2 V)
               p_untripped_max=i_min * (4.2 - i_min * rp),
               p_rs_sustained=i_max ** 2 * rs)
    for c34, tag in ((2.2e-9, '2n2'), (100e-9, '100n')):
        worst = max(inrush_cs_peak(4.2, rl, rs, RQ_HI, tau_f=1e3 * c34)[1] for rl in (0.25, 0.30, 0.40))
        out[f'inrush_cs_V_{tag}'] = worst
    return out


def main():
    rows = [study(rs) for rs in (0.0, 0.050, 0.068, 0.082, 0.100, 0.120)]
    print(f'R_Q1 + trace: {RQ_LO * 1e3:.0f}-{RQ_HI * 1e3:.0f} mOhm')
    print('Rs     trip min/typ/max A   margin@0.6A  drop@0.6A  sure<=  never>=  P_untripped  P_Rs   CS inrush 2n2/100n')
    for r in rows:
        print(f"{r['rs']:.3f}  {r['i_trip_min']:.2f}/{r['i_trip_typ']:.2f}/{r['i_trip_max']:.2f}        "
              f"{r['margin_peak']:.2f}x       {r['drop_peak_mV']:3.0f} mV    {r['r_sure_trip']:5.2f}  "
              f"{r['r_never_trip']:5.2f}   {r['p_untripped_max']:.2f} W     {r['p_rs_sustained'] * 1e3:3.0f} mW  "
              f"{r['inrush_cs_V_2n2']:.2f}/{r['inrush_cs_V_100n']:.2f} V")
    (HERE / 'battery_sense.json').write_text(json.dumps(dict(rq=[RQ_LO, RQ_HI], rows=rows), indent=1))


if __name__ == '__main__':
    main()
