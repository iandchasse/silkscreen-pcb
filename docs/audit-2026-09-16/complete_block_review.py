"""Read-only block coverage, simple corner calculations and layout measurements.

Consumes exports whose source hashes are checked before use. This is not a SPICE
model, signal-integrity solver, certification test, or factory-order amendment.
"""
import pathlib, json, csv, hashlib, math, itertools, collections, heapq, re
import numpy as np
from matplotlib.path import Path as MPath
import pymupdf

out=pathlib.Path(__file__).parent; root=out.parents[1]
manifest=json.loads((out/'source-manifest.json').read_text())
for item in manifest:
    if not (root/item['path']).exists() and pathlib.Path(item['path']).name.startswith('_autosave-'):
        continue  # KiCad removes this transient copy on clean close; required source stays hashed.
    assert hashlib.sha256((root/item['path']).read_bytes()).hexdigest()==item['sha256'], item['path']+' changed; refresh exports'
d=json.loads((out/'board.json').read_text()); fs={f['ref']:f for f in d['footprints']}
rows=list(csv.DictReader((out/'component-review.csv').open(encoding='utf-8-sig')))
blocks={
 'USB connector/shield/CC': 'J1 F1 R1 R2 R3 C1',
 'USB ESD': 'U6 CR1',
 'Charger and USB indicator': 'U11 R6 R59 D2 C2 C3',
 'Battery connector, protection, polarity': 'J5 U5 Q1 Q3 Q8 R16 R27 R56 R57 C7',
 'Power mux': 'U2 R38 R51 C4 C25 C26',
 '3.3 V regulator': 'U3 C6 C21',
 'Battery ADC': 'R10 R12 C8',
 'USB status ADC': 'R17 R67 R70 R71 C23',
 'Processor, boot, reset, UART': 'U4 R7 R13 C5 C22 C32 C33 SW6 SW11 R63 R64 TP1 TP2',
 'SDMMC and power gating': 'J7 U1 Q7 R8 R9 R21 R22 R23 R24 R25 R26 R40 R53 R54 R55 R77 R78 C36 C37',
 'E-paper connector, power and logic': 'J2 Q4 L1 D4 D5 D6 R5 R14 R15 R29 R30 R31 R32 R33 R34 C10 C11 C13 C14 C15 C16 C17 C18 C19 C20',
 'Frontlight boost, selection and ADC': 'J3 U10 U12 Q5 Q6 L2 R37 R39 R41 R49 R50 R75 C9 C12 C24 C31 TP3 TP4 TP5',
 'Touch connector and links': 'J4 U7 R42 R43 R44 R45 R46 R52 R58 R66',
 'Buttons and alternate wake link': 'SW1 SW2 SW3 SW4 SW5 SW7 SW8 SW9 R4 R11 R18 R19 R20 R28 R35 R36 R60 R61 R72 R73 R74 C27 C28',
 'Power/wake button': 'SW10 R62 R76 C29',
 'Optional RTC': 'U13 C30',
 'Expansion and shared ESD': 'J6 U8 U9 D3 D8 CR2 CR3 R47 R48 R65 R68 R69',
 'Mounting': 'H1 H2 H3 H4 H5',
}
assignment={}; duplicates=[]
for block,refs in blocks.items():
    for ref in refs.split():
        if ref in assignment: duplicates.append(ref)
        assignment[ref]=block
