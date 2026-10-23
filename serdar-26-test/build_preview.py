#!/usr/bin/env python3
"""Build a Serdar-only, noindex, 26-locale static preview without network calls."""
import html, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
PHOTO = "https://serdararminsargut.com/assets/photos/serdar-armin-sargut-cocuk-oyuncu-model-portre-1536-v12-1-20260826.webp"
EMAIL = "info@serdararminsargut.com"

LOCALES = [
("tr","Türkçe","ltr","Çocuk oyuncu ve model portföyü","Yayın onayı bekleyen editoryal taslak"),
("en","English","ltr","Child actor and model portfolio","Editorial draft pending publication approval"),
("ru","Русский","ltr","Портфолио детского актёра и модели","Редакционный черновик ожидает одобрения публикации"),
("ar","العربية","rtl","ملف أعمال ممثل وعارض أزياء للأطفال","مسودة تحريرية بانتظار موافقة النشر"),
("az","Azərbaycanca","ltr","Uşaq aktyor və model portfeli","Yayıma təsdiq gözləyən redaksiya qaralaması"),
("de","Deutsch","ltr","Portfolio für Kinderschauspiel und Kindermodel","Redaktioneller Entwurf – Freigabe zur Veröffentlichung ausstehend"),
("fr","Français","ltr","Portfolio d’enfant acteur et mannequin","Brouillon éditorial en attente d’approbation de publication"),
("es","Español","ltr","Portafolio de actor y modelo infantil","Borrador editorial pendiente de aprobación de publicación"),
("kk","Қазақша","ltr","Бала актер және модель портфолиосы","Жариялау мақұлдауын күткен редакциялық нобай"),
("uz","O‘zbekcha","ltr","Bolalar aktyori va modeli portfeli","Nashr tasdig‘ini kutayotgan tahririy qoralama"),
("ky","Кыргызча","ltr","Бала актер жана модель портфолиосу","Жарыялоого бекитүү күтүлгөн редакциялык долбоор"),
("tk","Türkmençe","ltr","Çaga aktýorynyň we modeliniň portfeli","Çap etmäge tassyklama garaşýan redaksiýa taslamasy"),
("it","Italiano","ltr","Portfolio di attore e modello bambino","Bozza editoriale in attesa di approvazione alla pubblicazione"),
("pt-BR","Português (Brasil)","ltr","Portfólio de ator e modelo infantil","Rascunho editorial aguardando aprovação para publicação"),
("uk","Українська","ltr","Портфоліо дитячого актора і моделі","Редакційна чернетка очікує схвалення публікації"),
("pl","Polski","ltr","Portfolio dziecięcego aktora i modela","Szkic redakcyjny oczekujący na zgodę na publikację"),
("bg","Български","ltr","Портфолио на детски актьор и модел","Редакционна чернова в очакване на одобрение за публикуване"),
("el","Ελληνικά","ltr","Χαρτοφυλάκιο παιδιού ηθοποιού και μοντέλου","Συντακτικό προσχέδιο σε αναμονή έγκρισης δημοσίευσης"),
("sr-Latn","Srpski (latinica)","ltr","Portfolio dečjeg glumca i modela","Urednički nacrt čeka odobrenje za objavljivanje"),
("sq","Shqip","ltr","Portofol për aktor dhe model fëmijë","Draft editorial në pritje të miratimit për publikim"),
("fa","فارسی","rtl","نمونه‌کار بازیگر و مدل کودک","پیش‌نویس تحریری در انتظار تأیید انتشار"),
("ur","اردو","rtl","بچوں کے اداکار اور ماڈل کا پورٹ فولیو","ادارتی مسودہ اشاعتی منظوری کا منتظر ہے"),
("hi","हिन्दी","ltr","बाल अभिनेता और मॉडल पोर्टफोलियो","संपादकीय मसौदा प्रकाशन स्वीकृति की प्रतीक्षा में है"),
("zh-CN","简体中文","ltr","儿童演员与模特作品集","等待发布批准的编辑草稿"),
("ja","日本語","ltr","子役・キッズモデルのポートフォリオ","公開承認待ちの編集草稿"),
("ko","한국어","ltr","아역 배우 및 키즈 모델 포트폴리오","게시 승인을 기다리는 편집 초안"),
]

def page(code,label,direction,role,draft):
    links="".join(f'<a href="../{html.escape(other_code)}/">{html.escape(other_label)}</a>' for other_code,other_label,*_ in LOCALES)
    return f'''<!doctype html><html lang="{html.escape(code)}" dir="{direction}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow,noarchive"><title>Serdar Armin Sargut | {html.escape(role)} | Test preview</title>
<style>:root{{--ink:#f5f1e8;--muted:#c8beb0;--panel:#16130f;--line:#5d5141;--gold:#d8b87d}}*{{box-sizing:border-box}}body{{margin:0;background:#090909;color:var(--ink);font:16px/1.55 Arial,sans-serif}}main{{width:min(960px,calc(100% - 28px));margin:auto;padding:28px 0 48px}}.notice{{border:1px solid var(--gold);padding:12px 14px;color:var(--gold);font-weight:700}}.card{{display:grid;grid-template-columns:minmax(220px,.8fr) 1.2fr;gap:28px;margin-top:24px;padding:24px;background:var(--panel);border:1px solid var(--line)}}img{{width:100%;aspect-ratio:1/1.2;object-fit:cover}}h1{{font:400 clamp(2.4rem,7vw,5rem)/.92 Georgia,serif;margin:.2em 0}}p{{color:var(--muted)}}.meta{{font-weight:700;color:var(--gold);letter-spacing:.08em;text-transform:uppercase}}.languages{{display:flex;flex-wrap:wrap;gap:8px;margin-top:28px}}.languages a{{color:var(--ink);border:1px solid var(--line);padding:7px 9px;text-decoration:none;font-size:.84rem}}@media(max-width:650px){{.card{{grid-template-columns:1fr;gap:18px;padding:16px}}main{{width:min(100% - 18px,960px);padding-top:12px}}}}</style></head><body><main>
<div class="notice">TEST PREVIEW · NOINDEX · {html.escape(draft)}</div><section class="card"><img src="{PHOTO}" alt="Serdar Armin Sargut portfolio portrait"><div><div class="meta">{html.escape(label)} · 2026</div><h1>Serdar Armin<br> Sargut</h1><h2>{html.escape(role)}</h2><p>{html.escape(draft)}</p><p>This is an editorial interface translation draft. It does not state or imply that Serdar speaks this language.</p><p>Professional contact is parent/guardian managed: <a href="mailto:{EMAIL}">{EMAIL}</a></p></div></section><nav class="languages" aria-label="Preview languages">{links}</nav></main></body></html>'''

def main():
    manifest=json.loads((ROOT/"locale_manifest.json").read_text(encoding="utf-8"))
    assert manifest["target_locales"] == [code for code,*_ in LOCALES]
    if OUT.exists(): shutil.rmtree(OUT)
    for code,label,direction,role,draft in LOCALES:
        destination=OUT/code/"index.html"; destination.parent.mkdir(parents=True)
        destination.write_text(page(code,label,direction,role,draft),encoding="utf-8")
    (OUT/"_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n",encoding="utf-8")
    print("SERDAR_26_NOINDEX_PREVIEW_BUILT 26/26")
if __name__=="__main__": main()
