(()=>{'use strict';
 const $=s=>document.querySelector(s), all=s=>[...document.querySelectorAll(s)];
 const sourceDialog=$('#source-dialog'),searchDialog=$('#search-dialog');
 const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let previousFocus=null;
 const globalEntries=window.NOTE_DATA.search.filter(s=>s.kind!=='daily');
 function returnContext(button){
   const file=location.pathname.split('/').pop(),chapter=button?.closest('.chapter');
   const candidate=chapter?file+'#'+chapter.id:new URLSearchParams(location.search).get('from');
   return globalEntries.find(s=>s.url===candidate)||globalEntries.find(s=>s.url===new URLSearchParams(location.search).get('from'));
 }
 function detailUrl(source,button){const context=returnContext(button),parts=source.detail_url.split('#');return parts[0]+(context?'?from='+encodeURIComponent(context.url):'')+'#'+parts[1];}
 function show(dialog){previousFocus=document.activeElement;dialog.showModal();}
 function close(dialog){dialog.close();if(previousFocus)previousFocus.focus();}
 all('dialog').forEach(d=>{d.querySelector('.dialog-close').addEventListener('click',()=>close(d));d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)close(d);}});});
 document.addEventListener('click',e=>{const b=e.target.closest('[data-source]');if(!b)return;const s=window.NOTE_DATA.sources.find(x=>x.id===b.dataset.source);if(!s)return;
 const detail=escape(detailUrl(s,b));
 $('#source-content').innerHTML=`<p class="source-code">课程出处 ${escape(s.id)}</p><h2 id="source-title">${escape(s.title)}</h2><a class="source-action" data-detail-link href="${detail}">阅读这一篇详细笔记</a><dl><dt>来源文件</dt><dd><a data-detail-link href="${detail}">${escape(s.date+'/'+s.original)} 对应的笔记</a></dd><dt>独立笔记</dt><dd><a href="${escape(s.note_pdf)}" target="_blank" rel="noopener">${escape(s.title)} · 打开笔记 PDF</a><small class="source-original">原资料：${escape(s.pdf)} · 第1页</small></dd><dt>当日合订本</dt><dd><a href="${escape(s.note_pdf)}" target="_blank" rel="noopener">${escape(s.date)} 每日笔记合订本 · 第${s.daily_page}页</a><small class="source-original">原资料：${escape(s.combined)} · 第${s.combined_page}页（PDF物理页序）</small></dd></dl><p class="source-dialog-note">网页和新合订本收录详细笔记；原文仍在原资料中。上方链接可直接定位到本篇。</p><div class="source-detail-links"><a href="${escape(s.daily_url)}">浏览 ${escape(s.date)} 当日全部笔记</a><a href="sources.html#src-${s.id}">完整出处索引</a></div>`;show(sourceDialog);
 });
 document.addEventListener('click',e=>{const link=e.target.closest('dialog a');if(link){const dialog=link.closest('dialog');dialog.close();}});
 const context=returnContext();if(context)all('.return-context').forEach(link=>{link.href=context.url;link.textContent='返回刚才的全局章节：'+context.title;link.hidden=false;});
 function jumpToHash(){let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}const target=document.getElementById(id);if(target)target.scrollIntoView({behavior:'instant',block:'start'});}
 window.addEventListener('load',jumpToHash);window.addEventListener('hashchange',jumpToHash);
 $('.search-open').addEventListener('click',()=>{show(searchDialog);$('#search-input').focus();});
 function search(){const q=$('#search-input').value.trim().toLowerCase(),out=$('#search-results');out.replaceChildren();if(!q){$('#search-status').textContent='输入一个主题，查找对应章节和原有材料。';return;}
 const results=window.NOTE_DATA.search.filter(s=>(s.title+' '+s.course+' '+s.text).toLowerCase().includes(q));
 const sourceResults=window.NOTE_DATA.sources.filter(s=>(s.id+' '+s.title).toLowerCase().includes(q));
 const dailyCount=results.filter(s=>s.kind==='daily').length;
 $('#search-status').textContent=`找到 ${results.length-dailyCount} 个全局章节、${dailyCount} 篇每日详解、${sourceResults.length} 份出处`;
 for(const s of results){const pos=s.text.toLowerCase().indexOf(q);const excerpt=s.text.slice(Math.max(0,pos-35),Math.max(0,pos-35)+135).replace(/\[(8\.[\d-]+|E\d+)\]/g,'');const a=document.createElement('a');a.className='search-result';a.href=s.url;a.innerHTML=`<small>${escape(s.course)}</small><strong>${escape(s.title)}</strong><p>${escape(excerpt)}…</p>`;a.addEventListener('click',()=>searchDialog.close());out.append(a);}
 for(const s of sourceResults){const a=document.createElement('a');a.className='search-result';a.href=s.detail_url;a.innerHTML=`<small>来源 ${escape(s.id)} · 点击阅读详解</small><strong>${escape(s.title)}</strong><p>原独立笔记第1页 · 原当日合订本第${s.combined_page}页</p>`;a.addEventListener('click',()=>searchDialog.close());out.append(a);}
 if(!results.length&&!sourceResults.length)out.innerHTML='<p>没有匹配内容。可尝试更短的词，如“排尿”“感觉”或“8.15”。</p>';
 }
 $('#search-input').addEventListener('input',search);search();
 const filter=$('#source-filter');if(filter)filter.addEventListener('input',()=>{const q=filter.value.trim().toLowerCase();let n=0;all('[data-source-row]').forEach(r=>{r.hidden=!r.textContent.toLowerCase().includes(q);if(!r.hidden)n++;});$('#source-count').textContent=`显示 ${n} / 118 份资料`;});
 const chapters=all('.chapter');if(chapters.length&&'IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{for(const e of entries){if(e.isIntersecting){all('.sidebar nav a').forEach(a=>{const active=a.hash==='#'+e.target.id;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});}}},{rootMargin:'-5% 0px -65% 0px'});chapters.forEach(s=>observer.observe(s));}
 const top=$('.back-top');top.addEventListener('click',()=>window.scrollTo({top:0,left:0,behavior:'instant'}));
})();
