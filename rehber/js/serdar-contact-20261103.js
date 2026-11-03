/* Serdar parent-managed contact. No tracking, data collection or network calls. */
(function () {
  "use strict";
  const form = document.getElementById("inquiry");
  if (!form) return;
  const tr = document.documentElement.lang === "tr";
  const subject = tr ? "Serdar Armin Sargut — Casting / İşbirliği" : "Serdar Armin Sargut — Casting / Collaboration";
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const value = name => (form.elements.namedItem(name).value || "").trim();
    const lines = [
      (tr ? "Yetkili: " : "Contact: ") + value("name"),
      "Email: " + value("reply"),
      (tr ? "Şirket / Proje: " : "Company / Project: ") + value("org"),
      "",
      value("details"),
      "",
      tr ? "Gönderim veli yönetimindeki profesyonel iletişim adresine yönlendirilmiştir." : "Addressed to the parent-managed professional contact."
    ];
    window.location.href = "mailto:info@serdararminsargut.com?subject=" +
       encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
  });
})();
