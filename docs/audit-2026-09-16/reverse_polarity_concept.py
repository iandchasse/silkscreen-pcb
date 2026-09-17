"""Run an illustrative LTspice DC check and draw the PROPOSED wiring.

Generic models: this does not qualify the named devices or the assembled PCB.
All simulator raw data stays in the Windows temporary directory.
"""
import json
import os
import pathlib
import re
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

out = pathlib.Path(__file__).parent
scratch = pathlib.Path(os.environ['LOCALAPPDATA']) / 'Temp/silkscreen-reverse-polarity-concept'
scratch.mkdir(parents=True, exist_ok=True)
exe = pathlib.Path(os.environ['LOCALAPPDATA']) / 'Programs/ADI/LTspice/LTspice.exe'
deck = (out / 'reverse-polarity-concept.cir').read_text()
labels = ['3.7 V discharge', '3.7 V charging', '2.5 V charging',
          'Reversed, USB absent', 'Reversed, USB present',
          '0 V pack, USB present', 'No battery, USB present', '2.5 V discharge']
rows = []
for case, label in enumerate(labels):
    path = scratch / f'case-{case}.cir'
    path.write_text(deck.replace('.step param CASE list 0 1 2 3 4 5 6 7', f'.param CASE={case}'))
    subprocess.run([str(exe), '-b', str(path)], cwd=scratch, timeout=30,
                   check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    raw_log = path.with_suffix('.log').read_bytes()
    log = raw_log.decode('utf-16') if raw_log.startswith((b'\xff\xfe', b'\xfe\xff')) else raw_log.decode('utf-8-sig')
    values = {m.group(1): float(m.group(2)) for m in re.finditer(
        r'^([a-z_]+):[^\n=]*=([-+0-9.eE]+)', log, flags=re.M)}
    assert len(values) == 6, log
    rows.append({'case': case, 'description': label, **values})
assert rows[0]['battery_charge_a'] < -.24
assert rows[7]['battery_charge_a'] < -.24
assert rows[1]['battery_charge_a'] > .2
assert rows[2]['battery_charge_a'] > .2
assert abs(rows[4]['pass_vgs']) < .01
assert abs(rows[4]['battery_charge_a']) < 10e-6
assert abs(rows[5]['battery_charge_a']) < 10e-6

result = {
    'status': 'Illustrative topology check; NOT a hardware qualification',
    'models': 'Handwritten generic VDMOS approximations, not manufacturer models',
    'excluded': ['DW01 and FS8205 operation and parasitics', 'Actual TP4056 control',
                 'Gate leakage and temperature corners', 'Hot-plug transients',
                 'Contact bounce, cable inductance, ESR corners, MOSFET SOA'],
    'dc_cases': rows,
    'no_battery_note': 'An enabled no-battery operating point exists: USB can hold B+ high through the pass channel. This is not a battery-presence detector. Do not assume an empty connector is de-energized.',
    'nominal_bias_uA': {str(v): (v/100000 + v/1010000)*1e6 for v in [2.5, 3.7, 4.2]},
    'added_bias_at_4V2_uA_vs_existing_divider': 42.0,
    'added_consumption_mAh_per_30_days': 42e-3 * 24 * 30,
}
(out / 'reverse-polarity-concept.json').write_text(json.dumps(result, indent=2), encoding='utf-8')

# Wiring diagram: component blocks expose package pin numbers explicitly.
fig, ax = plt.subplots(figsize=(13.5, 8.1))
fig.patch.set_facecolor('#f7fafc')
ax.set_facecolor('#f7fafc')
ax.set_xlim(0, 14)
ax.set_ylim(0, 8.7)
ax.axis('off')
ink = '#172b42'
wire = '#2e6686'
def line(points, color=wire, lw=2.2):
    ax.plot([p[0] for p in points], [p[1] for p in points], color=color, lw=lw, solid_capstyle='round')
def dot(x, y):
    ax.plot(x, y, 'o', color=wire, ms=5)
def text(x, y, value, size=11, ha='left', **kw):
    ax.text(x, y, value, fontsize=size, color=ink, ha=ha, va='center', **kw)
def box(x, y, w, h):
    ax.add_patch(FancyBboxPatch((x,y), w,h, boxstyle='round,pad=0.03,rounding_size=0.10',
                              facecolor='white', edgecolor=wire, linewidth=1.8))
def resistor(x1, y1, x2, y2, name, val, side='right'):
    cx, cy = (x1+x2)/2, (y1+y2)/2
    if y1 == y2:
        line([(x1,y1),(cx-.4,cy)])
        line([(cx+.4,cy),(x2,y2)])
        ax.add_patch(Rectangle((cx-.4,cy-.12),.8,.24,facecolor='white',edgecolor=wire,lw=1.7))
        text(cx,cy+.4,name+' '+val,10,ha='center')
    else:
        line([(x1,y1),(cx,cy+.38)])
        line([(cx,cy-.38),(x2,y2)])
        ax.add_patch(Rectangle((cx-.12,cy-.38),.24,.76,facecolor='white',edgecolor=wire,lw=1.7))
        text(cx+.25,cy,name+'\n'+val,10)

text(.3,8.25,'Battery polarity controls permission to charge',19,weight='bold')
text(.3,7.78,'Proposed revision • pin-level wiring • not applied to the KiCad design',11)
text(.55,6.5,'Raw B+',13,weight='bold')
line([(1.6,6.5),(4.4,6.5)])
box(4.4,5.8,3.4,1.45)
text(6.1,6.98,'Q8 · AO3419 · P-MOS',11,ha='center',weight='bold')
text(4.57,6.5,'D3',11)
text(7.63,6.5,'S2',11,ha='right')
# Body-diode direction: battery -> system. It blocks system -> reversed cell.
line([(5.2,6.5),(5.78,6.5)])
ax.add_patch(Polygon([[5.78,6.29],[5.78,6.71],[6.18,6.5]], closed=True,fc=wire,ec=wire))
line([(6.18,6.24),(6.18,6.76)])
line([(6.18,6.5),(7.0,6.5)])
text(6.1,6.04,'body diode →       G1 ↓',9,ha='center')
line([(7.8,6.5),(12.1,6.5)])
text(12.2,6.5,'P+',13,weight='bold')
text(10.55,7.05,'Charger BAT + system battery rail',10,ha='center')
line([(6.1,5.8),(6.1,5.1),(9.4,5.1)])
resistor(9.4,6.5,9.4,5.1,'Roff','100 kΩ')
dot(9.4,6.5); dot(6.1,5.1)
text(10.25,5.48,'Qdet OFF: pulls gate\nto source, Q8 OFF',11)
line([(6.1,5.1),(6.1,4.63)])
box(5.2,2.8,2.3,1.8)
text(6.34,4.37,'D3',10,ha='center')
text(6.34,3.87,'Qdet · N-MOS',11,ha='center',weight='bold')
text(6.34,3.5,'PMV40UN2',10,ha='center')
text(5.37,3.9,'G1',9)
text(6.34,2.98,'S2',10,ha='center')
line([(2.4,6.5),(2.4,3.9)])
dot(2.4,6.5)
resistor(2.4,3.9,4.4,3.9,'R56','10 kΩ')
line([(4.4,3.9),(5.2,3.9)])
resistor(4.45,3.9,4.45,1.6,'R57','1 MΩ')
dot(4.45,3.9)
line([(6.1,2.8),(6.1,1.6)])
text(.55,1.6,'Raw B−',13,weight='bold')
line([(1.65,1.6),(8.3,1.6)])
dot(4.45,1.6); dot(6.1,1.6)
box(8.3,1.13,2.2,.95)
text(9.4,1.6,'Existing Q1\nlow-side protection',10,ha='center')
line([(10.5,1.6),(11.8,1.6)])
text(11.9,1.6,'Board GND',12,weight='bold')
text(8.35,3.92,'Correct cell: detector ON → Q8 ON\nReversed cell: detector OFF → Q8 OFF',11,linespacing=1.8)
text(8.35,2.8,'Q3 leaves the series power path.\nRewire it for the detector, or use a new ref.',10)
text(.55,.6,'Keep B− distinct from board GND.  Roff is a starting value; qualify leakage, hot-plug and cutoff recovery.',11)
fig.tight_layout(pad=.5)
fig.savefig(out/'reverse-polarity-proposal.png',dpi=165,facecolor=fig.get_facecolor())
fig.savefig(out/'reverse-polarity-proposal.svg',facecolor=fig.get_facecolor())
plt.close(fig)
print(json.dumps(result,indent=2))
