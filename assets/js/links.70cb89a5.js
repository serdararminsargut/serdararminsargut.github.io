(() => {
  "use strict";

  const translations = {
    tr: {
      page_title: "Serdar Armin Sargut | Çocuk Oyuncu & Reklam Modeli",
      page_description: "Serdar Armin Sargut’un oyunculuk, reklam modelliği, showreel, profesyonel portföy ve casting bağlantılarına ulaşın.",
      skip_link: "Portföy bağlantılarına geç",
      preview_banner: "TEST PREVIEW • PRODUCTION DEĞİL",
      og_locale: "tr_TR",
      lang_switch_aria: "Dil seçimi",
      profile_alt: "Serdar Armin Sargut — çocuk oyuncu ve reklam modeli",
      cta_list_aria: "Portföy bağlantıları",
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
      privacy: "İletişim ebeveyn / veli yönetimindedir.",
      showreel_aria: "Serdar Armin Sargut showreelini izle",
      portfolio_aria: "Serdar Armin Sargut resmî portföyünü aç",
      modeling_aria: "Serdar Armin Sargut reklam ve modellik portföyünü aç",
      acting_aria: "Serdar Armin Sargut oyunculuk portföyünü aç",
      casting_aria: "Serdar Armin Sargut casting kartını aç",
      instagram_aria: "Serdar Armin Sargut Instagram profilini aç ve takip et",
      contact_aria: "Casting ve marka iletişimi bölümünü aç"
    },
    en: {
      page_title: "Serdar Armin Sargut | Child Actor & Commercial Model",
      page_description: "Access Serdar Armin Sargut’s acting, commercial modeling, showreel, professional portfolio and casting links.",
      skip_link: "Skip to portfolio links",
      preview_banner: "TEST PREVIEW • NOT PRODUCTION",
      og_locale: "en_US",
      lang_switch_aria: "Language selection",
      profile_alt: "Serdar Armin Sargut — child actor and commercial model",
      cta_list_aria: "Portfolio links",
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
      privacy: "Contact is parent / guardian managed.",
      showreel_aria: "Watch Serdar Armin Sargut showreel",
      portfolio_aria: "Open Serdar Armin Sargut official portfolio",
      modeling_aria: "Open Serdar Armin Sargut commercial and modeling portfolio",
      acting_aria: "Open Serdar Armin Sargut acting portfolio",
      casting_aria: "Open Serdar Armin Sargut casting card",
      instagram_aria: "Open and follow Serdar Armin Sargut on Instagram",
      contact_aria: "Open casting and brand inquiries section"
    },
    ar: {
      page_title: "Serdar Armin Sargut | ممثل طفل وموديل إعلاني",
      page_description: "روابط الشوريل والتمثيل والموديل الإعلاني والملف المهني والكاستينغ لـ Serdar Armin Sargut.",
      skip_link: "انتقل إلى روابط الملف",
      preview_banner: "نسخة اختبار • ليست للإنتاج",
      og_locale: "ar_AR",
      lang_switch_aria: "اختيار اللغة",
      profile_alt: "Serdar Armin Sargut — ممثل طفل وموديل إعلاني",
      cta_list_aria: "روابط الملف",
      location: "إسطنبول، تركيا",
      role: "ممثل طفل • موديل إعلاني",
      intro: "الشوريل، الملف المهني وروابط الكاستينغ.",
      showreel_title: "شاهد الشوريل",
      showreel_sub: "مختارات من التمثيل والأداء أمام الكاميرا",
      portfolio_title: "الملف الرسمي",
      portfolio_sub: "صور، أعمال تمثيل وملف مهني",
      modeling_title: "ملف الإعلانات والموديل",
      modeling_sub: "كتالوج، منتجات، أزياء وإعلانات",
      acting_title: "ملف التمثيل",
      acting_sub: "تلفزيون، سينما وأعمال إعلانية",
      casting_title: "بطاقة الكاستينغ",
      casting_sub: "بطاقة الملف للتقييم في الكاستينغ",
      instagram_title: "تابع Serdar على Instagram",
      instagram_sub: "صور جديدة وReels وتحديثات الملف",
      contact_title: "استفسارات الكاستينغ والعلامات",
      contact_sub: "للتعاون المهني وطلبات الكاستينغ",
      footer: "الملف الرسمي لـ Serdar Armin Sargut • إسطنبول، تركيا",
      privacy: "التواصل بإدارة الوالدين / الوصي.",
      showreel_aria: "شاهد شوريل Serdar Armin Sargut",
      portfolio_aria: "افتح الملف الرسمي لـ Serdar Armin Sargut",
      modeling_aria: "افتح ملف الإعلانات والموديل لـ Serdar Armin Sargut",
      acting_aria: "افتح ملف التمثيل لـ Serdar Armin Sargut",
      casting_aria: "افتح بطاقة الكاستينغ لـ Serdar Armin Sargut",
      instagram_aria: "افتح حساب Serdar Armin Sargut على Instagram وتابعه",
      contact_aria: "افتح قسم استفسارات الكاستينغ والعلامات"
    },
    ru: {
      page_title: "Serdar Armin Sargut | Детский актёр и рекламная модель",
      page_description: "Шоурил, актёрское и модельное портфолио, профессиональные материалы и ссылки для кастинга Serdar Armin Sargut.",
      skip_link: "Перейти к ссылкам портфолио",
      preview_banner: "ТЕСТОВАЯ ВЕРСИЯ • НЕ PRODUCTION",
      og_locale: "ru_RU",
      lang_switch_aria: "Выбор языка",
      profile_alt: "Serdar Armin Sargut — детский актёр и рекламная модель",
      cta_list_aria: "Ссылки портфолио",
      location: "Стамбул, Турция",
      role: "Детский актёр • Рекламная модель",
      intro: "Шоурил, профессиональное портфолио и ссылки для кастинга.",
      showreel_title: "Смотреть шоурил",
      showreel_sub: "Избранные актёрские и экранные работы",
      portfolio_title: "Официальное портфолио",
      portfolio_sub: "Фотографии, актёрские работы и профессиональный профиль",
      modeling_title: "Реклама и модельное портфолио",
      modeling_sub: "Каталог, товары, мода и рекламные съёмки",
      acting_title: "Актёрское портфолио",
      acting_sub: "Телевидение, кино и рекламные работы",
      casting_title: "Кастинг-карта",
      casting_sub: "Профильная карточка для кастинга",
      instagram_title: "Подписаться на Serdar в Instagram",
      instagram_sub: "Новые фото, Reels и обновления портфолио",
      contact_title: "Кастинг и запросы брендов",
      contact_sub: "Профессиональное сотрудничество и кастинг-запросы",
      footer: "Официальное портфолио Serdar Armin Sargut • Стамбул, Турция",
      privacy: "Контакты управляются родителем / опекуном.",
      showreel_aria: "Смотреть шоурил Serdar Armin Sargut",
      portfolio_aria: "Открыть официальное портфолио Serdar Armin Sargut",
      modeling_aria: "Открыть рекламное и модельное портфолио Serdar Armin Sargut",
      acting_aria: "Открыть актёрское портфолио Serdar Armin Sargut",
      casting_aria: "Открыть кастинг-карту Serdar Armin Sargut",
      instagram_aria: "Открыть Instagram Serdar Armin Sargut и подписаться",
      contact_aria: "Открыть раздел кастинга и запросов брендов"
    }
  };

  const routes = {
    tr: {base: "/", casting: "/casting-card/tr.html"},
    en: {base: "/en/", casting: "/casting-card/en.html"},
    ar: {base: "/ar/", casting: "/casting-card/ar.html"},
    ru: {base: "/ru/", casting: "/casting-card/ru.html"}
  };

  const languagePaths = {
    tr: "/links/",
    en: "/links/en/",
    ar: "/links/ar/",
    ru: "/links/ru"
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
    for (let i = nodes.length - 1; i >= 0; i -= 1) list.prepend(nodes[i]);
  }

  if (trafficSource === "direct" || (!["instagram","pinterest","tiktok","youtube","google"].includes(trafficSource) && !trafficSource.includes("casting") && !trafficSource.includes("agency"))) {
    moveToTop(["portfolio", "showreel", "instagram"]);
  } else if (trafficSource === "instagram") {
    moveToTop(["showreel", "portfolio"]);
  } else if (["pinterest", "tiktok", "youtube"].includes(trafficSource)) {
    moveToTop(["instagram", "showreel", "portfolio"]);
  } else if (trafficSource === "google") {
    moveToTop(["portfolio", "showreel"]);
  } else if (trafficSource.includes("casting") || trafficSource.includes("agency")) {
    moveToTop(["casting", "showreel", "portfolio"]);
  }

  function updateRoutes(lang) {
    const route = routes[lang];
    const targets = {
      portfolio: route.base,
      showreel: route.base + "#showreel",
      modeling: route.base + "#model",
      acting: route.base + "#oyunculuk",
      contact: route.base + "#iletisim",
      casting: route.casting
    };
    Object.entries(targets).forEach(([key, href]) => {
      const link = list.querySelector('[data-key="' + key + '"]');
      if (link) link.setAttribute("href", href);
    });
  }

  function setLanguage(lang) {
    const selected = translations[lang] ? lang : "tr";
    const t = translations[selected];

    document.documentElement.lang = selected;
    document.documentElement.dir = selected === "ar" ? "rtl" : "ltr";
    document.title = t.page_title;

    const description = document.querySelector('meta[name="description"]');
    if (description) description.setAttribute("content", t.page_description);

    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle) ogTitle.setAttribute("content", t.page_title);

    const ogDescription = document.querySelector('meta[property="og:description"]');
    if (ogDescription) ogDescription.setAttribute("content", t.page_description);

    const ogLocale = document.querySelector('meta[property="og:locale"]');
    if (ogLocale) ogLocale.setAttribute("content", t.og_locale);

    const ogImageAlt = document.querySelector('meta[property="og:image:alt"]');
    if (ogImageAlt) ogImageAlt.setAttribute("content", t.profile_alt);

    const twitterTitle = document.querySelector('meta[name="twitter:title"]');
    if (twitterTitle) twitterTitle.setAttribute("content", t.page_title);

    const twitterDescription = document.querySelector('meta[name="twitter:description"]');
    if (twitterDescription) twitterDescription.setAttribute("content", t.page_description);

    const twitterImageAlt = document.querySelector('meta[name="twitter:image:alt"]');
    if (twitterImageAlt) twitterImageAlt.setAttribute("content", t.profile_alt);

    const languageSwitch = document.querySelector(".lang-switch");
    if (languageSwitch) languageSwitch.setAttribute("aria-label", t.lang_switch_aria);

    const profilePhoto = document.querySelector(".profile-photo");
    if (profilePhoto) profilePhoto.setAttribute("alt", t.profile_alt);

    if (list) list.setAttribute("aria-label", t.cta_list_aria);

    document.querySelectorAll("[data-i18n]").forEach((node) => {
      const key = node.getAttribute("data-i18n");
      if (t[key]) node.textContent = t[key];
    });

    document.querySelectorAll("[data-lang]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.lang === selected));
    });

    document.querySelectorAll("[data-aria]").forEach((link) => {
      const key = link.getAttribute("data-aria");
      if (t[key]) link.setAttribute("aria-label", t[key]);
    });

    updateRoutes(selected);

    try {
      localStorage.setItem("sas_links_lang", selected);
    } catch (_) {}

    // The selected language is represented by the URL path.
  }

  function languageFromPath() {
    const path = window.location.pathname.replace(/\/+$/, "");
    if (path === "/links/en") return "en";
    if (path === "/links/ar") return "ar";
    if (path === "/links/ru") return "ru";
    return "tr";
  }

  const currentLinkPath = window.location.pathname.replace(/\/+$/, "");
  const legacyLang = params.get("lang");
  if (currentLinkPath === "/links" && legacyLang && translations[legacyLang]) {
    const legacyUrl = new URL(languagePaths[legacyLang], window.location.origin);
    for (const [key, value] of params.entries()) {
      if (key !== "lang") legacyUrl.searchParams.append(key, value);
    }
    legacyUrl.hash = window.location.hash;
    const nextLocation = legacyUrl.pathname + legacyUrl.search + legacyUrl.hash;
    const currentLocation = window.location.pathname + window.location.search + window.location.hash;
    if (nextLocation !== currentLocation) {
      window.location.replace(nextLocation);
      return;
    }
  }

  const initialLang = languageFromPath();
  setLanguage(initialLang);

  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => {
      const fromLanguage = document.documentElement.lang || "tr";
      const toLanguage = button.dataset.lang;
      if (fromLanguage === toLanguage) return;

      const payload = {
        talent_name: "serdar_armin_sargut",
        from_language: fromLanguage,
        to_language: toLanguage,
        traffic_source: trafficSource,
        utm_source: params.get("utm_source") || "",
        utm_campaign: campaign,
        utm_content: content
      };

      if (typeof window.gtag === "function") {
        window.gtag("event", "language_change", payload);
      } else {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({event: "language_change", ...payload});
      }

      const nextUrl = new URL(languagePaths[toLanguage], window.location.origin);
      for (const [key, value] of params.entries()) {
        if (key !== "lang") nextUrl.searchParams.append(key, value);
      }
      window.location.assign(nextUrl.pathname + nextUrl.search);
    });
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
})();
