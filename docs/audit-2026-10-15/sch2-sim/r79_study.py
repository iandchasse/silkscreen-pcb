"""R79/R80 (Q9's gate divider across the raw cell) scaled up 3x and 10x, on the SCH-2+ wiring (R81 100k, R82 10k).

Reuses run_sch2.py's deck and only swaps the two divider resistors (Rdg = R79, Rdpd = R80), plus optional leakage
sources on Q9's gate node.  Needs LTspice (batch mode); writes under ./out (git-ignored).
Usage:  python r79_study.py static | thresh | leak
See docs/audit-2026-10-15/SCH-2_CHARGE_ENABLE.md section 8 for what it shows and what it does not cover.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import run_sch2 as R

_orig = R.deck


def deck(name, r79='100k', r80='1Meg', igl=None, iinj=None, **kw):
    d = _orig(name, **kw)
    assert 'Rdg bp ng 100k' in d and 'Rdpd ng bm 1Meg' in d
    d = d.replace('Rdg bp ng 100k', 'Rdg bp ng ' + r79).replace('Rdpd ng bm 1Meg', 'Rdpd ng bm ' + r80)
    extra = []
    if igl:
        extra.append('Igl ng bm ' + igl)      # leakage from Q9's gate to B-  (pulls the gate down)
    if iinj:
        extra.append('Iinj vbus ng ' + iinj)  # current injected into Q9's gate from USB_VBUS (pulls the gate up)
    return d.replace('.end\n', ''.join(e + '\n' for e in extra) + '.end\n')


R.deck = deck

PLUS = dict(topo='vbus', r81='100k', r82='10k')
VARIANTS = {'base_100k_1M': dict(r79='100k', r80='1Meg'),
            'x3_300k_3M': dict(r79='300k', r80='3Meg'),
            'x10_1M_10M': dict(r79='1Meg', r80='10Meg')}

which = sys.argv[1] if len(sys.argv) > 1 else 'static'
res = {}
if which == 'static':
    cases = {
        'A_discharge_3V7': dict(VB=3.7, USB=0, LOAD=.25),
        'A2_sleep_3V7_noload': dict(VB=3.7, USB=0, LOAD=0),
        'B_charge_3V7': dict(VB=3.7, USB=1, LOAD=0),
        'C_charge_2V5_vth1V5': dict(VB=2.5, USB=1, LOAD=0, vth_n=1.5),
        'D_reversed_USB': dict(VB=-4.2, USB=1, LOAD=0),
        'E_reversed_hotswap': dict(VB=-4.2, USB=1, LOAD=0, ic={'pp': 4.2}),
        'E2_latched_then_reversed': dict(VB=-4.2, USB=1, LOAD=0, ic={'pp': 4.2, 'bp': 3.5, 'ce': 3.3}),
        'F_nobatt_USB_ppcharged': dict(VB=0, USB=1, LOAD=0, nobatt=True, ic={'pp': 4.2}),
        'G_reversed_noUSB': dict(VB=-4.2, USB=0, LOAD=0),
    }
    for vn, vk in VARIANTS.items():
        for cn, ck in cases.items():
            n = f'S_{vn}_{cn}'
            res[n] = R.run(n, **PLUS, **vk, **ck)
    (R.OUT / 'r79_static.json').write_text(json.dumps(res, indent=1))
elif which == 'thresh':
    # lowest correctly oriented cell voltage that still enables CE, at the worst-case (highest) BSS138 Vth
    for vn, vk in VARIANTS.items():
        for vth in (1.3, 1.6):
            for vb in (1.4, 1.6, 1.8, 2.0, 2.2, 2.4):
                n = f'T_{vn}_vth{vth}_vb{vb}'
                res[n] = R.run(n, **PLUS, **vk, VB=vb, USB=1, LOAD=0, vth_n=vth)
    (R.OUT / 'r79_thresh.json').write_text(json.dumps(res, indent=1))
elif which == 'leak':
    # false disable: good cell at the 2.4 V DW01A cut-off, worst-case Vth 1.6 V, leakage from the gate to B-
    for vn, vk in VARIANTS.items():
        for il in ('0', '0.1u', '0.3u', '1u', '3u'):
            n = f'LD_{vn}_igl{il}'
            res[n] = R.run(n, **PLUS, **vk, VB=2.4, USB=1, LOAD=0, vth_n=1.6, igl=None if il == '0' else il)
    # false enable: reversed cell, and no cell, with USB present; best-case (lowest) Vth 0.8 V; current injected into the gate
    for vn, vk in VARIANTS.items():
        for il in ('0', '0.1u', '0.3u', '1u', '3u'):
            n = f'LE_rev_{vn}_iinj{il}'
            res[n] = R.run(n, **PLUS, **vk, VB=-4.2, USB=1, LOAD=0, vth_n=0.8, iinj=None if il == '0' else il)
            n = f'LE_nocell_{vn}_iinj{il}'
            res[n] = R.run(n, **PLUS, **vk, VB=0, nobatt=True, USB=1, LOAD=0, vth_n=0.8, iinj=None if il == '0' else il)
    (R.OUT / 'r79_leak.json').write_text(json.dumps(res, indent=1))
print(which, len(res), 'runs done')
