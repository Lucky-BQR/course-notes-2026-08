(()=>{'use strict';
 const $=s=>document.querySelector(s), all=s=>[...document.querySelectorAll(s)];
 const sourceDialog=$('#source-dialog'),searchDialog=$('#search-dialog');
 const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let previousFocus=null;
 function show(dialog){previousFocus=document.activeElement;dialog.showModal();}
 function close(dialog){dialog.close();if(previousFocus)previousFocus.focus();}
 all('dialog').forEach(d=>{d.querySelector('.dialog-close').addEventListener('click',()=>close(d));d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)close(d);}});});
 document.addEventListener('click',e=>{const b=e.target.closest('[data-source]');if(!b)return;const s=window.NOTE_DATA.sources.find(x=>x.id===b.dataset.source);if(!s)return;
 $('#source-content').innerHTML=`<p class="source-code">课程出处 ${escape(s.id)}</p><h2 id="source-title">${escape(s.title)}</h2><dl><dt>源文件</dt><dd>${escape(s.date+'/'+s.original)}</dd><dt>独立笔记</dt><dd>${escape(s.pdf)}<br><strong>第1页</strong></dd><dt>当日合订本</dt><dd>${escape(s.combined)}<br><strong>第${s.combined_page}页（PDF物理页序）</strong></dd></dl><p>原文件保留在相应日期资料夹；本网站不附原文。编号和页码用于回查客户已有资料。</p><p><a href="sources.html#src-${s.id}">在完整出处索引中查看</a></p>`;show(sourceDialog);
 });
 $('.search-open').addEventListener('click',()=>{show(searchDialog);$('#search-input').focus();});
 function search(){const q=$('#search-input').value.trim().toLowerCase(),out=$('#search-results');out.replaceChildren();if(!q){$('#search-status').textContent='输入一个主题，查找对应章节和原有材料。';return;}
 const results=window.NOTE_DATA.search.filter(s=>(s.title+' '+s.course+' '+s.text).toLowerCase().includes(q));
 const sourceResults=window.NOTE_DATA.sources.filter(s=>(s.id+' '+s.title).toLowerCase().includes(q));
 $('#search-status').textContent=`找到 ${results.length} 个章节、${sourceResults.length} 份出处`;
 for(const s of results){const pos=s.text.toLowerCase().indexOf(q);const excerpt=s.text.slice(Math.max(0,pos-35),Math.max(0,pos-35)+135).replace(/\[(8\.[\d-]+|E\d+)\]/g,'');const a=document.createElement('a');a.className='search-result';a.href=s.url;a.innerHTML=`<small>${escape(s.course)}</small><strong>${escape(s.title)}</strong><p>${escape(excerpt)}…</p>`;a.addEventListener('click',()=>searchDialog.close());out.append(a);}
 for(const s of sourceResults){const a=document.createElement('a');a.className='search-result';a.href=`sources.html#src-${s.id}`;a.innerHTML=`<small>来源 ${escape(s.id)}</small><strong>${escape(s.title)}</strong><p>独立笔记第1页 · 当日合订本第${s.combined_page}页</p>`;a.addEventListener('click',()=>searchDialog.close());out.append(a);}
 if(!results.length&&!sourceResults.length)out.innerHTML='<p>没有匹配内容。可尝试更短的词，如“排尿”“感觉”或“8.15”。</p>';
 }
 $('#search-input').addEventListener('input',search);search();
 const filter=$('#source-filter');if(filter)filter.addEventListener('input',()=>{const q=filter.value.trim().toLowerCase();let n=0;all('[data-source-row]').forEach(r=>{r.hidden=!r.textContent.toLowerCase().includes(q);if(!r.hidden)n++;});$('#source-count').textContent=`显示 ${n} / 118 份资料`;});
 const chapters=all('.chapter');if(chapters.length&&'IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{for(const e of entries){if(e.isIntersecting){all('.sidebar nav a').forEach(a=>{const active=a.hash==='#'+e.target.id;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});}}},{rootMargin:'-5% 0px -65% 0px'});chapters.forEach(s=>observer.observe(s));}
 const top=$('.back-top');top.addEventListener('click',()=>window.scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'}));window.addEventListener('scroll',()=>top.classList.toggle('show',window.scrollY>600),{passive:true});
})();
