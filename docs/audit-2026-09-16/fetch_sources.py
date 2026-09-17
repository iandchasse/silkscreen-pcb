import pathlib,requests,concurrent.futures,json,tempfile
import pymupdf as fitz
cache=pathlib.Path(tempfile.gettempdir())/'silkscreen-audit-2026-09-16';cache.mkdir(exist_ok=True)
urls={'tps923610':'https://www.ti.com/lit/ds/symlink/tps923610.pdf','tps2116':'https://www.ti.com/lit/ds/symlink/tps2116.pdf','tlv755p':'https://www.ti.com/lit/ds/symlink/tlv755p.pdf','esp32s3':'https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf','tpd4e1u06':'https://www.ti.com/lit/ds/symlink/tpd4e1u06.pdf','dw01a':'https://hmsemi.com/downfile/DW01A.PDF','ds3231m':'https://www.analog.com/media/en/technical-documentation/data-sheets/DS3231M.pdf','tp4056':'https://www.lcsc.com/datasheet/lcsc_datasheet_2410121619_TOPPOWER-Nanjing-Extension-Microelectronics-TP4056-42-ESOP8_C16581.pdf'}
def get(kv):
 k,u=kv; f=cache/(k+'.pdf')
 try:
  if not f.exists():
   r=requests.get(u,timeout=35);r.raise_for_status()
   if not r.content.startswith(b'%PDF'):return {'name':k,'url':u,'error':'not PDF'}
   f.write_bytes(r.content)
  d=fitz.open(f);(cache/(k+'.txt')).write_text('\n'.join(f'\nPAGE {i+1}\n'+p.get_text() for i,p in enumerate(d)),encoding='utf-8')
  return {'name':k,'url':u,'pages':len(d),'cache':str(f)}
 except Exception as e:return {'name':k,'url':u,'error':str(e)}
urls.update({'fs8205-ordered':'https://datasheet.lcsc.com/datasheet/pdf/c060cb7baa8cc2b2d2a0ed3afa443ef8.pdf','dw01-ordered':'https://datasheet.lcsc.com/datasheet/pdf/0d2b2b5e8d1207bf276387cb4ff3a495.pdf','tp4056-ordered':'https://datasheet.lcsc.com/datasheet/pdf/d328ee101cbb1f3719611cd61db479c2.pdf','sd05c-ordered':'https://datasheet.lcsc.com/datasheet/pdf/f9b7b3e2c9eb25bcff59f2b72aceabee.pdf','bss138-ordered':'https://datasheet.lcsc.com/datasheet/pdf/e82111e7bf6514856f73f1b91d3645f8.pdf','led-substitute':'https://datasheet.lcsc.com/datasheet/pdf/8e04df73a20896aea76d4672dc480ed1.pdf','sd-shouhan':'https://datasheet.lcsc.com/datasheet/pdf/dc83ceb7bc09989eab2815b685da60e4.pdf'})
urls.pop('tp4056');urls.pop('ds3231m')
results=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(get,urls.items()))
for name in ['fs8205-ordered','sd-shouhan','led-substitute','sd05c-ordered']:
 f=cache/(name+'.pdf')
 if f.exists():
  d=fitz.open(f);d[0].get_pixmap(matrix=fitz.Matrix(2,2)).save(cache/(name+'-p1.png'))
print(json.dumps(results,indent=2));(pathlib.Path(__file__).parent/'datasheet-sources.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
