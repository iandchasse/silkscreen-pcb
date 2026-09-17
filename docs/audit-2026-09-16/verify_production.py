"""Recreate toolkit output in TEMP; never save or modify the source PCB."""
import sys, types, pathlib, tempfile, importlib, csv, json, zipfile, difflib, re, hashlib
import pcbnew
root=pathlib.Path(__file__).resolve().parents[2]
out=pathlib.Path(__file__).parent
plugin=pathlib.Path(r'C:\Users\iandc\OneDrive\Documents\KiCad\9.0\3rdparty\plugins\com_github_bennymeg_JLC-Plugin-for-KiCad')
pkg=types.ModuleType('audit_toolkit');pkg.__path__=[str(plugin)];sys.modules[pkg.__name__]=pkg
ProcessManager=importlib.import_module('audit_toolkit.process').ProcessManager
dest=pathlib.Path(tempfile.mkdtemp(prefix='silkscreen-production-audit-'))
b=pcbnew.LoadBoard(str(root/'silkscreen_pcb.kicad_pcb'))
p=ProcessManager(b)
p.generate_tables(str(dest),True,True)
p.generate_positions(str(dest))
p.generate_gerber(str(dest),None,False,False,False)
p.generate_drills(str(dest))
def rows(path):return {r['Designator']:r for r in csv.DictReader(path.open(encoding='utf-8-sig'))}
original=rows(root/'production/positions.csv');fresh=rows(dest/'positions.csv')
diffs=[]
for ref in sorted(original.keys()|fresh.keys()):
 if ref not in original or ref not in fresh:diffs.append({'ref':ref,'missing_from':'original' if ref not in original else 'regenerated'});continue
 for key in original[ref]:
  a=original[ref][key];c=fresh[ref][key]
  equal=abs(float(a)-float(c))<1e-5 if key in ['Mid X','Mid Y','Rotation'] else a==c
  if not equal:diffs.append({'ref':ref,'field':key,'saved':a,'regenerated':c})
def normalize(text):
 # Omit creation timestamps only. Keep geometry, units, net attributes and tool selections.
 return '\n'.join(s for s in text.splitlines() if not any(k in s for k in ['CreationDate,','Created by','CreationDate=','; DRILL file']))
gerbers=[]
with zipfile.ZipFile(root/'production/Silkscreen_Reader_PCB_1.0.zip') as z:
 for name in z.namelist():
  ext=pathlib.Path(name).suffix.lower();base=pathlib.Path(name).name
  candidates=list(dest.glob('*'+ext))
  if 'NPTH' in base:candidates=[x for x in candidates if 'NPTH' in x.name]
  elif 'PTH' in base:candidates=[x for x in candidates if 'PTH' in x.name and 'NPTH' not in x.name]
  if '-drl_map' in base:candidates=[x for x in candidates if '-drl_map' in x.name]
  if len(candidates)!=1:gerbers.append({'file':name,'candidates':[x.name for x in candidates]});continue
  a=normalize(z.read(name).decode('utf-8-sig'));c=normalize(candidates[0].read_text(encoding='utf-8-sig'))
  same=a==c
  record={'file':name,'regenerated':candidates[0].name,'equal_ignoring_creation_time':same}
  if not same:
   delta=list(difflib.unified_diff(a.splitlines(),c.splitlines(),n=2))
   record['diff_lines']=len(delta);record['diff_preview']=delta[:60]
  gerbers.append(record)
report={'regenerated_directory':str(dest),'method':'installed Fabrication Toolkit, auto-translation on, DNP excluded; no zone refill; no source save','original_cpl_rows':len(original),'regenerated_cpl_rows':len(fresh),'cpl_differences':diffs,'fabrication_comparison':gerbers}
(out/'production-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
