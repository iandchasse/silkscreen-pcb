"""Read-only KiCad 9 board geometry extraction for the independent PCBA audit."""
import pcbnew as p
import json, pathlib, sys
root = pathlib.Path(__file__).resolve().parents[2]
b = p.LoadBoard(str(root / 'silkscreen_pcb.kicad_pcb'))
def xy(v): return [p.ToMM(v.x),p.ToMM(v.y)]
def box(v): return [p.ToMM(v.GetX()),p.ToMM(v.GetY()),p.ToMM(v.GetWidth()),p.ToMM(v.GetHeight())]
data={'file':'silkscreen_pcb.kicad_pcb','bbox':box(b.GetBoardEdgesBoundingBox()),'copper_layers':b.GetCopperLayerCount(),'footprints':[],'tracks':[],'zones':[],'edges':[]}
for f in b.GetFootprints():
 d={'ref':f.GetReference(),'value':f.GetValue(),'lib':str(f.GetFPID().GetLibItemName()),'pos':xy(f.GetPosition()),'rotation':f.GetOrientationDegrees(),'layer':f.GetLayerName(),'dnp':f.IsDNP(),'exclude_bom':f.IsExcludedFromBOM(),'exclude_pos':f.IsExcludedFromPosFiles(),'pads':[],'models':[]}
 for a in f.Pads():
  d['pads'].append({'number':a.GetNumber(),'net':a.GetNetname(),'pos':xy(a.GetPosition()),'size':xy(a.GetSize()),'drill':xy(a.GetDrillSize()),'rotation':a.GetOrientationDegrees(),'shape':int(a.GetShape()),'attribute':int(a.GetAttribute()),'layers':a.GetLayerSet().FmtBin()})
 for m in f.Models(): d['models'].append({'path':m.m_Filename,'scale':[m.m_Scale.x,m.m_Scale.y,m.m_Scale.z],'offset':[m.m_Offset.x,m.m_Offset.y,m.m_Offset.z],'rotation':[m.m_Rotation.x,m.m_Rotation.y,m.m_Rotation.z]})
 data['footprints'].append(d)
for t in b.GetTracks():
 d={'kind':t.GetClass(),'net':t.GetNetname(),'layer':t.GetLayerName(),'width':p.ToMM(t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth()),'start':xy(t.GetStart()),'end':xy(t.GetEnd())}
 if isinstance(t,p.PCB_VIA): d['drill']=p.ToMM(t.GetDrillValue())
 data['tracks'].append(d)
for z in b.Zones():
 zd={'net':z.GetNetname(),'layer':z.GetLayerName(),'keepout':z.GetIsRuleArea(),'bbox':box(z.GetBoundingBox()),'clearance':p.ToMM(z.GetLocalClearance()),'thermal_gap':p.ToMM(z.GetThermalReliefGap()),'thermal_spoke':p.ToMM(z.GetThermalReliefSpokeWidth()),'filled':{}}
 for layer in [p.F_Cu,p.B_Cu]:
  if z.GetIsRuleArea() or not z.IsOnLayer(layer):continue
  a=z.GetFilledPolysList(layer);polys=[]
  for j in range(a.OutlineCount()):
   c=a.COutline(j);poly={'outer':[xy(c.CPoint(i)) for i in range(c.PointCount())],'holes':[]}
   for k in range(a.HoleCount(j)):
    c=a.CHole(j,k);poly['holes'].append([xy(c.CPoint(i)) for i in range(c.PointCount())])
   polys.append(poly)
  zd['filled'][b.GetLayerName(layer)]=polys
 data['zones'].append(zd)
for g in b.GetDrawings():
 if g.GetLayer()==p.Edge_Cuts:
  d={'shape':int(g.GetShape()),'start':xy(g.GetStart()),'end':xy(g.GetEnd()),'width':p.ToMM(g.GetWidth())}
  if g.GetShape()==p.SHAPE_T_ARC: d['mid']=xy(g.GetArcMid())
  data['edges'].append(d)
(pathlib.Path(__file__).parent/'board.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print('Extracted',len(data['footprints']),'footprints,',len(data['tracks']),'tracks/vias;',data['copper_layers'],'copper layers;',data['bbox'])
