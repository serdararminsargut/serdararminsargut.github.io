/* Serdar only: GA4 pageview for previously uninstrumented public pages.
 * Never attach alongside an existing GA4 initializer. No Yandex, replay, or other trackers.
 * Production requires separate authorization and live verification. */
(function (w, d) {
  'use strict';
  if (w.__sasGa4PageviewOnce) return;
  w.__sasGa4PageviewOnce = true;

  var measurementId = 'G-H894LKL93J';
  w.dataLayer = w.dataLayer || [];
  w.gtag = w.gtag || function () { w.dataLayer.push(arguments); };
  w.gtag('js', new Date());
  w.gtag('config', measurementId);

  if (!d.querySelector('script[src*="googletagmanager.com/gtag/js"]')) {
    var tag = d.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
    tag.setAttribute('data-sas-ga4-untracked', '1');
    d.head.appendChild(tag);
  }
})(window, document);
