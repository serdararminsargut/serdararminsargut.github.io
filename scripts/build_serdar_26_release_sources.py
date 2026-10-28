#!/usr/bin/env python3
"""Build a production-shaped, but unpublishable, Serdar 26-locale source package.

The package is intentionally written outside the live ``casting-card`` tree.
It reuses the approved Comp Card stylesheet and protected sections, so the
eventual release can be reviewed without changing main or deploying Pages.
"""
from __future__ import annotations

import html
from pathlib import Path

from build_serdar_26_candidate import LANGUAGE_NOTE, L, LANG_TAG, LOOKS, ORIGIN, PHOTO, h, split

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "serdar-26-release-sources" / "casting-card"
TEMPLATE = ROOT / "casting-card" / "tr.html"

NAV = {
    "tr": ("Portföy", "Showreel", "Blog", "İletişim", "PDF Kaydet"),
    "en": ("Portfolio", "Showreel", "Blog", "Contact", "Save PDF"),
    "ru": ("Портфолио", "Шоурил", "Блог", "Контакты", "Сохранить PDF"),
    "ar": ("الملف", "عرض الأعمال", "المدونة", "التواصل", "حفظ PDF"),
    "az": ("Rəsmi portfel", "Şouril", "Bloq", "Əlaqə", "PDF saxla"),
    "de": ("Portfolio", "Showreel", "Blog", "Kontakt", "PDF speichern"),
    "fr": ("Portfolio", "Bande démo", "Blog", "Contact", "Enregistrer le PDF"),
    "es": ("Portafolio", "Videodemostración", "Blog", "Contacto", "Guardar PDF"),
    "kk": ("Портфолио", "Шоурил", "Блог", "Байланыс", "PDF сақтау"),
    "uz": ("Rasmiy portfel", "Shouril", "Blog", "Aloqa", "PDF saqlash"),
    "ky": ("Портфолио", "Шоурил", "Блог", "Байланыш", "PDF сактоо"),
    "tk": ("Resmi portfel", "Şouril", "Blog", "Habarlaşmak", "PDF ýatda sakla"),
    "it": ("Portfolio", "Showreel", "Blog", "Contatti", "Salva PDF"),
    "pt-br": ("Portfólio", "Showreel", "Blog", "Contato", "Salvar PDF"),
    "uk": ("Портфоліо", "Шоуріл", "Блог", "Контакти", "Зберегти PDF"),
    "pl": ("Portfolio", "Showreel", "Blog", "Kontakt", "Zapisz PDF"),
    "bg": ("Портфолио", "Шоурил", "Блог", "Контакт", "Запази PDF"),
    "el": ("Χαρτοφυλάκιο", "Showreel", "Ιστολόγιο", "Επικοινωνία", "Αποθήκευση PDF"),
    "sr-latn": ("Portfolio", "Showreel", "Blog", "Kontakt", "Sačuvaj PDF"),
    "sq": ("Portofol", "Showreel", "Blog", "Kontakt", "Ruaj PDF"),
    "fa": ("نمونه‌کار", "شوریل", "وبلاگ", "تماس", "ذخیره PDF"),
    "ur": ("پورٹ فولیو", "شو ریل", "بلاگ", "رابطہ", "PDF محفوظ کریں"),
    "hi": ("पोर्टफोलियो", "शो रील", "ब्लॉग", "संपर्क", "PDF सहेजें"),
    "zh-hans": ("作品集", "演示片", "博客", "联系方式", "保存 PDF"),
    "ja": ("ポートフォリオ", "ショーリール", "ブログ", "連絡先", "PDFを保存"),
    "ko": ("포트폴리오", "쇼릴", "블로그", "문의", "PDF 저장"),
}

