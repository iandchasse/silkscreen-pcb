"""Draws the e-fuse schematic for BOOST_EFUSE.md (schemdraw). Usage: python draw_efuse.py -> ../efuse_schematic.png

Explicit grid: y = 0 is LDO_IN, G (M1 gate) runs along the bottom at y = -8.6.
"""
import pathlib

import schemdraw
import schemdraw.elements as elm

OUT = pathlib.Path(__file__).parent.parent / 'efuse_schematic.png'
GY = -8.6  # gate line


def _lab(d, a, b, lab, loc):
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    off = {'right': (0.35, 0, 'left', 'center'), 'left': (-0.35, 0, 'right', 'center'),
           'top': (0, 0.45, 'center', 'bottom'), 'bottom': (0, -0.45, 'center', 'top')}[loc]
    d += elm.Label().at((mx + off[0], my + off[1])).label(lab, fontsize=10, halign=off[2], valign=off[3])


def R(d, a, b, lab, loc='right'):
    d += elm.Resistor().at(a).to(b)
    _lab(d, a, b, lab, loc)


def C(d, a, b, lab, loc='right'):
    d += elm.Capacitor().at(a).to(b)
    _lab(d, a, b, lab, loc)


def W(d, *pts, color='black'):
    for a, b in zip(pts, pts[1:]):
        d += elm.Line().at(a).to(b).color(color)


with schemdraw.Drawing(file=str(OUT), show=False, dpi=170) as d:
    d.config(fontsize=11, lw=1.4)
    # LDO_IN rail
    d += elm.Dot(open=True).at((0, 0)).label('LDO_IN\n(U2, C4, U3)', loc='left')
    W(d, (0, 0), (7.3, 0))
    for x in (2.45, 3.8, 4.6, 6.85):
        d += elm.Dot().at((x, 0))
    R(d, (7.3, 0), (9.3, 0), 'Rs  2.7 Ω, 1206 pulse-rated', loc='top')
    d += elm.Dot().at((9.3, 0)).label('S', loc='top')
    W(d, (9.3, 0), (11.9, 0))
    # M1: source at top, gate on the left, drain down to LED_VIN
    d += elm.PFet(bulk=True).at((11.9, 0)).anchor('source').reverse().label('M1 AO3401A', loc='right', fontsize=10)
    W(d, (11.9, -1.5), (11.9, -2.2), (13.8, -2.2))
    d += elm.Dot(open=True).at((13.8, -2.2)).label('LED_VIN\n(C12, L2, U10 VIN)', loc='right')
    # Q3: sense PNP, emitter on the rail before Rs, base to S through Rb3
    q3 = elm.BjtPnp(circle=True).at((7.6, -2.2)).anchor('base').left().flip().label('Q3\nMMBT3906', loc='left', fontsize=10)
    d += q3
    W(d, q3.emitter, (6.85, 0))
    R(d, (7.6, -2.2), (9.3, -2.2), 'Rb3 1 kΩ', loc='bottom')
    W(d, (9.3, -2.2), (9.3, 0))
    # delay: Rt into T, Ct and Rtb to ground
    R(d, q3.collector, (6.85, -5.2), 'Rt\n100 kΩ')
    d += elm.Dot().at((6.85, -5.2)).label('T', loc='right', ofst=(0.1, 0.25))
    C(d, (6.85, -5.2), (6.85, -7.0), 'Ct\n470 nF', loc='left')
    d += elm.Ground().at((6.85, -7.0))
    W(d, (6.85, -5.2), (9.7, -5.2))
    R(d, (9.7, -5.2), (9.7, -7.0), 'Rtb\n100 kΩ')
    d += elm.Ground().at((9.7, -7.0))
    # Q2: NPN, base from T, collector through Rc2 to Q1's base node B1
    q2 = elm.BjtNpn(circle=True).at((5.6, -5.2)).anchor('base').left().flip().label('Q2\nMMBT3904', loc='left', fontsize=10)
    d += q2
    W(d, (5.6, -5.2), (6.85, -5.2))
    d += elm.Ground().at(q2.emitter)
    R(d, q2.collector, (4.85, -2.9), 'Rc2\n220 kΩ', loc='left')
    # Q1: latch PNP, emitter on the rail, base on the right (B1), collector down to the gate line
    q1 = elm.BjtPnp(circle=True).at((3.2, -2.9)).anchor('base').left().flip().label('Q1\nMMBT3906', loc='left', fontsize=10)
    d += q1
    W(d, q1.emitter, (2.45, 0))
    R(d, (3.8, 0), (3.8, -2.0), 'Rb1\n1 MΩ', loc='left')
    C(d, (4.6, 0), (4.6, -2.0), 'Cb1\n1 nF')
    W(d, (3.8, -2.0), (4.6, -2.0))
    W(d, (3.8, -2.0), (3.8, -2.9))
    W(d, (3.2, -2.9), (4.85, -2.9))
    d += elm.Dot().at((3.8, -2.9)).label('B1', loc='bottom')
    # gate line G
    W(d, q1.collector, (2.45, GY), (10.53, GY), color='#0050a0')
    W(d, (10.53, GY), (10.53, -0.75), color='#0050a0')
    d += elm.Dot().at((2.45, GY)).label('G', loc='left')
    for x in (3.4, 4.5, 8.0):
        d += elm.Dot().at((x, GY))
    R(d, (3.4, GY), (3.4, GY - 1.8), 'Rg\n1 MΩ', loc='left')
    d += elm.Ground().at((3.4, GY - 1.8))
    C(d, (4.5, GY), (4.5, GY - 1.8), 'Cg\n10 nF')
    d += elm.Ground().at((4.5, GY - 1.8))
    R(d, (8.0, GY), (8.0, -5.2), 'Rf\n100 kΩ')
    d += elm.Dot().at((8.0, -5.2))
    d += elm.Label().at((11.6, -6.2)).label(
        'Q3 senses I·Rs (≈0.5 V)\nRt/Ct: ~5–14 ms delay\nQ2+Q1 latch: G → LDO_IN,\nM1 off; Rf holds it\nuntil LDO_IN < ~1 V', fontsize=10, halign='left')
