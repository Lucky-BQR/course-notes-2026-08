"""Daily reading module; reuse curated notes, never the transcript appendices."""
from pathlib import Path
import ast,html,json,re,hashlib,io

DAY_INFO={
 '8.15':('感觉、疼痛与日常功能','从感觉与疼痛的概念，进入区域观察、现场问答和生活任务。'),
 '8.16':('身体感知与连续案例','接续前一天的反馈，阅读不同部位的案例与动作复测。'),
 '8.27':('女性身体感受与课程框架','建立身体知觉、压力、睡眠、运动和现场观察的整体框架。'),
 '8.28':('周期、感觉演示与消化','沿着周期与内分泌、身体体验、消化和排尿主题展开。'),
 '8.29':('盆底、排尿与功能复盘','区分尿意、控尿和排空，连接亲密体验、动作案例与课程复盘。'),
}
def day_slug(day):return day.replace('.','-')
def day_url(day):return f'daily-{day_slug(day)}.html'
def note_url(day,number):return f'{day_url(day)}#note-{number:02}'
def pdf_url(day):return f'downloads/daily/{day_slug(day)}.pdf'

def load_daily(root,src,sources,refresh=False):
    path=root/'data/daily.json'
    if refresh or not path.exists():
        result=[]
        for day in DAY_INFO:
            folder=src/day/'tmp/pdfs';notes=[]
            for p in sorted(folder.glob('notes*.json')):
                batch=json.loads(p.read_text(encoding='utf-8'))
                for n in batch:
                    n=dict(n,source_json=p.name,source_json_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                    notes.append(n)
            refs_path=folder/'references.json'
            if refs_path.exists():refs=json.loads(refs_path.read_text(encoding='utf-8'))
            else:
                tree=ast.parse((folder/'build.py').read_text(encoding='utf-8-sig'))
                node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REFS' for t in n.targets))
                refs=ast.literal_eval(node.value)
            notes.sort(key=lambda n:n['id'])
            expected={s['number']:s['title'] for s in sources if s['date']==day}
            assert {n['id']:n['title'] for n in notes}==expected
            assert len(notes)==len(expected)
            for n in notes:
                assert all(x in refs for x in n.get('refs',[])),(day,n['id'])
                assert all(x in refs for x in re.findall(r'\[(R\d+)\]',json.dumps(n,ensure_ascii=False)))
            result.append(dict(date=day,title=DAY_INFO[day][0],description=DAY_INFO[day][1],notes=notes,references=refs))
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    data=json.loads(path.read_text(encoding='utf-8'))
    assert sum(len(d['notes']) for d in data)==118
    return data

def enrich_sources(sources,data):
    for d in data:
        for page,n in enumerate(d['notes'],1):
            source=next(s for s in sources if s['date']==d['date'] and s['number']==n['id'])
            source.update(detail_url=note_url(d['date'],n['id']),daily_url=day_url(d['date']),
                          daily_pdf=pdf_url(d['date']),daily_page=page,note_pdf=f"{pdf_url(d['date'])}#page={page}")

def teaser(data):
    tiles=''.join(f'<a class="daily-tile" href="{day_url(d["date"])}"><strong>{d["date"]}</strong><span>{html.escape(d["title"])}</span><small>{len(d["notes"])} 篇详细笔记</small></a>' for d in data)
    return f'<section class="daily-entry" id="daily-notes"><div class="section-intro"><h2>每日详细笔记</h2><a href="daily.html">查看五天完整目录</a></div><p>沿日期进入具体篇目，也可以点击全局笔记中的出处编号，直接阅读对应详解。</p><div class="daily-grid">{tiles}</div></section>'

def build_daily_html(root,data,sources,courses,frame):
    site=root/'docs';search=[];byid={s['id']:s for s in sources};blocks=[]
    for d in data:
        day=d['date'];course=next(c for c in courses if day in c['days']);notes=d['notes'];refs=d['references']
        def rich(text):
            return re.sub(r'\[(R\d+)\]',lambda m:f'<a class="ref external" href="{html.escape(refs[m[1]][1],quote=True)}" target="_blank" rel="noopener" title="{html.escape(refs[m[1]][0],quote=True)}">{m[1]}</a>',html.escape(text))
        articles=[];md=[f'# {day} 每日详细笔记：{d["title"]}',course['title'],
            '沿用原有结构化笔记；文中的“原文附录”指原资料中的附录。此阅读版仅收录笔记。']
        for index,n in enumerate(notes,1):
            sid=f'{day}-{n["id"]:02}';s=byid[sid]
            related=''.join(f'<a class="chapter-tag" href="{course["slug"]}.html#{key}">{html.escape(next(t["title"] for t in course["sections"] if t["key"]==key))}</a>' for key in s['chapters'])
            cards=''.join('<div class="concept"><h3>'+rich(card[0])+'</h3><ul>'+''.join('<li>'+rich(line)+'</li>' for line in card[1:])+'</ul></div>' for card in n['cards'])
            table='<div class="table-scroll" role="region" tabindex="0" aria-label="'+html.escape(n['table_title'],quote=True)+'"><table><thead><tr>'+''.join('<th scope="col">'+rich(t)+'</th>' for t in n['cols'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+rich(v)+'</td>' for v in row)+'</tr>' for row in n['rows'])+'</tbody></table></div>'
            flow='<ol class="flow" aria-label="逻辑关系图">'+''.join('<li><strong>'+rich(a)+'</strong><span>'+rich(b)+'</span></li>' for a,b in n['flow'])+'</ol>'
            bottom='<div class="detail-bottom">'+''.join('<div class="review"><h3>'+rich(a)+'</h3><p>'+rich(b)+'</p></div>' for a,b in n['bottom'])+'</div>'
            references='<p class="note-references">原笔记核对来源：'+ '；'.join(f'<a href="{html.escape(refs[k][1],quote=True)}" target="_blank" rel="noopener">[{k}] {html.escape(refs[k][0])}</a>' for k in n.get('refs',[]))+'</p>' if n.get('refs') else ''
            prev=f'<a href="#note-{notes[index-2]["id"]:02}">上一篇</a>' if index>1 else '<a href="daily.html">五天目录</a>'
            following=f'<a href="#note-{notes[index]["id"]:02}">下一篇</a>' if index<len(notes) else '<a href="#main">当日目录</a>'
            articles.append(f'''<article class="chapter daily-note" id="note-{n['id']:02}" data-note-id="{sid}">
              <header class="chapter-heading"><span class="chapter-no">{n['id']:02}</span><h2>{html.escape(n['title'])}</h2><a class="anchor" href="#note-{n['id']:02}" aria-label="链接到本篇">#</a></header>
              <p class="note-subtitle">{rich(n['subtitle'])}</p><div class="note-actions"><button class="ref" data-source="{sid}" type="button">出处 {sid}</button><a href="{s['note_pdf']}" target="_blank" rel="noopener">打开本篇笔记 PDF</a></div><a class="return-context note-return" hidden></a>
              <div class="note-summary"><h3>核心提要</h3><ul>{''.join('<li>'+rich(t)+'</li>' for t in n['summary'])}</ul></div>
              <div class="concepts">{cards}</div><h3 class="note-table-title">{rich(n['table_title'])}</h3>{table}{flow}{bottom}{references}
              <div class="related-global"><h3>回到相关全局章节</h3><div>{related}</div></div><nav class="note-pagination" aria-label="{sid}篇目导航">{prev}<a href="#main">当日目录</a>{following}</nav></article>''')
            search.append(dict(title=f'{sid} {n["title"]}',course=f'{course["title"]} · 每日详解 {day}',kind='daily',url=s['detail_url'],text=' '.join([n['subtitle'],*n['summary'],*[' '.join(a) for a in n['cards']],*[' '.join(a) for a in n['rows']],*[' '.join(a) for a in n['bottom']]])))
            md += [f'\n## {n["id"]:02} {n["title"]}',n['subtitle'],'\n'.join('- '+t for t in n['summary'])]
            md += ['### '+card[0]+'\n\n'+'\n'.join('- '+t for t in card[1:]) for card in n['cards']]
            md += ['### '+n['table_title'],'| '+' | '.join(n['cols'])+' |','|---|---|---|']+['| '+' | '.join(row)+' |' for row in n['rows']]
            md += ['逻辑图：'+' → '.join(a+'（'+b+'）' for a,b in n['flow'])]+['### '+a+'\n\n'+b for a,b in n['bottom']]
            md += [f'出处：{sid}；{day}/{s["original"]}；原独立PDF《{s["pdf"]}》第1页；原当日合订本《{s["combined"]}》第{s["combined_page"]}页。']
        toc=''.join(f'<a href="#note-{n["id"]:02}"><span>{n["id"]:02}</span>{html.escape(n["title"])}</a>' for n in notes)
        adjacent=''.join(f'<a href="{day_url(other["date"])}"'+(' aria-current="page"' if other['date']==day else '')+f'>{other["date"]}</a>' for other in data)
        body=f'''<div class="reading-layout"><aside class="sidebar"><a class="back-home" href="daily.html">五天详细笔记目录</a><h2>{day} 每日详解</h2><p>{course['title']} · {len(notes)}篇</p><nav aria-label="当日篇目">{toc}</nav><a class="download-link" href="{pdf_url(day)}" download>下载当日笔记 PDF</a></aside><main id="main" class="reading"><header class="course-header"><p class="date">2026.{day} · {course['title']}</p><h1>{day} 每日详细笔记</h1><p class="subtitle">{d['title']}</p><p>{d['description']}</p><nav class="day-switch" aria-label="切换日期">{adjacent}</nav><div class="course-actions"><a class="button" href="{pdf_url(day)}" download>下载当日笔记 PDF</a><a class="button secondary" href="{course['slug']}.html">回到全局笔记</a></div><a class="return-context" hidden></a></header>
          <details class="reading-note"><summary>每日笔记与全局笔记怎样配合</summary><p>全局笔记帮助理解跨日期的知识联系；这里保留每份材料已整理的提要、概念卡、表格和逻辑图。点击篇末的相关全局章节可以返回整体脉络。</p><p>本页及当日PDF仅收录结构化笔记。笔记中提到的“原文附录”保留在客户原有资料中；原文件编号和页码仍可在出处中查阅。R编号沿用各日原笔记的核对来源，同一编号在不同日期可能指向不同资料。</p></details>
          <details class="daily-inline-toc"><summary>展开当日完整目录 · {len(notes)}篇</summary><nav aria-label="正文篇目目录">{toc}</nav></details>{''.join(articles)}<div class="end-nav"><a href="daily.html">返回五天目录</a><a href="{course['slug']}.html">回到{course['title']}全局笔记</a></div></main></div>'''
        body=body.replace('class="reading-layout"','class="reading-layout daily-reading"',1)
        (site/day_url(day)).write_text(frame(f'{day} 每日详细笔记',body,course),encoding='utf-8')
        md+=['\n## 原笔记核对来源']+[f'- [{k}] [{v[0]}]({v[1]})' for k,v in refs.items()]
        (site/'downloads/daily').mkdir(exist_ok=True)
        (site/'downloads/daily'/f'{day_slug(day)}.md').write_text('\n\n'.join(md),encoding='utf-8')
        blocks.append(f'<section class="daily-index-day" id="day-{day_slug(day)}"><div class="section-intro"><div><p class="date">{course["title"]} · {len(notes)}篇</p><h2><a href="{day_url(day)}">{day} · {d["title"]}</a></h2></div><a href="{pdf_url(day)}" download>下载当日笔记 PDF</a></div><p>{d["description"]}</p><ol class="daily-outline">'+''.join(f'<li><a href="{note_url(day,n["id"])}"><span>{n["id"]:02}</span>{html.escape(n["title"])}</a></li>' for n in notes)+'</ol></section>')
    body='<main id="main" class="home daily-index"><header class="course-header"><p class="date">两门课 · 五个日期 · 118篇笔记</p><h1>每日详细笔记</h1><p class="subtitle">从全局进入每一天，再读到每一篇。</p><p>选择日期或具体篇目，阅读全文、查看图表，并回到对应的全局章节。</p><nav class="day-switch" aria-label="跳到日期">'+''.join(f'<a href="#day-{day_slug(d["date"])}">{d["date"]} · {len(d["notes"])}篇</a>' for d in data)+'</nav></header>'+''.join(blocks)+'</main>'
    (site/'daily.html').write_text(frame('每日详细笔记',body),encoding='utf-8')
    return search

def create_daily_pdfs(root,src,data,sources):
    from pypdf import PdfReader,PdfWriter
    from pypdf.generic import NameObject,ArrayObject,DictionaryObject
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont('DailyFooter','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
    out=root/'output/pdf/daily';out.mkdir(parents=True,exist_ok=True)
    audit=[]
    for d in data:
        day=d['date'];items=[s for s in sources if s['date']==day];readers=[PdfReader(src/day/'output/pdf'/s['pdf']) for s in items]
        buf=io.BytesIO();overlay=canvas.Canvas(buf)
        for i,reader in enumerate(readers,1):
            page=reader.pages[0];w,h=float(page.mediabox.width),float(page.mediabox.height)
            overlay.setPageSize((w,h));overlay.setFillColorRGB(1,1,1);overlay.rect(0,0,w,30,fill=1,stroke=0)
            overlay.setFillColorRGB(.3,.37,.42);overlay.setFont('DailyFooter',8)
            overlay.drawString(30,17,f'{day} 每日详细笔记（笔记版） · 原文附录见原资料')
            overlay.drawRightString(w-30,17,f'{i} / {len(items)}');overlay.showPage()
        overlay.save();patch=PdfReader(buf);writer=PdfWriter()
        for i,(reader,s) in enumerate(zip(readers,items)):
            page=reader.pages[0]
            external=[]
            for ref in page.pop('/Annots',ArrayObject()):
                ann=ref.get_object();action=ann.get('/A',{})
                if action.get('/S')=='/URI':external.append(ann)
            page.merge_page(patch.pages[i]);new_page=writer.add_page(page)
            for ann in external:
                copied=DictionaryObject({NameObject(k):v.clone(writer) for k,v in ann.items() if k not in ('/P','/Dest')})
                writer.add_annotation(i,copied)
            writer.add_outline_item(f'{s["number"]:02} {s["title"]}',i)
        writer.add_metadata({'/Title':f'{day} 每日详细笔记（笔记版）','/Author':'课程资料整理','/Subject':'仅结构化笔记；不含原文附录和源文件附件'})
        writer.compress_identical_objects(remove_identicals=True,remove_orphans=True)
        path=out/f'{day}_每日详细笔记.pdf'
        with path.open('wb') as f:writer.write(f)
        target=root/'docs'/pdf_url(day);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        check=PdfReader(path);assert len(check.pages)==len(items);assert not list(check.attachments)
        for i,s in enumerate(items):
            assert s['title'] in check.pages[i].extract_text().replace(' ','')
            assert '原文附录' not in check.pages[i].extract_text().splitlines()[:3]
        audit.append(dict(date=day,pages=len(items),bytes=path.stat().st_size,attachments=0))
    (root/'qa/daily-pdf-build.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False))
