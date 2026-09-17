"""Independent source inventory; does not read historical Markdown reviews."""
import pathlib,json,xml.etree.ElementTree as E,hashlib,collections,zipfile,csv,io
import pymupdf as fitz
root=pathlib.Path(__file__).resolve().parents[2]; out=pathlib.Path(__file__).parent
tree=E.parse(out/'netlist.xml'); comps={x.attrib['ref']:x for x in tree.findall('./components/comp')}
nets={x.attrib['name']:[dict(n.attrib) for n in x.findall('node')] for x in tree.findall('./nets/net')}
pinmap=collections.defaultdict(list)
for name,nodes in nets.items():
 for n in nodes: pinmap[n['ref']].append((n['pin'],n.get('pinfunction',''),name))
lines=[]
for ref,c in comps.items():
 lines.append(f"{ref} | {c.findtext('value')} | {c.findtext('footprint')} | {c.findtext('datasheet')}")
 for p in pinmap[ref]: lines.append('  '+str(p))
(out/'component-connectivity.txt').write_text('\n'.join(lines),encoding='utf-8')
(out/'nets.json').write_text(json.dumps(nets,indent=2),encoding='utf-8')
for filename in ['silkscreen_pcb_schematic.pdf','silkscreen_pcb_layout.pdf']:
 d=fitz.open(root/'docs'/filename)
 print(filename,'pages',len(d),'page0',d[0].rect)
 (out/(filename+'.txt')).write_text('\n'.join(p.get_text() for p in d),encoding='utf-8')
 for i,page in enumerate(d):
  page.get_pixmap(matrix=fitz.Matrix(min(2200/page.rect.width,2200/page.rect.height),min(2200/page.rect.width,2200/page.rect.height)) ).save(out/f'{filename}-{i+1}.png')
manifest=[]
for rel in ['silkscreen_pcb.kicad_sch','silkscreen_pcb.kicad_pcb','silkscreen_pcb.kicad_pro','_autosave-silkscreen_pcb.kicad_pcb','production/bom_JLC_upload.csv','production/positions.csv','production/Silkscreen_Reader_PCB_1.0.zip']:
 f=root/rel; manifest.append({'path':rel,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
(out/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(root/'production/Silkscreen_Reader_PCB_1.0.zip') as z:
 print('FAB ZIP:',z.namelist())
 (out/'fabrication-archive.json').write_text(json.dumps([{'name':x.filename,'bytes':x.file_size,'time':x.date_time} for x in z.infolist()],indent=2),encoding='utf-8')
for fn in ['erc.json','drc.json']:
 if not (out/fn).exists(): continue
 d=json.loads((out/fn).read_text()); violations=d.get('violations',[])+[v for s in d.get('sheets',[]) for v in s.get('violations',[])]
 print(fn,collections.Counter((v['severity'],v['type']) for v in violations))
 if fn=='drc.json': print('unconnected',len(d.get('unconnected_items',[])),'parity',len(d.get('schematic_parity',[])))
 (out/(fn+'.txt')).write_text('\n'.join(f"{v['severity']} {v['type']}: {v['description']} | "+' | '.join(i['description'] for i in v.get('items',[])) for v in violations),encoding='utf-8')
print('Components',len(comps),'nets',len(nets))
# The supplied .xls is actually an OOXML ZIP, so use a binary stream to avoid
# openpyxl's filename-extension rejection.
import openpyxl
order=root/'production/bom_JLC_upload-JLCPCB Assembly Order.xls'
workbook=openpyxl.load_workbook(io.BytesIO(order.read_bytes()),data_only=True)
(out/'order-bom.json').write_text(json.dumps(list(workbook.active.values),indent=2,ensure_ascii=False),encoding='utf-8')
