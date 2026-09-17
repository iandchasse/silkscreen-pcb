"""Compare the primitives in this KiCad RS274X export independent of drawing order.

This is a deliberately narrow parser for the actual KiCad-generated syntax. It
fails on unexpected syntax rather than claiming to be a general Gerber engine.
Attributes/comments are not physical geometry. Aperture definitions are resolved
before comparison; polarity and regions are preserved.
"""
import re,json,pathlib,zipfile,collections,hashlib
out=pathlib.Path(__file__).parent;root=out.parents[1]
report=json.loads((out/'production-verification.json').read_text())
dest=pathlib.Path(report['regenerated_directory'])
def parse(text):
 aps={};macros={};objects=[];unknown=[];settings=[]
 x=y=0;ap=None;mode='G01';polarity=('D',0);region=None;macro=None;macrotext=[]
 for line in text.splitlines():
  s=line.strip()
  if not s or s.startswith('G04'):continue
  if s.startswith('%AM'):
   macro=s[3:s.index('*')];macrotext=[s[s.index('*')+1:]];continue
  if macro is not None:
   macrotext.append(s)
   if s.endswith('%'):macros[macro]='\n'.join(macrotext);macro=None
   continue
  m=re.fullmatch(r'%ADD(\d+)(.+)\*%',s)
  if m:
   aps[int(m[1])]=m[2];continue
  if s.startswith(('%TF','%TA','%TO','%TD')):continue
  if s.startswith(('%FS','%MO','%IP','%LN')):settings.append(s);continue
  if s in ('%LPD*%','%LPC*%'):
   if s[3]!=polarity[0]:polarity=(s[3],polarity[1]+1)
   continue
  if s in ('G01*','G02*','G03*'):mode=s[:3];continue
  if s in ('G75*','G74*'):settings.append(s);continue
  if s=='G36*':region=[];continue
  if s=='G37*':objects.append(('REGION',polarity,tuple(region)));region=None;continue
  if s in ('M02*',):continue
  m=re.fullmatch(r'D(\d+)\*',s)
  if m and int(m[1])>=10:ap=aps[int(m[1])];continue
  m=re.fullmatch(r'(?:G0([123]))?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I(-?\d+))?(?:J(-?\d+))?D0([123])\*',s)
  if m:
   g,nx,ny,i,j,d=m.groups();nx=x if nx is None else int(nx);ny=y if ny is None else int(ny)
   if g:mode='G0'+g
   if d=='1':
    shape=(mode,(x,y),(nx,ny),int(i or 0),int(j or 0))
    if region is not None:region.append(shape)
    else:
     if mode=='G01':shape=(mode,*sorted([(x,y),(nx,ny)]),0,0)
     objects.append(('DRAW',polarity,ap,shape))
   elif d=='3':objects.append(('FLASH',polarity,ap,nx,ny))
   elif region is not None:region.append(('MOVE',nx,ny))
   x,y=nx,ny;continue
  unknown.append(s)
 return collections.Counter(objects),macros,sorted(set(settings)),unknown
results=[]
with zipfile.ZipFile(root/'production/Silkscreen_Reader_PCB_1.0.zip') as z:
 for n in z.namelist():
  p=dest/pathlib.Path(n).name
  if p.suffix=='.drl':
   norm=lambda t:'\n'.join(s for s in t.splitlines() if not s.startswith('; DRILL file') and 'TF.CreationDate,' not in s)
   results.append({'file':n,'exact_except_timestamp':norm(z.read(n).decode())==norm(p.read_text())});continue
  a,am,aset,au=parse(z.read(n).decode());b,bm,bset,bu=parse(p.read_text())
  old=a-b;new=b-a
  results.append({'file':n,'geometry_equal':a==b and am==bm and aset==bset and not au and not bu,'old_only_count':sum(old.values()),'new_only_count':sum(new.values()),'old_only':list(old.items())[:30],'new_only':list(new.items())[:30],'macro_equal':am==bm,'settings_equal':aset==bset,'unparsed_old':au[:10],'unparsed_new':bu[:10],'objects_old':sum(a.values()),'objects_new':sum(b.values())})
(out/'gerber-geometry-comparison.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
