"use strict";
(async function () {
  const routes = ["/", "/en/", "/links/", "/links/en/"];
  const out = document.getElementById("qa-result");
  const lines = [];
  for (const route of routes) {
    try {
      const r = await fetch(route, {method:"GET",credentials:"same-origin",cache:"no-store",redirect:"follow"});
      const h = r.headers.get("X-Robots-Tag");
      const ct = r.headers.get("Content-Type") || "";
      const finalUrl = new URL(r.url);
      const sameOrigin = finalUrl.origin === location.origin;
      const good = r.status === 200 && sameOrigin && ct.toLowerCase().includes("text/html") && /(?:^|[, ]+)noindex(?:[, ]+|$)/i.test(h || "");
      lines.push(route + " | HTTP=" + r.status + " | sameOrigin=" + sameOrigin + " | X-Robots-Tag=" + (h || "MISSING") + " | " + (good ? "PASS" : "NO-GO/UNVERIFIED"));
    } catch (e) {
      lines.push(route + " | UNVERIFIED fetch failed: " + (e instanceof Error ? e.name : "error"));
    }
  }
  out.textContent = lines.join("\n");
})();
