"""Retrieve exact ordered-device sheets for the September 17 block review.

Public supplier document links only. PDF cache stays outside the repository.
"""
import concurrent.futures, hashlib, json, os, pathlib, requests, bs4, pymupdf

out = pathlib.Path(__file__).parent
cache = pathlib.Path(os.environ['TEMP']) / 'silkscreen-audit-2026-09-16' / 'complete'
cache.mkdir(exist_ok=True)
sources = {
    'tpd4-tech': ('C19829453', 'https://jlcpcb.com/partdetail/TECHPUBLIC-TPD4E1U06DBVR/C19829453'),
    'inverter-mdd': ('C53185133', 'https://jlcpcb.com/partdetail/MDD_MicrodiodeSemiconductor-74LVC1G04GV/C53185133'),
    'pesd-tech': ('C42370512', 'https://jlcpcb.com/partdetail/TECHPUBLIC-PESD2IVNUX/C42370512'),
    'ao3419': ('', 'https://www.aosmd.com/res/data_sheets/AO3419.pdf'),
}

def fetch(item):
    name, (code, url) = item
    result = {'name': name, 'source': url, 'part_code': code}
    try:
        r = requests.get(url, timeout=25)
        r.raise_for_status()
        if code:
            soup = bs4.BeautifulSoup(r.text, 'html.parser')
            links = [a['href'] for a in soup.select('a[href]') if '.pdf' in a['href'] and code in a['href']]
            assert links, 'No exact-part PDF link in public product page'
            r = requests.get(links[0], timeout=25)
            r.raise_for_status()
        assert r.content.startswith(b'%PDF'), 'Response is not a PDF'
        f = cache / (name + '.pdf')
        f.write_bytes(r.content)
        doc = pymupdf.open(f)
        f.with_suffix('.txt').write_text('\n'.join(f'PAGE {i+1}\n'+p.get_text() for i,p in enumerate(doc)), encoding='utf-8')
        doc[0].get_pixmap(matrix=pymupdf.Matrix(1.8,1.8)).save(cache/(name+'-1.png'))
        result.update(cache=str(f), pages=len(doc), sha256=hashlib.sha256(r.content).hexdigest())
    except Exception as e:
        result['error'] = str(e)
    return result

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(fetch, sources.items()))
(out/'complete-review-sources.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
