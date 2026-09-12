/* Analytics bootstrap: defer third-party network work until after initial render. */
window.dataLayer = window.dataLayer || [];
function gtag(){window.dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-H894LKL93J');

(function () {
  var loaded = false;
  function loadAnalytics() {
    if (loaded) return;
    loaded = true;

    /* Google Analytics */
    if (!document.querySelector('script[data-sas-ga]')) {
      var ga = document.createElement('script');
      ga.async = true;
      ga.src = 'https://www.googletagmanager.com/gtag/js?id=G-H894LKL93J';
      ga.setAttribute('data-sas-ga', '1');
      document.head.appendChild(ga);
    }

    /* Yandex.Metrika */
    window.ym = window.ym || function(){(window.ym.a = window.ym.a || []).push(arguments);};
    window.ym.l = +new Date();
    if (!document.querySelector('script[data-sas-ym]')) {
      var ymScript = document.createElement('script');
      ymScript.async = true;
      ymScript.src = 'https://mc.yandex.ru/metrika/tag.js?id=112473942';
      ymScript.setAttribute('data-sas-ym', '1');
      document.head.appendChild(ymScript);
    }
    window.ym(112473942, 'init', {
      ssr: true,
      webvisor: true,
      clickmap: true,
      ecommerce: 'dataLayer',
      referrer: document.referrer,
      url: location.href,
      accurateTrackBounce: true,
      trackLinks: true
    });
  }

  function scheduleAnalytics() {
    if ('requestIdleCallback' in window) {
      window.requestIdleCallback(loadAnalytics, {timeout: 2500});
    } else {
      window.setTimeout(loadAnalytics, 1500);
    }
  }

  if (document.readyState === 'complete') {
    scheduleAnalytics();
  } else {
    window.addEventListener('load', scheduleAnalytics, {once: true});
  }
})();
