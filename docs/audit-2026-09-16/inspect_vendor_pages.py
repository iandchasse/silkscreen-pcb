"""Retrieve public primary-vendor document links, outside the repository."""
import requests,re,pathlib,html
dest=pathlib.Path.home()/'AppData/Local/Temp/silkscreen-audit-2026-09-16'
for tag,url in [('panel-ft','https://www.good-display.com/companyfile/2001.html'),('panel-fl','https://www.good-display.com/companyfile/1946.html'),('mdd-inverter','https://www.lcsc.com/datasheet/C53185133.pdf')]:
 try:
  r=requests.get(url,timeout=25); t=html.unescape(r.text);(dest/(tag+'.html')).write_text(t,encoding='utf-8')
  links=sorted(set(re.findall(r'(?:https?:)?//[^\s<>"\x27]+?\.pdf[^\s<>"\x27]*',t)))
  print(tag,r.status_code,'links',links)
  if not links:
   for s in t.splitlines():
    if any(k in s for k in ['fileUrl','filePath','fileurl','downloadUrl','fileId','pdfUrl','pdfURL']):print(s[:600])
 except Exception as e:print(tag,str(e))