EXTRAS = {
    "tr": ("İsteğe bağlı ölçüler — yalnız manuel doğrulamadan sonra", "Tahmini ölçüler yayımlanmaz."),
    "en": ("Optional measurements — manual verification only", "Estimated measurements are not published."),
    "ru": ("Дополнительные измерения — только после ручной проверки", "Оценочные измерения не публикуются."),
    "ar": ("قياسات إضافية — بعد التحقق اليدوي فقط", "لا تُنشر القياسات التقديرية."),
    "az": ("Əlavə ölçülər — yalnız əl ilə yoxlamadan sonra", "Təxmini ölçülər yayımlanmır."),
    "de": ("Optionale Maße — nur nach manueller Prüfung", "Geschätzte Maße werden nicht veröffentlicht."),
    "fr": ("Mensurations facultatives — uniquement après vérification manuelle", "Les mensurations estimées ne sont pas publiées."),
    "es": ("Medidas opcionales — solo tras verificación manual", "Las medidas estimadas no se publican."),
    "kk": ("Қосымша өлшемдер — тек қолмен тексергеннен кейін", "Болжамды өлшемдер жарияланбайды."),
    "uz": ("Qo‘shimcha o‘lchamlar — faqat qo‘lda tekshirilgandan keyin", "Taxminiy o‘lchamlar e’lon qilinmaydi."),
    "ky": ("Кошумча өлчөмдөр — кол менен текшерилгенден кийин гана", "Болжолдуу өлчөмдөр жарыяланбайт."),
    "tk": ("Goşmaça ölçegler — diňe el bilen tassyklanandan soň", "Çaklama ölçegler çap edilmeýär."),
    "it": ("Misure facoltative — solo dopo verifica manuale", "Le misure stimate non vengono pubblicate."),
    "pt-br": ("Medidas opcionais — somente após verificação manual", "Medidas estimadas não são publicadas."),
    "uk": ("Додаткові мірки — лише після ручної перевірки", "Орієнтовні мірки не публікуються."),
    "pl": ("Opcjonalne wymiary — tylko po ręcznej weryfikacji", "Szacunkowe wymiary nie są publikowane."),
    "bg": ("Допълнителни мерки — само след ръчна проверка", "Приблизителни мерки не се публикуват."),
    "el": ("Προαιρετικές μετρήσεις — μόνο μετά από χειροκίνητη επαλήθευση", "Οι εκτιμώμενες μετρήσεις δεν δημοσιεύονται."),
    "sr-latn": ("Dodatne mere — samo nakon ručne provere", "Procenjene mere se ne objavljuju."),
    "sq": ("Masa shtesë — vetëm pas verifikimit manual", "Masat e vlerësuara nuk publikohen."),
    "fa": ("اندازه‌های اختیاری — فقط پس از بررسی دستی", "اندازه‌های تخمینی منتشر نمی‌شوند."),
    "ur": ("اختیاری پیمائشیں — صرف دستی تصدیق کے بعد", "تخمینی پیمائشیں شائع نہیں کی جاتیں۔"),
    "hi": ("वैकल्पिक माप — केवल मैन्युअल सत्यापन के बाद", "अनुमानित माप प्रकाशित नहीं किए जाते।"),
    "zh-hans": ("可选尺寸——仅在人工核实后", "估算尺寸不会发布。"),
    "ja": ("任意の採寸情報 — 手動確認後のみ", "推定値は公開しません。"),
    "ko": ("선택 치수 — 수동 확인 후에만", "추정 치수는 공개하지 않습니다."),
}


def css() -> str:
    source = TEMPLATE.read_text(encoding="utf-8")
    start, end = source.index("<style>"), source.index("</style>") + len("</style>")
    return source[start:end]


def generic_nav(code: str, portfolio: str) -> tuple[str, str, str, str, str]:
    assert code in NAV
    return NAV[code]


