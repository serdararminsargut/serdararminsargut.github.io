
(()=>{
  // GA4 receives the landing parameters in the head. Afterwards, remove
  // tracking-only parameters without redirecting or requesting the page again.
  const cleanTrackingUrl=()=>{try{
    const cleanUrl=new URL(window.location.href);
    const trackingParams=['fbclid','gclid','dclid','msclkid','utm_source','utm_medium','utm_campaign','utm_content','utm_term','utm_id'];
    let urlChanged=false;
    trackingParams.forEach((param)=>{
      if(cleanUrl.searchParams.has(param)){
        cleanUrl.searchParams.delete(param);
        urlChanged=true;
      }
    });
    if(urlChanged){
      const remaining=cleanUrl.searchParams.toString();
      window.history.replaceState(window.history.state,'',cleanUrl.pathname+(remaining?('?'+remaining):'')+cleanUrl.hash);
    }
  }catch(e){}};
  if(document.readyState==='complete') cleanTrackingUrl();
  else window.addEventListener('load',cleanTrackingUrl,{once:true});

  const IG_URL='https://www.instagram.com/serdararminsargutt/';
  const lang=document.documentElement.lang||'uz';
  const copy={"lang":"uz","gallery_note":"Tanlangan fotosuratlar Instagram portfoliysini to‘g‘ridan-to‘g‘ri ochadi. Boshqa rasmlarni kattalashtirish uchun bosing.","gallery_cta_a":"Instagramdagi hozirgi portfolioni ko‘rish","gallery_cta_b":"Instagramdagi yangi rasmlarni ko‘rish","main_a":"Instagramdagi hozirgi portfolioni ko‘rish","main_b":"Instagramdagi yangi suratga olishlarni ko‘rish","badge":"Instagram ↗","mobile_a":"Instagram • Hozirgi portfolio","mobile_b":"Instagram • Yangi suratga olishlar"};
  const GA_ID='G-H894LKL93J';
  let variant='A';
  try{
    variant=localStorage.getItem('sas_ig_variant')||'';
    if(variant!=='A'&&variant!=='B'){
      variant=Math.random()<0.5?'A':'B';
      localStorage.setItem('sas_ig_variant',variant);
    }
  }catch(e){ variant='A'; }

  const sendGA=(eventName,params={})=>{
    const payload={...params,send_to:GA_ID,transport_type:'beacon'};
    try{
      if(typeof window.gtag==='function'){
        window.gtag('event',eventName,payload);
        return true;
      }
      window.dataLayer=window.dataLayer||[];
      window.dataLayer.push(['event',eventName,payload]);
    }catch(e){}
    return false;
  };

  const trackIg=(placement)=>{
    const payload={placement,variant,language:lang,page_path:location.pathname,link_url:'https://www.instagram.com/serdararminsargutt/'};
    try{if(window.zaraz&&typeof window.zaraz.track==='function') window.zaraz.track('instagram_click',payload);}catch(e){}
    sendGA('instagram_click',payload);
    try{sessionStorage.setItem('sas_last_ig_click',JSON.stringify({ts:Date.now(),...payload}));}catch(e){}
  };
  window.sasTrackInstagram=trackIg;

  document.querySelectorAll('[data-ig-ab="main"]').forEach(el=>{el.textContent=variant==='A'?copy.main_a:copy.main_b;el.dataset.igVariant=variant;});
  document.querySelectorAll('[data-ig-ab="gallery"]').forEach(el=>{el.textContent=variant==='A'?copy.gallery_cta_a:copy.gallery_cta_b;el.dataset.igVariant=variant;});
  document.querySelectorAll('[data-ig-ab="mobile"]').forEach(el=>{el.textContent=variant==='A'?copy.mobile_a:copy.mobile_b;el.dataset.igVariant=variant;});

  document.querySelectorAll('a[data-ig-placement]').forEach(a=>{
    a.addEventListener('click',()=>trackIg(a.dataset.igPlacement||'instagram_link'));
  });
  document.querySelectorAll('a[href^="mailto:"]').forEach(a=>{a.addEventListener('click',()=>{sendGA('contact_email_click',{placement:'contact',language:lang,page_path:location.pathname,link_url:a.href});});});
  document.querySelectorAll('a[data-social-platform]').forEach(a=>{
    a.addEventListener('click',()=>{
      const payload={platform:a.dataset.socialPlatform,placement:a.dataset.socialPlacement||'contact',language:lang,page_path:location.pathname,link_url:a.href};
      try{if(window.zaraz&&typeof window.zaraz.track==='function') window.zaraz.track('social_click',payload);}catch(e){}
      sendGA('social_click',payload);
    });
  });
  document.querySelectorAll('[data-instagram-tile="true"]').forEach(btn=>{
    btn.addEventListener('click',(e)=>{
      e.preventDefault(); e.stopPropagation();
      trackIg(btn.dataset.igPlacement||'gallery_tile');
      window.open(IG_URL,'_blank','noopener,noreferrer');
    },true);
  });

  const lb=document.querySelector('.lightbox'),lbImg=lb?.querySelector('img'),close=lb?.querySelector('button');
  document.querySelectorAll('[data-lightbox]').forEach(b=>b.addEventListener('click',()=>{
    if(b.dataset.instagramTile==='true') return;
    lbImg.src=b.dataset.lightbox;lbImg.alt=b.querySelector('img').alt;lb.classList.add('open');document.body.classList.add('modal-open')
  }));
  const shut=()=>{lb?.classList.remove('open');if(lbImg)lbImg.src='';if(!document.querySelector('.video-modal.open')) document.body.classList.remove('modal-open')};
  close?.addEventListener('click',shut);lb?.addEventListener('click',e=>{if(e.target===lb)shut()});

  const videoModal=document.querySelector('.video-modal'),videoInner=videoModal?.querySelector('.video-modal-inner'),videoFrame=videoModal?.querySelector('iframe'),videoClose=videoModal?.querySelector('.video-close');
  let lastVideoTrigger=null;
  const openFullscreen=()=>{const req=videoInner&&(videoInner.requestFullscreen||videoInner.webkitRequestFullscreen||videoInner.msRequestFullscreen);if(req){try{req.call(videoInner)}catch(e){}}};
  const closeFullscreen=()=>{const exit=document.exitFullscreen||document.webkitExitFullscreen||document.msExitFullscreen;if((document.fullscreenElement||document.webkitFullscreenElement||document.msFullscreenElement)&&exit){try{exit.call(document)}catch(e){}}};
  const shutVideo=()=>{videoModal?.classList.remove('open');videoInner?.classList.remove('portrait');closeFullscreen();if(videoFrame){videoFrame.src='about:blank';videoFrame.title='Serdar Armin Sargut showreel video player';}if(!document.querySelector('.lightbox.open')) document.body.classList.remove('modal-open');const trigger=lastVideoTrigger;lastVideoTrigger=null;trigger?.focus()};
  videoClose?.addEventListener('click',shutVideo);videoModal?.addEventListener('click',e=>{if(e.target===videoModal)shutVideo()});document.addEventListener('keydown',e=>{if(e.key==='Escape'){shut();shutVideo()}});
  document.querySelectorAll('[data-video]').forEach(btn=>btn.addEventListener('click',()=>{lastVideoTrigger=btn;videoInner?.classList.toggle('portrait',btn.dataset.aspect==='portrait');sendGA('showreel_play',{placement:'showreel_grid',video_id:btn.dataset.video,video_title:btn.dataset.title||'Showreel video',language:lang,page_path:location.pathname});if(videoFrame){videoFrame.src='https://player.vimeo.com/video/'+btn.dataset.video+'?autoplay=1&title=0&byline=0&portrait=0';videoFrame.title=btn.dataset.title||'Showreel video';}videoModal?.classList.add('open');document.body.classList.add('modal-open');setTimeout(openFullscreen,80)}));
})();
