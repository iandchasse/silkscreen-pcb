"""Check source preservation and audit consistency; no design writes."""
import pathlib,hashlib,json,csv,datetime,io,re
import openpyxl
out=pathlib.Path(__file__).parent;root=out.parents[1]
initial=json.loads((out/'source-manifest.json').read_text());result=[]
for item in initial:
 path=root/item['path']
 if not path.exists() and path.name.startswith('_autosave-'):
  result.append({'path':item['path'],'initial_sha256':item['sha256'],'final_sha256':None,'unchanged':None,'status':'absent_ephemeral_autosave'})
  continue
 current=hashlib.sha256(path.read_bytes()).hexdigest()
 result.append({'path':item['path'],'initial_sha256':item['sha256'],'final_sha256':current,'unchanged':current==item['sha256'],'status':'present'})
(out/'source-preservation.json').write_text(json.dumps({'checked_local':datetime.datetime.now().astimezone().isoformat(),'files':result},indent=2),encoding='utf-8')
assert all(r['unchanged'] or r['status']=='absent_ephemeral_autosave' for r in result),'Source changed: report must be reassessed'
components=list(csv.DictReader((out/'component-review.csv').open(encoding='utf-8-sig')))
assert len(components)==173 and len({r['Ref'] for r in components})==173
bom=json.loads((out/'bom-verification.json').read_text())
assert not bom['passive_value_errors'] and not bom['unexplained_exclusions']
gerbers=json.loads((out/'gerber-geometry-comparison.json').read_text())
assert len(gerbers)==13
assert all(r.get('geometry_equal',r.get('exact_except_timestamp',False)) for r in gerbers)
assert not json.loads((out/'production-verification.json').read_text())['cpl_differences']
orderfile=root/'production/bom_JLC_upload-JLCPCB Assembly Order.xls'
current_order=[list(r) for r in openpyxl.load_workbook(io.BytesIO(orderfile.read_bytes()),data_only=True).active.values]
assert current_order==json.loads((out/'order-bom.json').read_text()),'Saved order has changed since extraction'
print('PASS:',sum(r['unchanged'] is True for r in result),'original hashed inputs unchanged;',sum(r['status']=='absent_ephemeral_autosave' for r in result),'ephemeral autosave absent; all 173 refs covered; 157 CPL entries match; 13 fabrication files match geometrically or except timestamps.')
coverage=list(csv.DictReader((out/'block-coverage.csv').open(encoding='utf-8-sig')))
assert len(coverage)==173 and len({r['Ref'] for r in coverage})==173
assert len({r['Block'] for r in coverage})==18
review=root/'DESIGN_REVIEW.md'
assert not (out/'REPORT.md').exists() and not (out/'Q4_AND_FRONTLIGHT_FOLLOWUP.md').exists()
checked_links=0
for doc in [review,root/'README.md',root/'docs/HARDWARE.md',root/'fabrication/README.md']:
 for link in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)',doc.read_text(encoding='utf-8')):
  if '://' in link or link.startswith('#'):continue
  target=(doc.parent/link.split('#')[0]).resolve()
  assert target.exists(),f'{doc}: missing {link}'
  checked_links+=1
print('PASS: 18 nonoverlapping blocks; one canonical review;',checked_links,'local documentation links resolve.')
print('Report words:',len(review.read_text(encoding='utf-8').split()))
