from pathlib import Path
import re,json,shutil
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor,white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle
from pypdf import PdfReader,PdfWriter
from pypdf.generic import DictionaryObject,ArrayObject,NameObject

W,H=744,1052;M=38;CW=W-2*M
INK='#203344';MUTED='#657583';LINE='#dce5ea'
pdfmetrics.registerFont(TTFont('Yahei','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('YaheiBold','C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('Yahei',normal='Yahei',bold='YaheiBold')

def create_pdfs(root,courses,sources,external,intro,editorial):
    metrics=[];ext={e[0]:e for e in external}
    def markup(text):
        def sub(m):
            k=m[1]
            if k in ext:return '<link href="'+escape(ext[k][2])+'" color="#77519a"><font size="8.5">['+k+']</font></link>'
            return '<link href="#src-'+k+'" color="#176b80"><font size="8.5">['+k+']</font></link>'
        return re.sub(r'\[((?:8\.(?:15|16|27|28|29)-\d{2})|(?:E\d{2}))\]',sub,escape(text)).replace('\n','<br/>')
    def p(t,size=11.6,bold=False,color=INK):
        return Paragraph(markup(t),ParagraphStyle('t',fontName='YaheiBold' if bold else 'Yahei',fontSize=size,leading=size*1.6,textColor=HexColor(color),wordWrap='CJK',splitLongWords=True))
    def height(t,w,size=11.6,bold=False):return p(t,size,bold).wrap(w,2000)[1]
    def draw(t,x,y,w,size=11.6,bold=False,color=INK):
        q=p(t,size,bold,color);_,h=q.wrap(w,2000);q.drawOn(cv,x,y-h);return y-h
    def box(x,y,w,h,fill):
        cv.setFillColor(HexColor(fill));cv.roundRect(x,y-h,w,h,5,stroke=0,fill=1)
    def footer(title):
        cv.setStrokeColor(HexColor(LINE));cv.line(M,35,W-M,35)
        cv.setFont('Yahei',8);cv.setFillColor(HexColor(MUTED));cv.drawString(M,20,title+' · 全局笔记 / 2026-10-30');cv.drawRightString(W-M,20,str(cv.getPageNumber()))
    def heading(title,kicker):
        draw(kicker,M,H-32,CW,9,color=MUTED)
        return draw(title,M,H-60,CW,23,True)-19
    def table(s,size):
        widths=[CW*.18,CW*.39,CW*.43]
        obj=Table([[p(t,size-.1,True) for t in s['headers']]]+[[p(t,size-.3) for t in row] for row in s['rows']],colWidths=widths)
        obj.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#edf3f6')),('BACKGROUND',(0,1),(0,-1),HexColor('#fafcfd')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.45,HexColor(LINE)),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
        return obj,obj.wrap(CW,3000)[1]
    def estimate(s,size):
        cardw=(CW-20)/3
        ch=max(height(a,cardw-24,size,True)+height(b,cardw-24,size-.2)+12 for a,b in s['cards'])+23
        t,th=table(s,size)
        fh=max(height(a,CW/4-18,size-.1,True)+height(b,CW/4-18,size-1)+10 for a,b in s['flow'])+21
        lead=height(s['lead'],CW,size)
        ex=height(s['explain'],CW,size-.2)
        review=height(s['review'],CW-24,size-.4)+38
        return lead,ch,t,th,fh,ex,review,lead+ch+th+fh+ex+review+116
    for course in courses:
        out=root/'output/pdf'/f"{course['title']}_全局笔记.pdf"
        cv=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1)
        cv.setTitle(course['title']+' | 全局笔记');cv.setAuthor('课程资料整理');cv.setSubject(course['subtitle'])
        cv.bookmarkPage('cover');cv.addOutlineEntry(course['title'],'cover',0)
        accent=course['color']
        cv.setFillColor(HexColor(accent));cv.rect(0,H-15,W,15,fill=1,stroke=0)
        y=draw(course['dates'],M,H-75,CW,12,color=MUTED)
        y=draw(course['title'],M,y-35,CW,43,True,accent)
        y=draw(course['subtitle'],M,y-18,CW,23,True)-24
        y=draw(course['description'],M,y,CW,14)-24
        box(M,y,CW,100,'#f1f6f9')
        draw('阅读方式',M+17,y-14,CW-34,13,True)
        draw('先看地图，再读主题；用表格比较，用逻辑图串联。正文编号可跳转到出处索引；无需在大段原文中反复寻找。',M+17,y-42,CW-34,12)
        y-=130
        y=draw('本课目录',M,y,CW,18,True)-14
        for i,s in enumerate(course['sections'],1):
            cv.linkRect('',s['key'],(M,y-30,W-M,y),relative=0,thickness=0)
            y=draw(f"{i:02}   {s['title']}",M,y,CW,12.5)-8
        y-=12
        y=draw(f"资料范围：{course['count']}份。各篇主题映射与具体文件页码见书末出处索引。",M,y,CW,10.2,color=MUTED)-12
        draw('本书用于课程学习与复盘。课堂模型、现场观察、整理补充和外部核对分别表达；原文与旧版逐篇PDF保留在原资料夹。',M,y,CW,10.2,color=MUTED)
        footer(course['title']);cv.showPage()
        for i,s in enumerate(course['sections'],1):
            cv.bookmarkPage(s['key']);cv.addOutlineEntry(s['title'],s['key'],1)
            y=heading(s['title'],course['title']+f' / 主题 {i:02}')
            size=11.8
            while True:
                vals=estimate(s,size)
                if vals[-1]<=y-58:break
                size-=.2
                if size<10.2:raise ValueError(f"页面过满：{course['title']}/{s['key']}，需拆页，不继续缩字")
            lead,ch,t,th,fh,ex,rh,total=vals
            y=draw(s['lead'],M,y,CW,size)-18
            cw=(CW-20)/3
            for n,(a,b) in enumerate(s['cards']):
                x=M+n*(cw+10);box(x,y,cw,ch,['#eaf7fa','#f4f0fa','#f3f7e8'][n])
                cy=draw(a,x+12,y-11,cw-24,size,True)-8
                draw(b,x+12,cy,cw-24,size-.2)
            y-=ch+20;t.drawOn(cv,M,y-th);y-=th+23
            fw=CW/4
            for n,(a,b) in enumerate(s['flow']):
                x=M+n*fw
                cv.setStrokeColor(HexColor(accent));cv.setLineWidth(1.4);cv.line(x,y,x+fw-18,y)
                fy=draw(a,x,y-10,fw-18,size-.1,True,accent)-6
                draw(b,x,fy,fw-18,size-1,color=MUTED)
                if n<3:
                    cv.setLineWidth(1);cv.line(x+fw-13,y-18,x+fw-4,y-18);cv.line(x+fw-4,y-18,x+fw-8,y-14);cv.line(x+fw-4,y-18,x+fw-8,y-22)
            y-=fh+16
            y=draw('把这些内容连起来',M,y,CW,size,True)-7
            y=draw(s['explain'],M,y,CW,size-.2)-17
            box(M,y,CW,rh,'#f4f7fa');ry=draw('复习与应用',M+12,y-9,CW-24,size,True)-6
            end=draw(s['review'],M+12,ry,CW-24,size-.4)
            if end<50:raise ValueError(f"内容越界：{s['key']} {end}")
            metrics.append(dict(course=course['title'],chapter=s['key'],page=cv.getPageNumber(),font=round(size,2),bottom=round(end,2)))
            footer(course['title']);cv.showPage()
        selected=[x for x in sources if x['course']==course['slug']]
        for offset in range(0,len(selected),12):
            if offset==0:cv.bookmarkPage('sources');cv.addOutlineEntry('课程出处索引','sources',1)
            y=heading('课程出处索引'+('（续）' if offset else ''),course['title']+' / 资料定位')
            y=draw('编号对应日期与文件；独立PDF第1页为原有笔记。合订本页码指PDF物理页序，原文仍保留在原资料夹。',M,y,CW,10.5,color=MUTED)-18
            for x in selected[offset:offset+12]:
                cv.bookmarkHorizontalAbsolute('src-'+x['id'],y)
                y=draw(f"[{x['id']}] {x['title']}",M,y,CW,10.6,True)-3
                y=draw('独立PDF：'+x['pdf'],M+12,y,CW-12,9.2,color=MUTED)-2
                y=draw(f"{x['date']}/{x['original']}   |   笔记第1页   |   当日合订本第{x['combined_page']}页",M+12,y,CW-12,9.2,color=MUTED)-10
            if y<45:raise ValueError('出处索引越界 '+str(y))
            footer(course['title']);cv.showPage()
        cv.bookmarkPage('external');cv.addOutlineEntry('外部核对与阅读说明','external',1)
        y=heading('外部核对与阅读说明',course['title']+' / 参考资料')
        used=set(re.findall(r'\[(E\d+)\]',json.dumps(course,ensure_ascii=False)))
        for key,title,url,desc in external:
            if key not in used:continue
            cv.linkURL(url,(M,y-22,W-M,y),relative=0,thickness=0)
            y=draw(f'[{key}] {title}',M,y,CW,12,True)-6
            y=draw(desc,M,y,CW,10.5)-5
            y=draw(url,M,y,CW,8.4,color='#176b80')-17
        y=draw('整理口径',M,y-10,CW,15,True)-12
        y=draw(editorial,M,y,CW,10.7)-15
        y=draw('引用说明：以客户提供的课程标题与日期归档。课堂来源指向已生成的结构化笔记；外部核对仅用于对应基础知识与关键边界，不表示相关机构认可课堂技术。没有可统一核验的录音时间戳，因此不编造分钟定位。',M,y,CW,10.5)-15
        draw('版本：2026-10-30。8.15的11号文件已补齐；全部118份材料均完成通读与主题映射。原始资料未改动，公开版不附原文、个人身份或私人经历细节。',M,y,CW,10.5,color=MUTED)
        footer(course['title']);cv.save()
        shutil.copy2(out,root/'docs/downloads'/f"{course['slug']}.pdf")
    writer=PdfWriter()
    for c in courses:
        reader=PdfReader(str(root/'output/pdf'/f"{c['title']}_全局笔记.pdf"))
        offset=len(writer.pages)
        page_map={pg.indirect_reference.idnum:offset+i for i,pg in enumerate(reader.pages)}
        saved_annotations=[]
        for pg in reader.pages:
            annotations=pg.pop('/Annots',ArrayObject())
            saved_annotations.append(annotations)
            writer.add_page(pg)
        parent=writer.add_outline_item(c['title'],offset)
        for i,s in enumerate(c['sections'],1):writer.add_outline_item(s['title'],offset+i,parent=parent)
        for i,pg in enumerate(reader.pages):
            for ref in saved_annotations[i]:
                old=ref.get_object();new=DictionaryObject()
                for key,value in old.items():
                    if key not in ['/P','/Dest']:new[key]=value.clone(writer)
                if '/Dest' in old:
                    dest=old['/Dest'];target=page_map[dest[0].idnum]
                    new[NameObject('/Dest')]=ArrayObject([writer.pages[target].indirect_reference]+[v.clone(writer) for v in dest[1:]])
                new[NameObject('/P')]=writer.pages[offset+i].indirect_reference
                targetpage=writer.pages[offset+i]
                if '/Annots' not in targetpage:targetpage[NameObject('/Annots')]=ArrayObject()
                targetpage['/Annots'].append(writer._add_object(new))
    writer.add_metadata({'/Title':'两课全局笔记合订本','/Author':'课程资料整理'})
    with (root/'output/pdf/两课全局笔记_合订本.pdf').open('wb') as f:writer.write(f)
    shutil.copy2(root/'output/pdf/两课全局笔记_合订本.pdf',root/'docs/downloads/all-courses.pdf')
    (root/'qa/pdf-layout.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    print([(c['title'],len(PdfReader(str(root/'output/pdf'/f"{c['title']}_全局笔记.pdf")).pages)) for c in courses])
