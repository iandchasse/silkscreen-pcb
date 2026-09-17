import json,pathlib,math,collections,csv
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,Ellipse
from matplotlib.transforms import Affine2D
out=pathlib.Path(__file__).parent;root=out.parents[1]
d=json.loads((out/'board.json').read_text()); fs={f['ref']:f for f in d['footprints']}
colors={'GND':'#b1bdc2','3V3':'#e39b24','LDO_IN':'#2db975','USB_VBUS':'#ed4561','P+':'#bc5ac4','B+':'#9264c8','B-':'#606467','TPS_SW_NODE':'#eb3f2f','LED_SW':'#235cda','EINK_SW':'#bd3aa4','PREVGH':'#2aac63','PREVGL':'#2a88aa','Net-(Q5-S)':'#c29724','/RESE':'#dd9944','DP':'#cc3692','DN':'#3979c8'}
def plot(name,limits,refs=(),nets=None):
 fig,ax=plt.subplots(figsize=(12,9)); xmin,xmax,ymin,ymax=limits; selected=set(nets or [])
 for z in d['zones']:
  for poly in z['filled'].get('B.Cu',[]):
   pts=poly['outer']; ax.add_patch(Polygon(pts,facecolor=colors.get(z['net'],'#e7c891'),edgecolor='none',alpha=.55,zorder=0))
   for h in poly['holes']:ax.add_patch(Polygon(h,facecolor='white',edgecolor='none',zorder=.1))
 for t in d['tracks']:
  if not (xmin-2<=t['start'][0]<=xmax+2 and ymin-2<=t['start'][1]<=ymax+2) and not (xmin-2<=t['end'][0]<=xmax+2 and ymin-2<=t['end'][1]<=ymax+2):continue
  color=colors.get(t['net'],'#777777'); alpha=1 if not selected or t['net'] in selected else .20
  if t['kind']=='PCB_VIA':
   ax.add_patch(Ellipse(t['start'],t['width'],t['width'],facecolor=color,edgecolor='#222',alpha=alpha,zorder=4))
   ax.add_patch(Ellipse(t['start'],t['drill'],t['drill'],facecolor='white',zorder=5))
  else:
   ax.plot([t['start'][0],t['end'][0]],[t['start'][1],t['end'][1]],color=color,alpha=alpha,linewidth=max(.3,t['width']*450/(xmax-xmin)),linestyle='-' if t['layer']=='B.Cu' else '--',zorder=2)
 for f in d['footprints']:
  if not xmin-3<=f['pos'][0]<=xmax+3 or not ymin-3<=f['pos'][1]<=ymax+3:continue
  for p in f['pads']:
   x,y=p['pos'];w,h=p['size'];tr=Affine2D().rotate_deg_around(x,y,-p['rotation'])+ax.transData
   ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor=colors.get(p['net'],'#dfbb81'),edgecolor='#555',linewidth=.4,transform=tr,zorder=6))
   if p['drill'][0]: ax.add_patch(Ellipse((x,y),*p['drill'],facecolor='white',zorder=7))
   if f['ref'] in refs: ax.text(x,y,p['number'],fontsize=6,ha='center',va='center',zorder=8,clip_on=True)
  if not refs or f['ref'] in refs:ax.text(*f['pos'],f['ref'],fontsize=8,fontweight='bold',ha='center',va='bottom',color='#111',bbox=dict(facecolor='white',alpha=.8,edgecolor='none',pad=.3),zorder=9,clip_on=True)
 for e in d['edges']:
  if 'mid' not in e:ax.plot([e['start'][0],e['end'][0]],[e['start'][1],e['end'][1]],'k-',lw=1,zorder=10)
 ax.set(xlim=(xmin,xmax),ylim=(ymax,ymin),xlabel='PCB X (mm)',ylabel='PCB Y (mm)',title=name+' — top-view coordinates; solid B.Cu / dashed F.Cu')
 ax.set_aspect('equal');ax.grid(alpha=.15);fig.tight_layout();fig.savefig(out/(name+'.png'),dpi=170);plt.close(fig)
print('IMPORTANT COMPONENTS')
for ref in ['J1','J2','J3','J4','J5','J6','J7','U2','U3','U4','U5','U10','U11','U12','C9','C12','L2','R37','L1','Q4','Q1','Q3','Q8','SW2','SW3','SW8','SW9','D2']:
 f=fs[ref];print(ref,f['pos'],f['rotation'],f['layer'],'DNP',f['dnp'])
for name in ['3V3','LDO_IN','USB_VBUS','P+','B-','TPS_SW_NODE','LED_SW','EINK_SW','DP','DN','SD_CLK']:
 ts=[t for t in d['tracks'] if t['net']==name]; print(name,'length',round(sum(math.dist(t['start'],t['end']) for t in ts),3),'vias',sum(t['kind']=='PCB_VIA' for t in ts),'widths',collections.Counter(t['width'] for t in ts if t['kind']!='PCB_VIA'))
for a,pa,b,pb in [('U10','5','C9','2'),('U10','4','C9','1'),('U10','1','C12','2'),('U10','6','L2','2'),('U10','3','R37','1'),('U3','5','C6','1'),('U3','1','C4','1'),('U4','2','C32','1')]:
 x=next(p for p in fs[a]['pads'] if p['number']==pa);y=next(p for p in fs[b]['pads'] if p['number']==pb);print('PAD DISTANCE',a,pa,b,pb,round(math.dist(x['pos'],y['pos']),3))
plot('whole-board',(42,106,35,150))
for name,center,span,refs in [('led-loop','U10',12,['U10','L2','C9','C12','R37','Q5','Q6','U12']),('power-path','U3',24,['U2','U3','U11','Q1','Q3','Q8','U5','C3','C4','C6','C21','C25','C26']),('eink-loop','Q4',17,['Q4','L1','D4','D5','D6','C11','C10','R14','R15']),('sd-footprint','J7',26,['J7','U1','U9','Q7','C36','C37']),('usb-path','J1',22,['J1','U6','F1','CR1','C1','R1','D2'])]:
 x,y=fs[center]['pos'];plot(name,(x-span/2,x+span/2,y-span/2,y+span/2),refs)
# Fabrication Toolkit uses pad bounding-box centers for some footprints; comparing
# these to KiCad anchors would incorrectly report placement errors. Use a replay
# of the installed toolkit, including its rotation/position database, instead.
verification=json.loads((out/'production-verification.json').read_text())
(out/'geometry-metrics.json').write_text(json.dumps({'cpl_differences':verification['cpl_differences'],'cpl_count':verification['original_cpl_rows'],'footprint_count':len(fs),'method':'See verify_production.py and production-verification.json'},indent=2))