def page(code: str, data: tuple[str, ...], stylesheet: str) -> str:
    label, direction, role, intro, _notice, facts, values, words = data
    # Do not expose a child's birth date/year in HTML or the rendered PDF.
    fact_labels, fact_values, words = split(facts)[1:], split(values)[1:], split(words)
    assert len(fact_labels) == len(fact_values) == 6 and len(words) == 10
    tag = LANG_TAG[code]
    rtl = ' dir="rtl"' if direction == "rtl" else ""
    nav_portfolio, nav_showreel, nav_blog, nav_contact, nav_pdf = generic_nav(code, words[1])
    extras_summary, extras_policy = EXTRAS[code]
    alternate = "\n".join(
        f'<link rel="alternate" hreflang="{LANG_TAG[other]}" href="{ORIGIN}/casting-card/{other}">' for other in L
    )
    selector = "".join(
        f'<a{" class=\"active\" aria-current=\"page\"" if other == code else ""} href="/casting-card/{other}">{h(other_data[0])}</a>'
        for other, other_data in L.items()
    )
    facts_html = "".join(
        f'<div class="fact"><span>{h(k)}</span><strong>{h(v)}</strong><span>{h(k)}</span></div>'
        for k, v in zip(fact_labels, fact_values)
    )
    captions = words[3:7]
    looks = "".join(
        f'<figure class="look {klass}"><img height="1536" width="1024" src="{src}" alt="Serdar Armin Sargut portfolio photograph"><span>{h(caption)}</span></figure>'
        for (klass, src), caption in zip(LOOKS, captions)
    )
    upper = code.upper()
    pdf = f"Serdar-Armin-Sargut-Comp-Card-{upper}.pdf"
    language_note = LANGUAGE_NOTE[code]
    return f'''<!doctype html>
<html lang="{tag}"{rtl} translate="no" class="notranslate"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="google" content="notranslate"><meta name="theme-color" content="#090909">
<title>Serdar Armin Sargut | {h(role)} | Comp Card</title>
<meta name="description" content="{h(intro)}"><meta name="robots" content="index,follow">
<link rel="canonical" href="{ORIGIN}/casting-card/{code}">
{alternate}
<link rel="alternate" hreflang="x-default" href="{ORIGIN}/casting-card/tr">
<meta property="og:type" content="profile"><meta property="og:title" content="Serdar Armin Sargut | {h(role)}">
<meta property="og:description" content="{h(intro)}"><meta property="og:url" content="{ORIGIN}/casting-card/{code}">
<meta property="og:image" content="{ORIGIN}{PHOTO}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{stylesheet}
<style>.language-disclaimer{{margin:10px 0 0;color:var(--muted);font-size:.76rem;line-height:1.42}}html[dir="rtl"] .info,html[dir="rtl"] .contact-panel{{text-align:right}}</style>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"ProfilePage","url":"{ORIGIN}/casting-card/{code}","name":"Serdar Armin Sargut | {h(role)}","description":"{h(intro)}","inLanguage":"{tag}","mainEntity":{{"@type":"Person","name":"Serdar Armin Sargut","jobTitle":["Child Actor","Child Model"],"height":{{"@type":"QuantitativeValue","value":162,"unitCode":"CMT"}},"url":"{ORIGIN}/","email":"info@serdararminsargut.com"}}}}</script>
</head><body class="single-language"><nav><div class="wrap"><a class="brand" href="/">SAS</a><a href="/">{h(nav_portfolio)}</a><a class="nav-current" aria-current="page" href="/casting-card/{code}">Comp Card</a><a href="/#showreel">{h(nav_showreel)}</a><a href="/blog/">{h(nav_blog)}</a><a href="/#iletisim">{h(nav_contact)}</a><a class="nav-btn" href="/downloads/{pdf}" download>{h(nav_pdf)}</a></div></nav>
<main class="card-shell"><section class="top"><div class="headshot-wrap"><img height="1536" width="1536" class="headshot" src="{PHOTO}" alt="Serdar Armin Sargut portfolio portrait" fetchpriority="high"></div><div class="info"><div class="eyebrow">{h(role)}</div><div class="location">{h(words[9])}</div><h1>Serdar Armin<br><span class="accent">Sargut</span></h1><p class="lead">{h(intro)}</p><div class="facts">{facts_html}</div><div class="actions"><a class="btn primary" href="/downloads/{pdf}" download>{h(words[0])}</a><a class="btn" href="/">{h(words[1])}</a><a class="btn" href="https://www.instagram.com/serdararminsargutt/" target="_blank" rel="noopener noreferrer">Instagram</a><p class="pdf-language-note">{h(label)} · {upper}</p></div><p class="language-disclaimer">{h(language_note)}</p><div class="language-switch" aria-label="Comp Card languages">{selector}</div></div></section><section class="looks" id="looks"><div class="looks-head"><div><div class="eyebrow">{h(words[2])}</div><h2>{h(words[2])}</h2></div><div class="looks-note">{h(label)}</div></div><div class="photo-grid">{looks}</div></section><section class="bottom" id="contact"><div class="contact-panel"><div><h3>{h(words[7])}</h3><p><strong>{h(words[8])}</strong></p><p><strong>Email:</strong> <a href="mailto:info@serdararminsargut.com">info@serdararminsargut.com</a></p><p><strong>{h(words[9])}</strong></p><p><strong>{h(words[1])}:</strong> <a href="{ORIGIN}/">serdararminsargut.com</a></p></div></div><div class="qr-panel"><img height="450" width="450" src="/assets/portfolio-qr.png" alt="QR code to official portfolio"></div></section><section class="extras"><details><summary>{h(extras_summary)}</summary><p class="policy">{h(extras_policy)}</p></details></section></main><footer>Serdar Armin Sargut · {h(words[8])}</footer></body></html>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stylesheet = css()
    for code, data in L.items():
        (OUT / f"{code}.html").write_text(page(code, data, stylesheet), encoding="utf-8")
    print(f"SERDAR_26_RELEASE_SOURCES_BUILT {len(L)}/26")


if __name__ == "__main__":
    main()
