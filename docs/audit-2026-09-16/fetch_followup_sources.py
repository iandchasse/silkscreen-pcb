"""Cache primary follow-up datasheets outside the repository for inspection."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests, pymupdf, hashlib, json, os, bs4

out = Path(__file__).parent
cache = Path(os.environ['TEMP']) / 'silkscreen-audit-2026-09-16' / 'followup'
cache.mkdir(parents=True, exist_ok=True)
sources = {
    'si1308edl': 'https://www.vishay.com/docs/63399/si1308edl.pdf',
    'irlml6346': 'https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlml6346-datasheet-en.pdf',
    'dmn3150l': 'https://www.diodes.com/datasheet/download/DMN3150L.pdf',
    'dmn3200u': 'https://www.diodes.com/datasheet/download/DMN3200U.pdf',
    'pmv40un2': 'https://assets.nexperia.com/documents/data-sheet/PMV40UN2.pdf',
    'ao3400a': 'https://www.aosmd.com/res/data_sheets/AO3400A.pdf',
}

def fetch(item):
    name, url = item
    result = {'name': name, 'url': url}
    try:
        r = requests.get(url, timeout=35)
        if name == 'irlml6346' and not r.content.startswith(b'%PDF'):
            landing = 'https://jlcpcb.com/partdetail/InfineonTechnologies-IRLML6346TRPBF/C67276'
            soup = bs4.BeautifulSoup(requests.get(landing, timeout=25).text, 'html.parser')
            link = next(a['href'] for a in soup.select('a[href]') if '-C67276.pdf' in a['href'])
            r = requests.get(link, timeout=35)
            result['mirror_landing'] = landing
        r.raise_for_status()
        assert r.content.startswith(b'%PDF'), 'Not PDF'
        path = cache / (name + '.pdf')
        path.write_bytes(r.content)
        d = pymupdf.open(path)
        path.with_suffix('.txt').write_text('\n'.join(f'PAGE {i+1}\n'+p.get_text() for i,p in enumerate(d)), encoding='utf-8')
        result.update(sha256=hashlib.sha256(r.content).hexdigest(), pages=len(d), cache=str(path))
        if name == 'irlml6346':
            for page in [0,1,2,7]:
                d[page].get_pixmap(matrix=pymupdf.Matrix(1.8,1.8)).save(cache/f'{name}-{page+1}.png')
    except Exception as e:
        result['error'] = str(e)
    return result

with ThreadPoolExecutor(max_workers=6) as pool:
    results = list(pool.map(fetch, sources.items()))
(out/'followup-sources.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
print(json.dumps(results, indent=2))
