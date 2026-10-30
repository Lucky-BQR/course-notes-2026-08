from pathlib import Path
import json,re,hashlib,csv,html,sys,shutil,zipfile
from xml.sax.saxutils import escape
from content import COURSES,EXTERNAL,INTRO,EDITORIAL,VERSION

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'docs'; ASSETS=SITE/'assets'; DOWNLOAD=SITE/'downloads'
for p in [ASSETS,DOWNLOAD,ROOT/'output/pdf',ROOT/'output/notes',ROOT/'qa']:p.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'data';DATA.mkdir(exist_ok=True)
SRC=Path(r'D:\gwl')
if '--refresh-sources' in sys.argv or not (DATA/'sources.json').exists():
    sources=[]
    for c in COURSES:
        for day in c['days']:
            folder=SRC/day/'output/pdf'
            manifests=json.loads((folder/'交付清单.json').read_text(encoding='utf-8'))
            candidates=list(folder.glob(f'00*全部{len(manifests)}篇*合订本.pdf'))
            assert len(candidates)==1,(day,'无法唯一确定当前版本合订本')
            combined=candidates[0].name
            for x in manifests:
                sid=f"{day}-{x['id']:02}"
                pdf=folder/x['file']; original=SRC/day/x['source']
                assert pdf.exists() and original.exists(),sid
                sources.append(dict(id=sid,course=c['slug'],date=day,number=x['id'],title=x['title'],pdf=x['file'],note_page=1,
                    combined=combined,combined_page=x['combined_start'],original=x['source'],
                    pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                    chapters=[s['key'] for s in c['sections'] if sid in s['refs']]))
    (DATA/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
sources=json.loads((DATA/'sources.json').read_text(encoding='utf-8'))
source_by_id={s['id']:s for s in sources}
ext_by_id={e[0]:e for e in EXTERNAL}
pattern=r'\[((?:8\.(?:15|16|27|28|29)-\d{2})|(?:E\d{2}))\]'
for c in COURSES:
    for s in c['sections']:
        for rid in re.findall(pattern,json.dumps(s,ensure_ascii=False)):
            assert rid in source_by_id or rid in ext_by_id,rid
assert len(sources)==118 and all(x['chapters'] for x in sources)

def rich(t):
    t=html.escape(t)
    def replace(m):
        k=m[1]
        if k in ext_by_id:return f'<a class="ref external" href="{ext_by_id[k][2]}" target="_blank" rel="noopener" title="{html.escape(ext_by_id[k][1])}">{k}</a>'
        return f'<button class="ref" type="button" data-source="{k}" aria-label="查看出处 {k}">{k}</button>'
    return re.sub(pattern,replace,t)

def flow_html(nodes):
    return '<ol class="flow" aria-label="逻辑关系图">'+''.join(f'<li><strong>{rich(a)}</strong><span>{rich(b)}</span></li>' for a,b in nodes)+'</ol>'

def section_html(s,n):
    return f'''<section class="chapter" id="{s['key']}" data-search="{html.escape(s['title'])}">
    <header class="chapter-heading"><span class="chapter-no">{n:02}</span><h2>{s['title']}</h2><a class="anchor" href="#{s['key']}" aria-label="链接到本章">#</a></header>
    <p class="lead">{rich(s['lead'])}</p>
    <div class="concepts">{''.join('<div class="concept"><h3>'+rich(a)+'</h3><p>'+rich(b)+'</p></div>' for a,b in s['cards'])}</div>
    <div class="table-scroll" role="region" aria-label="{s['title']}对照表" tabindex="0"><table><thead><tr>{''.join('<th scope="col">'+rich(x)+'</th>' for x in s['headers'])}</tr></thead><tbody>{''.join('<tr>'+''.join('<td>'+rich(x)+'</td>' for x in row)+'</tr>' for row in s['rows'])}</tbody></table></div>
    {flow_html(s['flow'])}<div class="explanation"><h3>把这些内容连起来</h3><p>{rich(s['explain'])}</p></div>
    <div class="review"><h3>复习与应用</h3><p>{rich(s['review'])}</p></div>
    <details class="chapter-sources"><summary>本章出处 · {len(s['refs'])} 份材料</summary><div>{' '.join(rich('['+x+']') for x in s['refs'])}</div></details></section>'''

def frame(title,body,course=None):
    theme=f' style="--accent:{course["color"]}"' if course else ''
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | 课程全局笔记</title><meta name="description" content="神经重置与女性脑科学课程的主题笔记、逻辑图、对照表和可追溯出处。"><link rel="stylesheet" href="assets/style.css"><script src="assets/data.js" defer></script><script src="assets/app.js" defer></script></head>
    <body{theme}><a class="skip" href="#main">跳到正文</a><header class="topbar"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">知</span>课程全局笔记</a><nav aria-label="全站导航"><a href="neural-reset.html">神经重置</a><a href="women-neuroscience.html">女性脑科学</a><a href="sources.html">出处索引</a><a href="index.html#downloads">下载资料</a></nav><button class="search-open" type="button">搜索笔记</button></header>
    {body}<footer class="footer">课程复习资料 · {VERSION} · 依据118份资料重新组织。课程观点、现场反馈与补充查证分别标示。</footer>
    <dialog id="source-dialog" aria-labelledby="source-title"><button class="dialog-close" aria-label="关闭出处">×</button><div id="source-content"></div></dialog>
    <dialog id="search-dialog" aria-labelledby="search-title"><button class="dialog-close" aria-label="关闭搜索">×</button><h2 id="search-title">搜索两门课程</h2><label for="search-input">输入主题、概念或出处编号</label><input id="search-input" type="search" autocomplete="off" placeholder="例如：睡眠、尿意、8.15-11"><p id="search-status" role="status"></p><div id="search-results"></div></dialog>
    <button class="back-top" type="button" aria-label="返回页首">返回页首</button></body></html>'''

search=[]
for c in COURSES:
    toc=''.join(f'<a href="#{s["key"]}"><span>{i:02}</span>{s["title"]}</a>' for i,s in enumerate(c['sections'],1))
    body=f'''<div class="reading-layout"><aside class="sidebar"><a class="back-home" href="index.html">两门课程总览</a><h2>{c['title']}</h2><p>{c['dates']}</p><nav aria-label="本课目录">{toc}</nav><a class="download-link" href="downloads/{c['slug']}.pdf" download>下载本课 PDF</a></aside><main id="main" class="reading"><header class="course-header"><p class="date">{c['dates']}</p><h1>{c['title']}</h1><p class="subtitle">{c['subtitle']}</p><p>{c['description']}</p><div class="course-actions"><a class="button" href="downloads/{c['slug']}.pdf" download>保存 PDF</a><button class="button secondary" onclick="window.print()">打印本页</button></div></header><details class="reading-note"><summary>如何阅读与查证</summary><p>{INTRO}</p><p>{EDITORIAL}</p><p>正文编号可点击查看具体文件和页码；原文与旧PDF未嵌入本网站。案例采用匿名主题描述。</p></details>
    {''.join(section_html(s,i) for i,s in enumerate(c['sections'],1))}<div class="end-nav"><a href="sources.html">查看完整出处索引</a><a href="index.html#downloads">获取全部资料</a></div></main></div>'''
    (SITE/f"{c['slug']}.html").write_text(frame(c['title'],body,c),encoding='utf-8')
    for s in c['sections']:
        text='\n'.join([s['lead'],*[' '.join(x) for x in s['cards']],*[' '.join(x) for x in s['rows']],s['explain'],s['review']])
        search.append(dict(title=s['title'],course=c['title'],url=c['slug']+'.html#'+s['key'],text=text))
    md=['# '+c['title']+'：'+c['subtitle'],c['dates'],INTRO,EDITORIAL]
    for s in c['sections']:
        md+=['\n## '+s['title'],s['lead']]
        md+=['\n### '+a+'\n'+b for a,b in s['cards']]
        md+=['\n| '+' | '.join(s['headers'])+' |','|---|---|---|']
        md+=['| '+' | '.join(row)+' |' for row in s['rows']]
        md+=['\n逻辑图：'+' → '.join(a+'（'+b+'）' for a,b in s['flow']),'\n'+s['explain'],'\n复习与应用：'+s['review'],'\n本章出处：'+'、'.join(s['refs'])]
    md+=['\n## 出处索引']
    md += [f"- [{x['id']}] {x['date']} / {x['original']}；《{x['pdf']}》第1页；《{x['combined']}》第{x['combined_page']}页。" for x in sources if x['course']==c['slug']]
    md+=['\n## 外部核对资料（2026-10-30）']+[f'- [{i}] [{t}]({u})：{d}' for i,t,u,d in EXTERNAL]
    (ROOT/'output/notes'/f"{c['title']}_全局笔记.md").write_text('\n\n'.join(md),encoding='utf-8')
    shutil.copy2(ROOT/'output/notes'/f"{c['title']}_全局笔记.md",DOWNLOAD/f"{c['slug']}.md")

home=f'''<main id="main" class="home"><section class="hero"><div><p class="date">2026年8月课程整理</p><h1>先看见全局，<br>再读懂每个问题。</h1><p class="hero-description">把五天的课堂资料连成两套完整笔记。<br>用概念图理解联系，用对照表看清差别，用出处回到具体材料。</p><a class="button" href="#courses">选择课题</a><a class="text-link" href="#downloads">下载完整资料包</a></div><div class="knowledge-map" aria-label="两门课的共同阅读结构"><div class="map-core">身体感受<br><span>连接概念与生活</span></div><div class="map-node node-a">概念<br><small>知道在说什么</small></div><div class="map-node node-b">案例<br><small>看见变化过程</small></div><div class="map-node node-c">功能<br><small>回到真实任务</small></div><div class="map-node node-d">出处<br><small>每一项可追溯</small></div></div></section>
    <section id="courses"><div class="section-intro"><h2>按课题完整阅读</h2><p>章节跟随知识主线，日期保留在出处中。</p></div><div class="course-grid">{''.join(f'<a class="course-tile" style="--tile-color:{c["color"]}" href="{c["slug"]}.html"><p class="date">{c["dates"]}</p><h3>{c["title"]}</h3><p class="tile-subtitle">{c["subtitle"]}</p><p>{c["description"]}</p><div class="tile-meta">{len(c["sections"])}个主题 · {c["count"]}份资料 <strong>进入笔记</strong></div></a>' for c in COURSES)}</div></section>
    <section class="shared-map"><h2>两门课程，怎样连接？</h2>{flow_html([['感觉与体验','本人感到什么'],['动作与功能','实际能做什么'],['场景与变化','在什么条件下改变'],['记录与核查','来源能说明什么']])}<p>神经重置侧重疼痛、区域观察和日常动作；女性脑科学进一步展开睡眠、周期、消化、盆底和亲密体验。共用清楚的记录方法，各主题保留自身的知识与评估范围。</p></section>
    <section id="downloads"><div class="section-intro"><h2>带走完整资料</h2><p>在线阅读、PDF与可编辑文本采用同一套内容。</p></div><div class="download-grid"><a href="downloads/course-notes-complete.zip" download><strong>完整阅读包</strong><span>两课PDF、合订本、文本、出处索引与离线网站</span></a><a href="downloads/all-courses.pdf" download><strong>两课 PDF 合订本</strong><span>适合连续阅读、打印与归档</span></a><a href="downloads/neural-reset.pdf" download><strong>神经重置 PDF</strong><span>感觉、疼痛与日常功能</span></a><a href="downloads/women-neuroscience.pdf" download><strong>女性脑科学 PDF</strong><span>三天内容的全局整理</span></a><a href="downloads/source-index.csv" download><strong>出处清单 CSV</strong><span>118份材料的文件、页码与主题映射</span></a><a href="downloads/site-source.zip" download><strong>网站与编辑源码</strong><span>用于保存、修改与再次部署</span></a></div></section>
    <section class="editorial-note"><h2>这套笔记的整理方式</h2><p>{INTRO}</p><p>{EDITORIAL}</p><p>118份材料均已纳入阅读与主题映射；8.15的11号文件已补齐。现有材料没有可统一核验的录音时间戳，因此采用文件编号和PDF页序定位。</p><a href="sources.html">查看课程来源与外部核对资料</a></section></main>'''
(SITE/'index.html').write_text(frame('两门课程总览',home),encoding='utf-8')

source_rows=''.join(f'<tr id="src-{x["id"]}" data-source-row><td><button class="ref" data-source="{x["id"]}">{x["id"]}</button></td><td>{html.escape(x["title"])}</td><td>{x["original"]}<br><small>独立笔记第1页 / 合订本第{x["combined_page"]}页</small></td><td>'+''.join(f'<a class="chapter-tag" href="{x["course"]}.html#{key}">{next(s["title"].split("：")[0] for c in COURSES if c["slug"]==x["course"] for s in c["sections"] if s["key"]==key)}</a>' for key in x['chapters'])+'</td></tr>' for x in sources)
source_body=f'''<main id="main" class="sources-page"><header class="course-header"><h1>出处索引</h1><p>按日期与文件编号，找到每一条知识的来处。</p></header><div class="source-note"><p>来源编号如 <strong>8.15-11</strong>，表示8月15日第11号文件。每项可查独立PDF的第1页和当日合订本的物理页序。原文留在原资料目录，本网站与阅读包不重复附上。</p><label for="source-filter">筛选日期、编号或标题</label><input id="source-filter" type="search" placeholder="例如：8.29、尿意、11"><p id="source-count" role="status">共118份资料</p></div><div class="table-scroll"><table><thead><tr><th>编号</th><th>原有笔记标题</th><th>文件与页码</th><th>本书主题</th></tr></thead><tbody>{source_rows}</tbody></table></div><section id="external-sources"><h2>外部核对资料</h2><p>以下为本次补充核对的资料，核对日期：2026-10-30。它们用于相关基础概念和边界，不表示机构认可本课程技术。</p>{''.join(f'<article class="external-source" id="{i}"><h3><span>{i}</span> <a href="{u}" target="_blank" rel="noopener">{t}</a></h3><p>{d}</p></article>' for i,t,u,d in EXTERNAL)}</section></main>'''
(SITE/'sources.html').write_text(frame('出处索引',source_body),encoding='utf-8')
(ASSETS/'data.js').write_text('window.NOTE_DATA='+json.dumps(dict(sources=sources,search=search),ensure_ascii=False)+';',encoding='utf-8')
with (DOWNLOAD/'source-index.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['来源编号','课题','标题','源文件','独立PDF','笔记页','当日合订本','合订本物理页序','全局笔记主题','原文件SHA256'])
    for x in sources:w.writerow([x['id'],next(c['title'] for c in COURSES if c['slug']==x['course']),x['title'],x['date']+'/'+x['original'],x['pdf'],1,x['combined'],x['combined_page'],';'.join(x['chapters']),x['original_sha256']])
(SITE/'.nojekyll').touch()

if '--html-only' not in sys.argv:
    from make_pdf import create_pdfs
    create_pdfs(ROOT,COURSES,sources,EXTERNAL,INTRO,EDITORIAL)
print(json.dumps({'courses':len(COURSES),'sections':sum(len(c['sections']) for c in COURSES),'sources':len(sources),'site':str(SITE)},ensure_ascii=False))
