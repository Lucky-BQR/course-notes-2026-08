from pathlib import Path
import json,re,hashlib
from pypdf import PdfReader
import pdfplumber
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from content import COURSES

root=Path(__file__).resolve().parents[1];src=Path(r'D:\gwl');results={}
sources=json.loads((root/'data/sources.json').read_text(encoding='utf-8'))
assert len(sources)==118
errors=[];combined_cache={}
for s in sources:
    pdf=src/s['date']/'output/pdf'/s['pdf'];original=src/s['date']/s['original']
    assert hashlib.sha256(pdf.read_bytes()).hexdigest()==s['pdf_sha256']
    assert hashlib.sha256(original.read_bytes()).hexdigest()==s['original_sha256']
    text=PdfReader(pdf).pages[0].extract_text().replace(' ','')
    assert s['title'] in text,(s['id'],'笔记标题不匹配')
    if s['date'] not in combined_cache:combined_cache[s['date']]=PdfReader(src/s['date']/'output/pdf'/s['combined'])
    combined=combined_cache[s['date']]
    assert s['title'] in combined.pages[s['combined_page']-1].extract_text().replace(' ',''),(s['id'],'合订本页码不匹配')
    assert s['chapters']
results['source_audit']={'count':118,'all_original_hashes_unchanged':True,'all_pdf_pages_verified':True,'mapped_to_chapters':118}
pdf_stats=[]
for path in sorted((root/'output/pdf').glob('*.pdf')):
    reader=PdfReader(path);pagemap={p.indirect_reference.idnum:i for i,p in enumerate(reader.pages)}
    internal=external=0
    for i,pg in enumerate(reader.pages):
        assert pg.extract_text().strip(),(path.name,i,'空页')
        for obj in pg.get('/Annots',[]):
            a=obj.get_object()
            if '/Dest' in a:
                assert a['/Dest'][0].idnum in pagemap,(path.name,i,'无效链接')
                internal+=1
            if a.get('/A',{}).get('/S')=='/URI':external+=1
    with pdfplumber.open(path) as doc:
        for i,pg in enumerate(doc.pages):
            for char in pg.chars:
                if char['text'].strip() and (char['x0']<0 or char['x1']>pg.width+1 or char['top']<0 or char['bottom']>pg.height):
                    errors.append([path.name,i+1,'文字超出页面',char['text']])
    pdf_stats.append(dict(file=path.name,pages=len(reader.pages),internal_links=internal,external_links=external))
results['pdf']=pdf_stats

class Scan(HTMLParser):
    def __init__(self):super().__init__();self.urls=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.add(d['id'])
        for key in ['href','src']:
            if key in d:self.urls.append(d[key])
htmls={p:Scan() for p in (root/'docs').glob('*.html')}
for p,scan in htmls.items():scan.feed(p.read_text(encoding='utf-8'))
links=0
for p,scan in htmls.items():
    for url in scan.urls:
        u=urlsplit(url)
        if u.scheme or u.netloc:continue
        target=(p.parent/unquote(u.path)).resolve() if u.path else p
        if not target.exists():errors.append([p.name,url,'目标不存在']);continue
        if u.fragment and target in htmls and unquote(u.fragment) not in htmls[target].ids:errors.append([p.name,url,'锚点不存在'])
        links+=1
results['website_local_links']=links
results['errors']=errors
(root/'qa/verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False))
if errors:raise SystemExit(1)
