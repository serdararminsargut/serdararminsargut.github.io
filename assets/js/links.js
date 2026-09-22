(() => {
  "use strict";

  const translations = {
    tr: {
      location: "İstanbul, Türkiye",
      role: "Çocuk Oyuncu • Reklam Modeli",
      intro: "Showreel, profesyonel portföy ve casting bağlantıları.",
      showreel_title: "Showreel'i İzle",
      showreel_sub: "Oyunculuk ve kamera önü seçkisi",
      portfolio_title: "Resmî Portföy",
      portfolio_sub: "Fotoğraflar, oyunculuk ve profesyonel profil",
      modeling_title: "Reklam & Modellik Portföyü",
      modeling_sub: "Katalog, ürün, moda ve reklam çekimleri",
      acting_title: "Oyunculuk Portföyü",
      acting_sub: "Dizi, sinema ve reklam çalışmaları",
      casting_title: "Casting Card",
      casting_sub: "Casting değerlendirmesi için profil kartı",
      instagram_title: "Instagram'da Takip Et",
      instagram_sub: "Yeni çekimler, Reels ve portföy güncellemeleri",
      contact_title: "Casting & Marka İletişimi",
      contact_sub: "Profesyonel iş birliği ve casting talepleri",
      footer: "Serdar Armin Sargut Resmî Portföyü • İstanbul, Türkiye",
      privacy: "İletişim ebeveyn / veli yönetimindedir."
    },
    en: {
      location: "Istanbul, Türkiye",
      role: "Child Actor • Commercial Model",
      intro: "Showreel, professional portfolio and casting links.",
      showreel_title: "Watch Showreel",
      showreel_sub: "Selected acting and on-camera work",
      portfolio_title: "Official Portfolio",
      portfolio_sub: "Photos, acting work and professional profile",
      modeling_title: "Commercial & Modeling Portfolio",
      modeling_sub: "Catalog, product, fashion and commercial work",
      acting_title: "Acting Portfolio",
      acting_sub: "Television, film and commercial work",
      casting_title: "Casting Card",
      casting_sub: "Profile card for casting review",
      instagram_title: "Follow Serdar on Instagram",
      instagram_sub: "New photos, reels and portfolio updates",
      contact_title: "Casting & Brand Inquiries",
      contact_sub: "Professional collaboration and casting inquiries",
      footer: "Official Portfolio of Serdar Armin Sargut • Istanbul, Türkiye",
      privacy: "Contact is parent / guardian managed."
    }
  };

  const params = new URLSearchParams(window.location.search);

  function referrerSource() {
    if (!document.referrer) return "direct";
    try {
      const host = new URL(document.referrer).hostname.toLowerCase();
      if (host.includes("google.")) return "google";
      if (host.includes("instagram.")) return "instagram";
      if (host.includes("pinterest.")) return "pinterest";
      if (host.includes("tiktok.")) return "tiktok";
      if (host.includes("youtube.") || host.includes("youtu.be")) return "youtube";
      return host.replace(/^www\./, "");
    } catch (_) {
      return "direct";
    }
  }

  const trafficSource = (params.get("utm_source") || referrerSource()).toLowerCase();
  const campaign = params.get("utm_campaign") || "";
  const content = params.get("utm_content") || "";

  const list = document.getElementById("cta-list");

  function moveToTop(keys) {
    const nodes = keys
      .map((key) => list.querySelector('[data-key="' + key + '"]'))
      .filter(Boolean);
    for (let i = nodes.length - 1; i >= 0; i -= 1) {
      list.prepend(nodes[i]);
    }
  }

  if (trafficSource === "instagram") {
    moveToTop(["showreel", "portfolio"]);
  } else if (["pinterest", "tiktok", "youtube"].includes(trafficSource)) {
    moveToTop(["instagram", "showreel", "portfolio"]);
  } else if (trafficSource === "google") {
    moveToTop(["portfolio", "showreel"]);
  } else if (trafficSource.includes("casting") || trafficSource.includes("agency")) {
    moveToTop(["casting", "showreel", "portfolio"]);
  }

  function setLanguage(lang) {
    const selected = translations[lang] ? lang : "tr";
    document.documentElement.lang = selected;
    document.querySelectorAll("[data-i18n]").forEach((node) => {
      const key = node.getAttribute("data-i18n");
      if (translations[selected][key]) node.textContent = translations[selected][key];
    });
    document.querySelectorAll("[data-lang]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.lang === selected));
    });
    try {
      localStorage.setItem("sas_links_lang", selected);
    } catch (_) {}
  }

  let initialLang = params.get("lang");
  if (!translations[initialLang]) {
    try {
      initialLang = localStorage.getItem("sas_links_lang");
    } catch (_) {}
  }
  setLanguage(translations[initialLang] ? initialLang : "tr");

  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => setLanguage(button.dataset.lang));
  });

  function currentPosition(link) {
    return Array.from(list.querySelectorAll("[data-event]")).indexOf(link) + 1;
  }

  document.querySelectorAll("[data-event]").forEach((link) => {
    link.addEventListener("click", () => {
      const payload = {
        talent_name: "serdar_armin_sargut",
        button_name: link.dataset.key || link.dataset.event,
        button_position: currentPosition(link),
        traffic_source: trafficSource,
        utm_source: params.get("utm_source") || "",
        utm_campaign: campaign,
        utm_content: content,
        language: document.documentElement.lang,
        outbound_url: link.href
      };
      if (typeof window.gtag === "function") {
        window.gtag("event", link.dataset.event, payload);
      } else {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({event: link.dataset.event, ...payload});
      }
    });
  });

  const note = document.getElementById("source-note");
  if (note && trafficSource !== "direct") {
    note.textContent = "source: " + trafficSource;
  }
})();
