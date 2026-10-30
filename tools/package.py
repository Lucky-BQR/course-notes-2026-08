from pathlib import Path
import zipfile,html,shutil,re,json
from urllib.parse import urlsplit,unquote
import posixpath
root=Path(__file__).resolve().parents[1]
out=root/'output';download=root/'docs/downloads'

def site_bytes(p):
    if p.name=='index.html':
        text=p.read_text(encoding='utf-8')
        text=re.sub(r'<a href="downloads/(?:course-notes-complete|site-source)\.zip" download>.*?</a>','',text,flags=re.S)
        return text.encode('utf-8')
    return p.read_bytes()

def code_files():
    for folder in ['tools','data','.github']:
        for p in (root/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in str(p) and p.name!='read_notes.py':yield p,p.relative_to(root).as_posix()
    for name in ['README.md','.gitignore','.gitattributes']:yield root/name,name

sourcezip=download/'site-source.zip'
with zipfile.ZipFile(sourcezip,'w',zipfile.ZIP_DEFLATED) as z:
    for p,name in code_files():z.write(p,name)
    for p in (root/'docs').rglob('*'):
        if p.is_file() and p.suffix!='.zip':z.writestr(p.relative_to(root).as_posix(),site_bytes(p))

package=out/'课程全局笔记_完整交付包.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for p in (out/'pdf').glob('*.pdf'):z.write(p,'PDF/'+p.name)
    for p in (out/'notes').glob('*.md'):z.write(p,'可编辑笔记/'+p.name)
    z.write(download/'source-index.csv','出处索引.csv')
    z.write(root/'README.md','阅读与部署说明.md')
    for p in (root/'docs').rglob('*'):
        if p.is_file() and p.suffix!='.zip':z.writestr('离线网站/'+p.relative_to(root/'docs').as_posix(),site_bytes(p))
    for p,name in code_files():z.write(p,'编辑源码/'+name)
    for name in ['verification.json','browser-verification.json','daily-verification.json','daily-browser-verification.json']:
        p=root/'qa'/name
        if p.exists():z.write(p,'验证记录/'+name)
shutil.copy2(package,download/'course-notes-complete.zip')
checks=[]
for zip_path,prefix in [(package,'离线网站/'),(sourcezip,'docs/')]:
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None
        names=set(z.namelist())
        assert not any(n.lower().endswith(('.doc','.docx','.zip')) for n in names)
        checked=0
        for name in names:
            if name.startswith(prefix) and name.endswith('.html'):
                for url in re.findall(r'(?:href|src)="([^"]+)"',z.read(name).decode('utf-8')):
                    u=urlsplit(html.unescape(url))
                    if u.scheme or u.netloc or not u.path:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(u.path)))
                    assert target in names,(zip_path.name,name,url,'包内路径缺失')
                    checked+=1
        checks.append(dict(file=zip_path.name,entries=len(names),html_file_links=checked,crc_valid=True,raw_documents_included=False))
(root/'qa/archive-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'complete_zip_bytes':package.stat().st_size,'source_zip_bytes':sourcezip.stat().st_size},ensure_ascii=False))
