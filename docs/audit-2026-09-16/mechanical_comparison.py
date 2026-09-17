"""Dimensioned drawings from KiCad/source vendor coordinates, not from models."""
import pathlib,json,math
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle,PathPatch
from matplotlib.path import Path
out=pathlib.Path(__file__).parent
d=json.loads((out/'board.json').read_text());f=next(f for f in d['footprints'] if f['ref']=='J7')
origin=f['pos']
def rel(p):return [p[0]-origin[0],p[1]-origin[1]]
tf=[(-3.30,-11.00),(4.70,-11.00)]
gct=[(-2.13,-11.42),(4.67,-11.42)]
fig,axes=plt.subplots(1,3,figsize=(14,5),gridspec_kw={'width_ratios':[1.6,1,1]})
ax=axes[0]
for p in f['pads']:
 if p['drill'][0]:continue
 x,y=rel(p['pos']);w,h=p['size'];ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor='#d9b269',edgecolor='#9e7b37'))
 if p['number']!='9':ax.text(x,y,p['number'],ha='center',va='center',fontsize=7)
# True capsule outline for the existing routed slot (not an ellipse).
def draw_holes(ax):
 for p in f['pads']:
  if not p['drill'][0]:continue
  x,y=rel(p['pos']);w,h=p['drill'];r=h/2;half=(w-h)/2
  if abs(w-h)<1e-6:ax.add_patch(Circle((x,y),r,facecolor='#dbe9fa',edgecolor='#215a98',lw=1.8))
  else:
   import numpy as np
   pts=[(x+half+r*math.cos(t),y+r*math.sin(t)) for t in np.linspace(-math.pi/2,math.pi/2,80)]+[(x-half+r*math.cos(t),y+r*math.sin(t)) for t in np.linspace(math.pi/2,3*math.pi/2,80)]
   ax.add_patch(plt.Polygon(pts,facecolor='#dbe9fa',edgecolor='#215a98',lw=1.8))
for a in axes:
 draw_holes(a)
 for name,posts,r,color in [('TF PUSH',tf,.40,'#25834a'),('GCT MEM2075',gct,.375,'#b93738')]:
  for i,(x,y) in enumerate(posts):
   a.add_patch(Circle((x,y),r,fill=False,edgecolor=color,lw=1.5,linestyle='--',label=name+' nominal peg' if i==0 else None));a.plot(x,y,'+',color=color)
 a.set_aspect('equal');a.grid(alpha=.2);a.set_xlabel('X relative to J7 anchor (mm)')
ax.set(xlim=(-7.4,11),ylim=(1.5,-13.4),title='Actual common lands + nominal pegs',ylabel='PCB Y relative to contact centers (mm)')
axes[1].set(xlim=(-4.3,-1.2),ylim=(-9.9,-12.5),title='Left routed slot: 2.25 × 1.05 mm')
axes[2].set(xlim=(3.5,5.9),ylim=(-9.9,-12.5),title='Right hole: Ø1.00 mm')
axes[2].legend(loc='lower center',fontsize=8)
fig.suptitle('J7 locating-hole audit — contact rows aligned; no connector placement offset applied',fontsize=13)
fig.text(.5,.01,'Blue = current drilled openings. Dashed outlines = nominal peg diameters; dimensional/drilling tolerances are additional.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.035,1,.94));fig.savefig(out/'sd-hole-overlay.png',dpi=190);plt.close(fig)
summary={'coordinate_system':'PCB top-view, relative to J7 contact-row anchor; B.Cu orientation included','board_holes':[{'center':rel(p['pos']),'drill':p['drill']} for p in f['pads'] if p['drill'][0]],'tf_nominal_pegs':tf,'gct_nominal_pegs':gct,'tf_translation_to_center_right_peg':[-.03,-.22],'gct_translation_to_center_right_peg':[0,.20],'tf_nominal_contact_land_vertical_overlap_after_translation_mm':1.6-.22,'gct_nominal_contact_land_vertical_overlap_after_translation_mm':1.3,'qualification':'Overlap refers to recommended land rectangles, not a measured solder joint. Requires tolerance/actual-lot check.','gct_keepout_board_rect':[57.27,67.47,77.05,81.10]}
(out/'sd-mechanical-comparison.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
# Thermal benchmarks, not an estimate of the actual board thetaJA.
import numpy as np
fig,ax=plt.subplots(figsize=(8,4.6));i=np.linspace(0,.5,100)
for th,color,label in [(100.8,'#287ca4','TI EVM benchmark: 100.8 °C/W'),(231.1,'#c0642e','TI JEDEC benchmark: 231.1 °C/W')]:
 ax.plot(i*1000,40+1.7*i*th,label=label,color=color)
ax.axhline(125,color='#555',ls='--',label='125 °C maximum recommended junction temperature')
ax.set(xlabel='Sustained 3.3 V load (mA)',ylabel='Calculated junction temperature (°C)',title='TLV75533P DBV: 5.0 V input, 40 °C ambient\nActual board thermal resistance is unmeasured',ylim=(35,245));ax.grid(alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'ldo-thermal-benchmarks.png',dpi=170)