assert not duplicates
assert set(assignment)=={r['Ref'] for r in rows}, (set(assignment)^{r['Ref'] for r in rows})
with (out/'block-coverage.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=['Ref','Block','Population','Value','Ordered MPN']);w.writeheader()
    w.writerows({'Ref':r['Ref'],'Block':assignment[r['Ref']],'Population':r['Population'],'Value':r['Schematic value'],'Ordered MPN':r['Ordered MPN']} for r in rows)

def pad(ref,number): return next(p for p in fs[ref]['pads'] if p['number']==str(number))
def distance(a,pa,b,pb): return math.dist(pad(a,pa)['pos'],pad(b,pb)['pos'])
distances={f'{a}.{pa} to {b}.{pb}':round(distance(a,pa,b,pb),3) for a,pa,b,pb in [
 ('U10',5,'C9',2),('U10',4,'C9',1),('U10',1,'C12',2),('U10',3,'R37',1),
 ('U3',1,'C4',1),('U3',5,'C6',1),('U3',5,'C21',1),('U4',2,'C32',1),('U4',2,'C22',1),
 ('U5',5,'C7',1),('U5',6,'C7',2),('Q4',2,'R14',2),('Q4',1,'J2',2),('R14',2,'J2',3),
 ('U12',5,'C24',1),('J7',4,'C37',2),('J7',4,'C36',2),('U11',4,'C2',1),('U11',5,'C3',1),
]}

# Branch-inclusive net geometry and copper resistance at an assumed 35 um/20 C.
# Does not model pads, zones, parallel routes, via resistance or skin effect.
net_metrics={}
for name in ['DP','DN','SD_CLK','SD_CMD','SD_DAT0','SD_DAT1','SD_DAT2','SD_DAT3','SPI_SCK','SPI_MOSI','/GDR','/RESE','EINK_SW','PREVGH','PREVGL','TPS_SW_NODE','LDO_IN','3V3','USB_VBUS','P+','B+','B-','SD_VDD']:
    ts=[t for t in d['tracks'] if t['net']==name]; segs=[t for t in ts if t['kind']!='PCB_VIA']
    net_metrics[name]={'branch_inclusive_length_mm':round(sum(math.dist(t['start'],t['end']) for t in segs),3),'vias':sum(t['kind']=='PCB_VIA' for t in ts),'widths_mm':sorted(set(t['width'] for t in segs)),'sum_segment_R_35um_20C_ohm':sum(1.724e-8*math.dist(t['start'],t['end'])*1e-3/(t['width']*1e-3*35e-6) for t in segs)}

# Track endpoints form a graph; join endpoints that lie inside the same pad.
# Pad span edges use physical centerline length; through-hole spans connect layers.
def route(net,startref,startpin,endref,endpin):
    ts=[t for t in d['tracks'] if t['net']==net]; nodes=set(); edges=collections.defaultdict(list)
    def key(pos,layer):return (round(pos[0],6),round(pos[1],6),layer)
    def edge(a,b,length,kind):
        nodes.update([a,b]);edges[a].append((b,length,kind));edges[b].append((a,length,kind))
    for t in ts:
        if t['kind']=='PCB_VIA':edge(key(t['start'],'F.Cu'),key(t['start'],'B.Cu'),0,'via')
        else:edge(key(t['start'],t['layer']),key(t['end'],t['layer']),math.dist(t['start'],t['end']),'track')
    # Some traces terminate off the via center but inside its annular copper.
    for t in ts:
        if t['kind']!='PCB_VIA':continue
        for n in list(nodes):
            if math.dist(n[:2],t['start'])<=t['width']/2+.00001:
                edge(key(t['start'],n[2]),n,math.dist(n[:2],t['start']),'via-pad')
    # Split segments at any existing endpoint lying exactly on them.
    for t in ts:
        if t['kind']=='PCB_VIA':continue
        a=np.array(t['start']); b=np.array(t['end']); v=b-a; den=float(v@v)
        if den==0:continue
        candidates=[]
        for n in list(nodes):
            if n[2]!=t['layer']:continue
            q=np.array(n[:2]);u=float((q-a)@v/den)
            if -.000001<=u<=1.000001 and np.linalg.norm(q-a-u*v)<.00001:candidates.append((u,n))
        candidates.sort()
        for (_,n1),(_,n2) in zip(candidates,candidates[1:]):edge(n1,n2,math.dist(n1[:2],n2[:2]),'track')
    padnodes={}
    for f in fs.values():
        for p in f['pads']:
            if p['net']!=net:continue
            angle=math.radians(p['rotation']);c=math.cos(angle);s=math.sin(angle); found=[]
            for n in list(nodes):
                if p['drill'][0]==0 and n[2]!=f['layer']:continue
                dx=n[0]-p['pos'][0];dy=n[1]-p['pos'][1]
                x=c*dx-s*dy;y=s*dx+c*dy
                if abs(x)<=p['size'][0]/2+.005 and abs(y)<=p['size'][1]/2+.005:found.append(n)
            center=key(p['pos'],f['layer']);padnodes.setdefault((f['ref'],p['number']),[]).append(center)
            for n in found:edge(center,n,math.dist(center[:2],n[:2]),'pad')
    starts=padnodes.get((startref,str(startpin)),[]);ends=set(padnodes.get((endref,str(endpin)),[]))
    queue=[(0,n,0,[]) for n in starts];heapq.heapify(queue);done=set()
    while queue:
        length,n,vias,path=heapq.heappop(queue)
        if n in done:continue
        done.add(n)
        if n in ends:return {'length_mm':round(length,3),'vias':vias,'path':path+[n]}
        for other,w,kind in edges[n]:
            if other not in done:heapq.heappush(queue,(length+w,other,vias+(kind=='via'),path+[n]))
    return {'error':'No graph path; centerline approximation did not connect pads'}

routes={}
for net,ref,pin,end,epin in [('DP','J1','A6','U4','14'),('DP','J1','B6','U4','14'),('DN','J1','A7','U4','13'),('DN','J1','B7','U4','13'),('/RESE','Q4','2','R14','2'),('/RESE','R14','2','J2','3'),('/GDR','Q4','1','J2','2'),('SD_CLK','R24','2','J7','5'),('SD_CMD','R23','2','J7','3'),('SD_DAT0','R25','2','J7','7'),('SD_DAT1','R26','2','J7','8'),('SD_DAT2','R21','2','J7','1'),('SD_DAT3','R22','2','J7','2')]:
    routes[f'{net}: {ref}.{pin}-{end}.{epin}']=route(net,ref,pin,end,epin)

# Ground-zone projection is only a screening metric, not an impedance/return-path
# proof: same-layer ground and ground traces/pads are deliberately not counted.
polys={layer:[] for layer in ['F.Cu','B.Cu']}
for z in d['zones']:
    if z['net']!='GND' or z['keepout']:continue
    for layer,ps in z['filled'].items():
        for p in ps:polys[layer].append((MPath(p['outer']),[MPath(h) for h in p['holes']]))
ground_projection={}
for net in ['DP','DN','SD_CLK','SD_CMD','SD_DAT0','SD_DAT1','SD_DAT2','SD_DAT3','SPI_SCK','/GDR','/RESE']:
    total=covered=0;gaps=[]
    for t in d['tracks']:
        if t['net']!=net or t['kind']=='PCB_VIA':continue
        length=math.dist(t['start'],t['end']);n=max(1,math.ceil(length/.05))
        samples=np.array([np.array(t['start'])+(np.array(t['end'])-t['start'])*(i+.5)/n for i in range(n)])
        layer='F.Cu' if t['layer']=='B.Cu' else 'B.Cu'; mask=np.zeros(n,dtype=bool)
        for outer,holes in polys[layer]:
            inside=outer.contains_points(samples)
            for h in holes:inside&=~h.contains_points(samples)
            mask|=inside
        total+=length;covered+=sum(mask)*length/n
        if np.mean(mask)<.5 and length>.2:gaps.append({'layer':t['layer'],'start':t['start'],'end':t['end'],'length_mm':round(length,3)})
    ground_projection[net]={'length_mm':round(total,3),'opposite_GND_zone_percent':round(100*covered/total,1) if total else None,'segments_less_than_half_covered':gaps}

adc={}
for name,pull,branches in [('BUTTON_ADC_1',10000,[100,5600,20000,56000]),('BUTTON_ADC_2',10000,[100,12000,33000,68000])]:
    adc[name]=[]
    for r in branches:
        volts=[s*r*rt/(pull*pt+r*rt) for s,pt,rt in itertools.product([3.3*.985,3.3*1.015],[.99,1.01],[.99,1.01])]
        adc[name].append({'R':r,'min_V_including_1pct_R_1p5pct_rail':min(volts),'max_V':max(volts),'nominal_V':3.3*r/(pull+r)})
results={
 'review_date':'2026-09-17','block_count':len(blocks),'reference_count':len(rows),'blocks':blocks,
 'source_hashes_unchanged':True,'pad_center_distances_mm':distances,'net_metrics':net_metrics,'routes':routes,
 'opposite_ground_projection':ground_projection,'button_corners':adc,
 'button_corner_limits':'Resistors +/-1%, assumed regulated rail +/-1.5%; excludes ADC error, contact resistance and leakage.',
 'battery_reversed_with_Q8_on':{'assumptions':'Q8 is enhanced by positive P+ relative to GND. Q3 body diode forward from common drains to B+. Reversed cell: B-=B+ +Vcell. Approximate Q8 drop neglected; no current/damage prediction.','U5_VCC_minus_GND_formula':'Vdiode - Vcell','example_at_Vdiode_0p7V_Vcell_4p2V':.7-4.2},
 'button_pullup_current_when_low_uA':3.3/10000*1e6,
 'power_button_pressed_nominal_V':3.3*100000/110000,
 'i2c_max_C_400kHz_300ns_rise_pF':300e-9/(.8473*2200)*1e12,
 'adim_40us_enable_min_duty_examples':{'10kHz':.4,'20kHz':.8,'25kHz':1.0},
 'usb_direct_input_C_nominal_uF':11,
 'source_note':'C2=10uF plus C25=1uF directly on VBUS after fuse; switched downstream capacitance needs inrush measurement.',
 'limitations':'No board powered; no thermal/EMC/ESD certification or exact MLCC-bias characterization. Graph lengths approximate pad traversal; zone projection is a geometric screen only.'
}
(out/'complete-block-review.json').write_text(json.dumps(results,indent=2),encoding='utf-8')

# Schematic crops from the current supplied PDF, not historical docs/images.
pdf=pymupdf.open(root/'docs/silkscreen_pcb_schematic.pdf');page=pdf[0];w,h=page.rect.width,page.rect.height
for name,rect in {'battery-schematic':(.028,.31,.219,.523),'sd-schematic':(.388,.064,.611,.303),'led-schematic':(.328,.519,.674,.778),'processor-schematic':(.674,.351,.944,.690)}.items():
    clip=pymupdf.Rect(rect[0]*w,rect[1]*h,rect[2]*w,rect[3]*h)
    page.get_pixmap(matrix=pymupdf.Matrix(1300/clip.width,1300/clip.width),clip=clip).save(out/(name+'.png'))
print('Coverage:',len(blocks),'blocks,',len(rows),'references. Source hashes unchanged.')
print('Pad distances:',json.dumps(distances))
print('Routes:',json.dumps({k:{a:b for a,b in v.items() if a!='path'} for k,v in routes.items()}))
print('Opposite ground screening:',json.dumps({k:v['opposite_GND_zone_percent'] for k,v in ground_projection.items()}))

# Show actual filled ground polygons on each layer, with selected signal paths.
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
def ground_plot(filename,limits,nets,refs):
    fig,axs=plt.subplots(1,2,figsize=(15,9),sharex=True,sharey=True)
    colors=dict(zip(nets,['#d82762','#1069c4','#df8500','#8428a8','#009968']))
    for ax,layer in zip(axs,['F.Cu','B.Cu']):
        for z in d['zones']:
            if z['net']!='GND' or z['keepout']:continue
            for p in z['filled'].get(layer,[]):
                ax.add_patch(Polygon(p['outer'],color='#d6dedb',linewidth=0))
                for hole in p['holes']:ax.add_patch(Polygon(hole,color='white',linewidth=0))
        for t in d['tracks']:
            if t['net'] not in nets:continue
            color=colors[t['net']]
            if t['kind']=='PCB_VIA':ax.add_patch(Circle(t['start'],.25,fill=False,edgecolor=color,lw=1.2,zorder=4))
            else:ax.plot([t['start'][0],t['end'][0]],[t['start'][1],t['end'][1]],color=color,lw=1.5,linestyle='-' if t['layer']==layer else ':',alpha=1 if t['layer']==layer else .6,zorder=3)
        for ref in refs:
            f=fs[ref]
            if limits[0]<=f['pos'][0]<=limits[1] and limits[2]<=f['pos'][1]<=limits[3]:
                ax.text(*f['pos'],ref,fontsize=8,bbox=dict(fc='white',ec='none',alpha=.8),zorder=6,clip_on=True)
        for net in nets:ax.plot([],[],color=colors[net],label=net)
        ax.set(title=f'{layer}: grey = filled GND; solid = this layer; dotted = other',xlim=limits[:2],ylim=(limits[3],limits[2]),xlabel='PCB X / mm',ylabel='PCB Y / mm')
        ax.set_aspect('equal');ax.legend(fontsize=8,loc='lower left');ax.grid(alpha=.15)
    fig.suptitle('Coordinate inspection — pad copper omitted; not a field-solver result',fontsize=10)
    fig.tight_layout();fig.savefig(out/filename,dpi=140);plt.close(fig)
ground_plot('usb-ground-paths.png',(65,100,88,109),['DP','DN'],['J1','U6','U4'])
ground_plot('eink-control-ground.png',(65,96,108,139),['/GDR','/RESE','EINK_SW'],['J2','Q4','L1','R14','R15'])
ground_plot('sd-ground-paths.png',(52,84,68,94),['SD_CLK','SD_CMD','SD_DAT0','SD_DAT1'],['J7','U4','U1','U9','Q7'])
