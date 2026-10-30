/* Browser QA for TEST branch only. Never deploy.
 * Uses runner pre-installed Chrome and local HTTP after Hugo build.
 */
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

(async () => {
  const base = process.env.QA_ORIGIN || 'http://127.0.0.1:8765';
  const chrome = process.env.CHROME_BIN;
  if (!chrome) throw Error('CHROME_BIN missing; do not silently skip browser QA');
  const slugs = [
    '/',
    '/post/cocuk-giyim-e-ticaret-cekimlerinde-portfoy-secimi/',
    '/post/spor-giyim-ayakkabi-katalog-fotograflari/',
    '/post/cocuk-oyuncu-casting-sunum-dosyasi/'
  ];
  const widths = [360,390,430,1280];
  fs.mkdirSync('qa_artifacts', {recursive:true});
  let browser;
  const results = [];
  try {
    browser = await chromium.launch({executablePath:chrome, headless:true, args:['--no-sandbox','--disable-dev-shm-usage']});
    for (const rel of slugs) for (const width of widths) {
      const page = await browser.newPage({viewport:{width,height:900}, deviceScaleFactor:1});
      const pageErrors=[];
      const localFailures=[];
      page.on('pageerror', e=> pageErrors.push(String(e)));
      page.on('response', r => {
        if(r.url().startsWith(base) && r.status()>=400) localFailures.push(r.status()+' '+r.url());
      });
      let issue=null;
      try {
        const response=await page.goto(base+rel,{waitUntil:'load',timeout:25000});
        await page.waitForTimeout(250);
        const m=await page.evaluate(() => ({
          h1:document.querySelectorAll('h1').length,
          docWidth:document.documentElement.scrollWidth,
          viewport:window.innerWidth,
          robots:document.querySelector('meta[name="robots"]')?.getAttribute('content')||'',
          fake:document.documentElement.outerHTML.includes('example.invalid'),
          navLinks:[...document.querySelectorAll('nav a')].map(a=>a.getAttribute('href'))
        }));
        if(!response || response.status()!==200) throw Error('not 200');
        if(m.h1!==1) throw Error('H1='+m.h1);
        if(m.docWidth>width+1) throw Error('horizontal overflow '+m.docWidth+' > '+width);
        if(m.robots!=='noindex,nofollow,noarchive') throw Error('bad robots '+m.robots);
        if(m.fake) throw Error('placeholder domain remains');
        if(!m.navLinks.includes('/post/')) throw Error('missing content navigation');
        if(!m.navLinks.some(x=>x&&x.startsWith('https://serdararminsargut.com/'))) throw Error('missing official portfolio navigation');
        if(width<500){
          const toggle=page.locator('label[for="nav-toggle"]');
          if(await toggle.count()!==1) throw Error('mobile menu toggle missing');
          if(await toggle.evaluate(el=>{const r=el.getBoundingClientRect();return r.width<44||r.height<44;})) throw Error('mobile touch target smaller than 44 px');
          await toggle.click({timeout:5000});
          if(!(await page.locator('#nav-toggle').isChecked())) throw Error('mobile menu did not open');
          await toggle.click({timeout:5000});
          if(await page.locator('#nav-toggle').isChecked()) throw Error('mobile menu did not close');
        }
        if(pageErrors.length) throw Error('JS page errors: '+pageErrors.join('; ').slice(0,600));
        if(localFailures.length) throw Error('HTTP resource errors: '+localFailures.join('; ').slice(0,600));
        if(width===390 && rel==='/') await page.screenshot({path:'qa_artifacts/serdar-http-browser-390.png',fullPage:true});
      }catch(e){issue=String(e);}
      results.push({path:rel,width,passed:!issue,issue,pageErrors,localFailures});
      await page.close();
    }
  }finally{if(browser)await browser.close();}
  fs.writeFileSync('qa_artifacts/browser_qa.json',JSON.stringify(results,null,2));
  const errors=results.filter(x=>!x.passed);
  console.log('HTTP browser checks:',results.length-errors.length+'/'+results.length);
  errors.forEach(e=>console.error('FAIL',e.path,e.width,e.issue));
  if(errors.length) process.exit(1);
})().catch(e=>{console.error(e);process.exit(1);});
