
'use strict';
const source='__SOURCE_SHA__', expectedDoc='1rBx2v_8ovMuzS0WQzcoPQwWAMNGIHM9TQLSrZkm80Fs';
const frame=document.querySelector('#site'), route=document.querySelector('#route'), width=document.querySelector('#width');
const state=document.querySelector('#state'), result=document.querySelector('#result');
let results=[];
function record(value){results.push({time:new Date().toISOString(),source,...value});result.textContent=JSON.stringify(results,null,2);state.textContent=value.result||value.kind;}
function context(){const w=frame.contentWindow,d=w.document;if(d.location.origin!==location.origin)throw new Error('Aynı preview kaynağına erişilemiyor');return {w,d};}
const tick=w=>new Promise(resolve=>w.requestAnimationFrame(()=>w.requestAnimationFrame(resolve)));
function openPage(){frame.style.width=Number(width.value)+'px';state.textContent='Önizleme yükleniyor';frame.src=route.value;}
frame.addEventListener('load',()=>{try{const {w,d}=context();state.textContent='Yüklendi: '+d.location.pathname+' / '+w.innerWidth+' CSS px';}catch(e){state.textContent='Erişim tamamlanmadı: '+e.message;}});
document.querySelector('#open').addEventListener('click',openPage);
document.querySelector('#check').addEventListener('click',async()=>{
 state.textContent='Kontrol ediliyor';try{const {w,d}=context();await d.fonts.ready;await tick(w);const requested=Number(width.value);
  const robots=d.querySelector('meta[name="robots"]')?.content||'',canonical=d.querySelector('link[rel="canonical"]')?.href||'';
  const a=d.querySelector('a[href*="'+expectedDoc+'"]');if(!a)throw new Error('Doğru Casting Brief bağlantısı yok');
  a.scrollIntoView({block:'center',behavior:'instant'});await tick(w);const r=a.getBoundingClientRect(),hit=d.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
  const cta={href:a.href,target:a.target,rel:a.rel,left:r.left,right:r.right,height:r.height,hit:!!hit&&(a===hit||a.contains(hit))};
  const images=[...d.images].filter(i=>{const r=i.getBoundingClientRect();return r.width>0&&r.height>0&&r.top<w.innerHeight&&r.bottom>0&&r.left<w.innerWidth&&r.right>0;});
  await Promise.all(images.map(i=>i.complete?Promise.resolve():new Promise(resolve=>{i.addEventListener('load',resolve,{once:true});i.addEventListener('error',resolve,{once:true});setTimeout(resolve,8000);})));await tick(w);
  const imageState=images.map(i=>({src:i.getAttribute('src'),complete:i.complete,naturalWidth:i.naturalWidth}));
  const value={kind:'remote-layout',path:d.location.pathname,requested,innerWidth:w.innerWidth,innerHeight:w.innerHeight,scrollWidth:d.documentElement.scrollWidth,h1:d.querySelectorAll('h1').length,robots,canonical,cta,visibleImages:imageState};
  value.result=w.innerWidth===requested&&value.path===route.value&&value.scrollWidth<=requested+2&&value.h1===1&&robots.includes('noindex')&&canonical==='https://serdararminsargut.com'+route.value&&cta.hit&&cta.left>=-1&&cta.right<=requested+1&&cta.target==='_blank'&&['noopener','noreferrer'].every(x=>cta.rel.split(/\s+/).includes(x))&&imageState.every(i=>i.complete&&i.naturalWidth>0)?'PASS':'FAIL';record(value);
 }catch(e){record({kind:'remote-layout',result:'NOT_TESTED',error:e.message});}
});
document.querySelector('#gallery').addEventListener('click',async()=>{
 state.textContent='Galeri kontrol ediliyor';
 try{const {w,d}=context();if(d.location.pathname!=='/')throw new Error('Galeri ana sayfada kontrol edilir');
  const filter=d.querySelector('[data-model-filter="sport"]'),photo=d.querySelector('[data-lightbox]:not([data-instagram-tile])'),dialog=d.querySelector('.lightbox');
  if(!filter||!photo||!dialog)throw new Error('Galeri kontrolleri eksik');
  filter.click();await tick(w);const filtered=filter.getAttribute('aria-pressed')==='true';filter.click();await tick(w);
  photo.scrollIntoView({block:'center',behavior:'instant'});photo.click();await tick(w);const opened=dialog.classList.contains('open');dialog.querySelector('button').click();await tick(w);
  const closed=!dialog.classList.contains('open');
  record({kind:'remote-gallery',path:d.location.pathname,innerWidth:w.innerWidth,filter:filtered,opened,closed,result:filtered&&opened&&closed?'PASS':'FAIL'});
 }catch(e){record({kind:'remote-gallery',result:'NOT_TESTED',error:e.message});}
});
document.querySelector('#headers').addEventListener('click',async()=>{
 state.textContent='Aynı preview kaynağından HTTP başlıkları okunuyor';
 for(const path of ['/','/links/en/','/robots.txt']){
  try{const response=await fetch(path,{method:'HEAD',credentials:'same-origin',cache:'no-store'}),x=response.headers.get('X-Robots-Tag')||'';
   record({kind:'remote-http-header',method:'HEAD',path,status:response.status,finalURL:response.url,contentType:response.headers.get('Content-Type'),xRobotsTag:x,result:response.status===200&&new URL(response.url).origin===location.origin&&/\bnoindex\b/i.test(x)?'PASS':'NOT_VERIFIED'});
  }catch(e){record({kind:'remote-http-header',path,result:'NOT_TESTED',error:e.message});}
 }
});
