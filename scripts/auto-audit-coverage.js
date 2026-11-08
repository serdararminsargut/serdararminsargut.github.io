'use strict';
// Serdar-only bounded public GET checks. Reports hashes and statuses, not page content.
const https=require('node:https'),crypto=require('node:crypto'),fs=require('node:fs');
const ORIGIN='https://serdararminsargut.com';
const CODES=['tr','en','ru','ar','az','de','fr','es','kk','uz','ky','tk','it','pt-br','uk','pl','bg','el','sr-latn','sq','fa','ur','hi','zh-hans','ja','ko'];
const GUIDES=['/rehber/','/rehber/post/','/rehber/post/cocuk-giyim-e-ticaret-cekimlerinde-portfoy-secimi/','/rehber/post/cocuk-oyuncu-casting-sunum-dosyasi/','/rehber/post/spor-giyim-ayakkabi-katalog-fotograflari/'];
const LINKS=['/links/','/links/en/','/links/ar/','/links/ru/'];
const MAX_REQUESTS=64, MAX_BYTES=6*1024*1024;
function safeUrl(route){const u=new URL(route,ORIGIN);if(u.protocol!=='https:'||u.origin!==ORIGIN||u.username||u.password||u.port||/%(?:2f|5c|00)/i.test(u.pathname)||u.pathname.includes('\\'))throw Error('BLOCKED_ORIGIN');u.search='';u.hash='';return u;}
function fetchPublic(route){const u=safeUrl(route);return new Promise((resolve,reject)=>{const q=https.get(u,{timeout:7000,headers:{'User-Agent':'Mozilla/5.0 SerdarPortfolioAudit/0.4','Accept':'*/*'}},r=>{let n=0,parts=[];r.on('data',b=>{n+=b.length;if(n>MAX_BYTES){q.destroy(Error('RESPONSE_LIMIT'));return;}parts.push(b)});r.on('end',()=>resolve({status:r.statusCode,body:Buffer.concat(parts)}));r.on('error',reject)});q.on('error',reject);q.on('timeout',()=>q.destroy(Error('TIMEOUT')));});}
async function audit({fetcher=fetchPublic,now=()=>new Date().toISOString()}={}){
 const rows=[],timestamp=now();let calls=0;
 async function check(route,kind){safeUrl(route);if(++calls>MAX_REQUESTS)throw Error('REQUEST_LIMIT');try{const r=await fetcher(route);const body=Buffer.isBuffer(r.body)?r.body:Buffer.from(r.body||'');if(body.length>MAX_BYTES)throw Error('RESPONSE_LIMIT');const hash=crypto.createHash('sha256').update(body).digest('hex');const pass=kind==='404'?r.status===404:kind==='pdf'?r.status===200&&body.subarray(0,5).toString()==='%PDF-':r.status===200;rows.push({route,kind,status:pass?'PASS':'FAIL',httpStatus:r.status,sha256:hash});}catch(e){rows.push({route,kind,status:'DOĞRULANMADI',error:String(e.message).slice(0,120)});}}
 for(const code of CODES)await check('/casting-card/'+code,'html');
 for(const code of CODES)await check('/downloads/Serdar-Armin-Sargut-Comp-Card-'+code.toUpperCase()+'.pdf','pdf');
 for(const route of [...LINKS,...GUIDES])await check(route,'html');
 await check('/audit-nonexistent-404-check-20261108','404');
 return {project:'serdar',mode:'public-readonly-GET',timestamp,requestBudget:MAX_REQUESTS,requestsMade:calls,checks:rows,acceptance:rows.some(x=>x.status==='FAIL')?'FAIL':rows.some(x=>x.status!=='PASS')?'DOĞRULANMADI':'PASS',limitations:['HTTP only; no rendered mobile, PDF content or QR, translation, analytics or indexing verification','Fixed routes require maintenance after site changes; no scheduler or automatic update']};
}
if(require.main===module)audit().then(r=>{const f='serdar-current-coverage-'+Date.now()+'.json';fs.writeFileSync(f,JSON.stringify(r,null,2)+'\n',{flag:'wx',mode:0o600});console.log(JSON.stringify({file:f,acceptance:r.acceptance,requests:r.requestsMade}));if(r.acceptance!=='PASS')process.exitCode=r.acceptance==='FAIL'?1:2}).catch(e=>{console.error('DOĞRULANMADI: '+e.message);process.exitCode=2});
module.exports={audit,safeUrl,CODES,GUIDES,LINKS,MAX_REQUESTS,MAX_BYTES};
