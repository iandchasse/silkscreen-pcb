"""Draws the 4-part limiter schematic for BOOST_LIMITER.md (schemdraw). Usage: python draw_limiter.py"""
import pathlib

import schemdraw
import schemdraw.elements as elm

OUT = pathlib.Path(__file__).parent.parent / 'limiter_schematic.png'

with schemdraw.Drawing(file=str(OUT), show=False, dpi=170) as d:
    d.config(fontsize=11, lw=1.4)
    d += elm.Dot(open=True).at((0, 0)).label('LDO_IN\n(U2, C4, U3)', loc='left')
    d += elm.Line().at((0, 0)).to((2.0, 0))
    d += elm.Resistor().at((2.0, 0)).to((4.6, 0))
    d += elm.Label().at((3.3, 0.55)).label('Rs 2.7 Ω, 1206', fontsize=10)
    d += elm.Dot().at((4.6, 0)).label('S', loc='top')
    d += elm.Line().at((4.6, 0)).to((6.6, 0))
    d += elm.PFet(bulk=True).at((6.6, 0)).anchor('source').reverse().label('M1 AO3401A', loc='right', fontsize=10)
    d += elm.Line().at((6.6, -1.5)).to((6.6, -2.2))
    d += elm.Line().at((6.6, -2.2)).to((8.6, -2.2))
    d += elm.Dot(open=True).at((8.6, -2.2)).label('LED_VIN\n(C12, L2, U10 VIN)', loc='right')
    # Q3: emitter on the LDO_IN side of Rs, base on S, collector to the gate
    q3 = elm.BjtPnp(circle=True).at((4.6, -1.6)).anchor('base').left().flip().label('Q3\nMMBT3906', loc='left',
                                                                                         fontsize=10)
    d += q3
    d += elm.Line().at(q3.emitter).to((1.6, q3.emitter[1]))
    d += elm.Line().at((1.6, q3.emitter[1])).to((1.6, 0))
    d += elm.Dot().at((1.6, 0))
    d += elm.Line().at((4.6, -1.6)).to((4.6, 0))
    d += elm.Line().at(q3.collector).to((q3.collector[0], -3.4))
    d += elm.Line().at((q3.collector[0], -3.4)).to((5.23, -3.4)).color('#0050a0')
    d += elm.Line().at((5.23, -3.4)).to((5.23, -0.75)).color('#0050a0')
    d += elm.Dot().at((q3.collector[0], -3.4)).label('G', loc='left')
    d += elm.Resistor().at((q3.collector[0], -3.4)).to((q3.collector[0], -5.2))
    d += elm.Label().at((q3.collector[0] + 0.35, -4.3)).label('Rg\n1 MΩ', fontsize=10, halign='left')
    d += elm.Ground().at((q3.collector[0], -5.2))
    d += elm.Label().at((6.0, -4.4)).label(
        'I·Rs ≈ 0.5 V turns Q3 on;\nQ3 lifts G and M1 limits the\ncurrent to ≈0.17–0.20 A (25 °C).\nNo latch, no delay, no bias current.',
        fontsize=10, halign='left')
