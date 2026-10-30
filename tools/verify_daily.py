from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from pypdf import PdfReader
import json,hashlib,re,zipfile
root=Path(__file__).resolve().parents[1];docs=root/'docs'
data=json.loads((docs/'assets/data.js').read_text(encoding='utf-8').removeprefix('window.NOTE_DATA=').removesuffix(';'))
daily=json.loads((root/'data/daily.json').read_text(encoding='utf-8'))
checks={'days':{},'sources':0,'links':0,'back_to_top_pages':0,'global_chapters_unchanged':0}
baseline=json.loads((root/'qa/before-daily-hashes.json').read_text(encoding='utf-8'))
for name,digest in baseline.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
with zipfile.ZipFile(root/'qa/before-daily.zip') as old:
    for file in ['neural-reset.html','women-neuroscience.html']:
        before=old.read('docs/'+file).decode('utf-8').replace('\r\n','\n');after=(docs/file).read_text(encoding='utf-8')
        previous=re.findall(r'<section class="chapter".*?</section>',before,re.S)
        assert previous==re.findall(r'<section class="chapter".*?</section>',after,re.S),file
        checks['global_chapters_unchanged']+=len(previous)
    before=old.read('docs/index.html').decode('utf-8').replace('\r\n','\n');after=(docs/'index.html').read_text(encoding='utf-8')
    assert re.search(r'<section class="hero">.*?</section>',before,re.S)[0]==re.search(r'<section class="hero">.*?</section>',after,re.S)[0]
checks['original_three_pdfs_and_content_unchanged']=True

class Scan(HTMLParser):
    def __init__(self):super().__init__();self.urls=[];self.ids=set();self.notes=set();self.top=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:assert d['id'] not in self.ids,d['id'];self.ids.add(d['id'])
        if 'data-note-id' in d:self.notes.add(d['data-note-id'])
        if tag=='button' and 'back-top' in d.get('class','').split():self.top+=1
        for key in ['href','src']:
            if key in d:self.urls.append(d[key])
htmls={p:Scan() for p in docs.glob('*.html')}
for p,scan in htmls.items():
    scan.feed(p.read_text(encoding='utf-8'));assert scan.top==1,p
    checks['back_to_top_pages']+=1
for p,scan in htmls.items():
    for url in scan.urls:
        u=urlsplit(url)
        if u.scheme or u.netloc:continue
        target=(p.parent/unquote(u.path)).resolve() if u.path else p
        assert target.exists(),(p.name,url)
        if u.fragment and target in htmls:assert unquote(u.fragment) in htmls[target].ids,(p.name,url)
        checks['links']+=1
assert len(data['sources'])==118
assert len(data['search'])==136
for day in daily:
    ds=day['date'];ss=[s for s in data['sources'] if s['date']==ds];reader=PdfReader(docs/ss[0]['daily_pdf'])
    assert len(reader.pages)==len(ss)==len(day['notes'])
    assert not list(reader.attachments)
    for s in ss:
        u=urlsplit(s['detail_url']);target=docs/u.path
        assert u.fragment in htmls[target].ids
        assert s['id'] in htmls[target].notes
        page=reader.pages[s['daily_page']-1];text=''.join(page.extract_text().split())
        original=Path(r'D:\gwl')/ds/'output/pdf'/s['pdf']
        assert hashlib.sha256(original.read_bytes()).hexdigest()==s['pdf_sha256']
        oldtext=''.join(PdfReader(original).pages[0].extract_text().split())
        assert oldtext in text,(s['id'],'原笔记正文不完整')
        assert s['title'] in text and s['note_pdf']==s['daily_pdf']+'#page='+str(s['daily_page'])
        assert len(page.extract_text())<3000,(s['id'],'意外包含原文')
        for key in s['chapters']:assert key in htmls[docs/(s['course']+'.html')].ids
        checks['sources']+=1
    checks['days'][ds]={'notes':len(ss),'pdf_pages':len(reader.pages),'attachments':0,'all_note_content_preserved':True}
(root/'qa/daily-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False))
