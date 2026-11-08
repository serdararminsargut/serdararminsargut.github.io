'use strict';
const { chromium } = require('playwright');
const project=process.env.AUDIT_PROJECT;
const cfg=project==='serdar'
 ? {origin:'https://serdararminsargut.com', paths:['/','/links/','/casting-card/tr','/casting-card/ar','/rehber/post/']}
 : project==='duru'
 ? {origin:'https://durumuallasargut.com', paths:['/','/links/','/comp-card/tr/','/comp-card/ar/']}
 : null;
if(!cfg)throw Error('Project not selected');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 let fails=0;
 for(const width of [360,390,430,1280]){
  const ctx=await browser.newContext({viewport:{width,height:844},deviceScaleFactor:1});
  await ctx.route('**/*',route=>{const req=route.request();let url;try{url=new URL(req.url())}catch{return route.abort()}return url.origin===cfg.origin&&req.method()==='GET'?route.continue():route.abort()});
  for(const path of cfg.paths){
   const page=await ctx.newPage();
   try{
    const res=await page.goto(cfg.origin+path,{waitUntil:'domcontentloaded',timeout:30000});
    if(!res||res.status()!==200)throw Error('HTTP '+(res?.status()||'no response'));
    await page.waitForLoadState('load',{timeout:15000});
    const result=await page.evaluate(async()=>{await document.fonts.ready;const d=document.documentElement;const visible=[...document.images].filter(i=>{const r=i.getBoundingClientRect();return r.width>0&&r.height>0&&r.top<innerHeight&&r.bottom>0&&new URL(i.currentSrc||i.src,location.href).origin===location.origin});return {width:d.clientWidth,scroll:d.scrollWidth,h1:document.querySelectorAll('h1').length,broken:visible.filter(i=>i.complete&&i.naturalWidth===0).length};});
    if(result.scroll>result.width+2)throw Error('horizontal overflow');
    if(result.h1!==1)throw Error('expected one H1; found '+result.h1);
    if(result.broken)throw Error('visible image failed to load');
    console.log('BROWSER_PASS',project,path,width);
   }catch(e){fails++;console.log('BROWSER_FAIL',project,path,width,String(e.message).slice(0,150));}
   finally{await page.close()}
  }
  await ctx.close();
 }
 await browser.close();
 if(fails){console.log('BROWSER_FAIL_TOTAL',fails);process.exitCode=1}else console.log('BROWSER_PASS_ALL');
})().catch(e=>{console.error('BROWSER_UNVERIFIED',e.message);process.exitCode=2});
