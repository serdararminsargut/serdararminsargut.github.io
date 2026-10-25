#!/usr/bin/env python3
"""Build the isolated, noindex 26-language Serdar Comp Card candidate.

This does not edit the production sitemap, canonical routes, Cloudflare
configuration, or Duru files. It only creates reviewable candidate files on a
dedicated Serdar test branch.
"""
from __future__ import annotations

import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "serdar-26-candidate" / "casting-card"
ORIGIN = "https://serdararminsargut.com"
PHOTO = "/assets/photos/serdar-armin-sargut-cocuk-oyuncu-model-portre-1536-v12-1-20260826.webp"
LOOKS = (
    ("full", "/assets/photos/serdar-armin-sargut-bej-takim-tam-boy.webp"),
    ("classic", "/assets/photos/serdar-armin-sargut-gri-takim-yelek.webp"),
    ("sport", "/assets/photos/serdar-armin-sargut-futbol-spor-portre.webp"),
    ("life", "/assets/photos/serdar-armin-sargut-beyaz-tisort-lifestyle.webp"),
)

# The source vocabulary is deliberately compact. The profile facts themselves
# are fixed, already approved Serdar data; no measurement is inferred here.
L = {
 "tr": ("Türkçe","ltr","Çocuk Oyuncu ve Model","Profesyonel çocuk oyuncu ve model portföyü; reklam, sinema, televizyon, katalog, moda, çocuk giyim, spor giyim, ayakkabı ve yaşam tarzı projeleri için.","Yayın öncesi editoryal önizleme","Doğum yılı|Boy|Göz rengi|Saç|Ayakkabı numarası|Yönetim|Profesyonel iletişim","2014|162 cm|Yeşil|Sarışın · Dalgalı|37 EU|Ebeveyn / veli|info@serdararminsargut.com","PDF indir|Resmî portföy|Seçili portföy görünümleri|Tam boy|Klasik|Spor|Yaşam tarzı|Profesyonel iletişim|Ebeveyn / veli yönetiminde|İstanbul, Türkiye"),
 "en": ("English","ltr","Child Actor and Model","Professional child actor and model portfolio for commercial, film, television, catalogue, fashion, kidswear, sportswear, footwear and lifestyle projects.","Editorial preview before publication","Year of birth|Height|Eye colour|Hair|Shoe size|Management|Professional contact","2014|162 cm|Green|Blonde · Wavy|37 EU|Parent / guardian|info@serdararminsargut.com","Download PDF|Official portfolio|Selected portfolio looks|Full length|Classic|Sport|Lifestyle|Professional contact|Parent / guardian managed|Istanbul, Türkiye"),
 "ru": ("Русский","ltr","Детский актёр и модель","Профессиональное портфолио детского актёра и модели для рекламы, кино, телевидения, каталогов, моды, детской и спортивной одежды, обуви и lifestyle-проектов.","Редакционная предварительная версия до публикации","Год рождения|Рост|Цвет глаз|Волосы|Размер обуви|Представительство|Профессиональный контакт","2014|162 см|Зелёные|Светлые · Волнистые|37 EU|Родитель / опекун|info@serdararminsargut.com","Скачать PDF|Официальное портфолио|Избранные образы|В полный рост|Классика|Спорт|Повседневный стиль|Профессиональные запросы|Под управлением родителя / опекуна|Стамбул, Турция"),
 "ar": ("العربية","rtl","ممثل وعارض أزياء للأطفال","ملف مهني لممثل وعارض أزياء للأطفال لمشاريع الإعلان والسينما والتلفزيون والكتالوغ والأزياء وملابس الأطفال والملابس الرياضية والأحذية ونمط الحياة.","معاينة تحريرية قبل النشر","سنة الميلاد|الطول|لون العينين|الشعر|مقاس الحذاء|الإدارة|التواصل المهني","2014|162 سم|أخضر|أشقر · مموّج|37 EU|الوالد / الوصي|info@serdararminsargut.com","تحميل PDF|الملف الرسمي|إطلالات مختارة|كامل الطول|كلاسيكي|رياضي|نمط حياة|طلبات مهنية|بإدارة الوالد / الوصي|إسطنبول، تركيا"),
 "az": ("Azərbaycanca","ltr","Uşaq aktyor və model","Reklam, kino, televiziya, kataloq, moda, uşaq geyimi, idman geyimi, ayaqqabı və həyat tərzi layihələri üçün peşəkar uşaq aktyor və model portfeli.","Nəşrdən əvvəl redaksiya önbaxışı","Doğum ili|Boy|Göz rəngi|Saç|Ayaqqabı ölçüsü|İdarəetmə|Peşəkar əlaqə","2014|162 sm|Yaşıl|Sarışın · Dalğalı|37 EU|Valideyn / qəyyum|info@serdararminsargut.com","PDF yüklə|Rəsmi portfel|Seçilmiş görünüşlər|Tam boy|Klassik|İdman|Həyat tərzi|Peşəkar əlaqə|Valideyn / qəyyum idarəçiliyində|İstanbul, Türkiyə"),
 "de": ("Deutsch","ltr","Kinderschauspieler und Model","Professionelles Portfolio für Kinderschauspiel, Werbung, Film, Fernsehen, Katalog, Mode, Kinder- und Sportbekleidung, Schuhe und Lifestyle-Projekte.","Redaktionelle Vorschau vor Veröffentlichung","Geburtsjahr|Körpergröße|Augenfarbe|Haare|Schuhgröße|Management|Beruflicher Kontakt","2014|162 cm|Grün|Blond · Wellig|37 EU|Eltern / Sorgeberechtigte|info@serdararminsargut.com","PDF herunterladen|Offizielles Portfolio|Ausgewählte Looks|Ganzkörper|Klassisch|Sport|Lifestyle|Beruflicher Kontakt|Von Eltern / Sorgeberechtigten verwaltet|Istanbul, Türkei"),
 "fr": ("Français","ltr","Enfant acteur et mannequin","Portfolio professionnel d’enfant acteur et mannequin pour la publicité, le cinéma, la télévision, les catalogues, la mode, les vêtements enfant et sport, les chaussures et les projets lifestyle.","Aperçu éditorial avant publication","Année de naissance|Taille|Couleur des yeux|Cheveux|Pointure|Gestion|Contact professionnel","2014|162 cm|Verts|Blonds · Ondulés|37 EU|Parent / tuteur|info@serdararminsargut.com","Télécharger le PDF|Portfolio officiel|Looks sélectionnés|Plein pied|Classique|Sport|Lifestyle|Contact professionnel|Géré par parent / tuteur|Istanbul, Turquie"),
 "es": ("Español","ltr","Actor y modelo infantil","Portafolio profesional de actor y modelo infantil para publicidad, cine, televisión, catálogo, moda, ropa infantil y deportiva, calzado y proyectos de estilo de vida.","Vista editorial antes de publicar","Año de nacimiento|Altura|Color de ojos|Cabello|Talla de calzado|Representación|Contacto profesional","2014|162 cm|Verdes|Rubio · Ondulado|37 EU|Padre / tutor|info@serdararminsargut.com","Descargar PDF|Portafolio oficial|Looks seleccionados|Cuerpo completo|Clásico|Deportivo|Lifestyle|Contacto profesional|Gestionado por padre / tutor|Estambul, Turquía"),
 "kk": ("Қазақша","ltr","Бала актер және модель","Жарнама, кино, теледидар, каталог, сән, балалар және спорт киімі, аяқ киім және lifestyle жобаларына арналған кәсіби бала актер мен модель портфолиосы.","Жариялар алдындағы редакциялық алдын ала қарау","Туған жылы|Бойы|Көз түсі|Шашы|Аяқ киім өлшемі|Басқару|Кәсіби байланыс","2014|162 см|Жасыл|Ақшыл · Толқынды|37 EU|Ата-ана / қамқоршы|info@serdararminsargut.com","PDF жүктеу|Ресми портфолио|Таңдалған образдар|Толық бой|Классикалық|Спорт|Өмір салты|Кәсіби байланыс|Ата-ана / қамқоршы басқарады|Ыстанбұл, Түркия"),
 "uz": ("O‘zbekcha","ltr","Bola aktyor va model","Reklama, kino, televideniye, katalog, moda, bolalar va sport kiyimlari, poyabzal hamda turmush tarzi loyihalari uchun professional bola aktyor va model portfeli.","Nashrdan oldingi tahririy ko‘rinish","Tug‘ilgan yil|Bo‘y|Ko‘z rangi|Soch|Poyabzal o‘lchami|Boshqaruv|Professional aloqa","2014|162 sm|Yashil|Sariq · To‘lqinsimon|37 EU|Ota-ona / vasiy|info@serdararminsargut.com","PDF yuklab olish|Rasmiy portfel|Tanlangan ko‘rinishlar|To‘liq bo‘y|Klassik|Sport|Turmush tarzi|Professional aloqa|Ota-ona / vasiy boshqaruvida|Istanbul, Turkiya"),
 "ky": ("Кыргызча","ltr","Бала актер жана модель","Жарнама, кино, телевидение, каталог, мода, балдар жана спорт кийими, бут кийим жана жашоо стили долбоорлору үчүн кесипкөй бала актер жана модель портфолиосу.","Жарыялоого чейинки редакциялык алдын ала кароо","Туулган жылы|Бою|Көзүнүн түсү|Чачы|Бут кийим өлчөмү|Башкаруу|Кесипкөй байланыш","2014|162 см|Жашыл|Сары · Толкундуу|37 EU|Ата-эне / камкорчу|info@serdararminsargut.com","PDF жүктөө|Расмий портфолио|Тандалган образдар|Толук бой|Классикалык|Спорт|Жашоо стили|Кесипкөй байланыш|Ата-эне / камкорчу башкарат|Стамбул, Түркия"),
 "tk": ("Türkmençe","ltr","Çaga aktýory we model","Mahabat, kino, telewideniýe, katalog, moda, çaga we sport geýimleri, aýakgap we durmuş ýörelgesi taslamalary üçin hünär taýdan çaga aktýory we model portfeli.","Çap edilmezinden öň redaksiýa syny","Doglan ýyly|Boýy|Gözüniň reňki|Saçy|Aýakgap ölçegi|Dolandyryş|Hünär aragatnaşygy","2014|162 sm|Ýaşyl|Sarymtyl · Tolkunly|37 EU|Ene-ata / hossar|info@serdararminsargut.com","PDF ýükle|Resmi portfel|Saýlanan görnüşler|Doly boý|Klassik|Sport|Durmuş ýörelgesi|Hünär aragatnaşygy|Ene-ata / hossar dolandyrýar|Stambul, Türkiýe"),
 "it": ("Italiano","ltr","Attore e modello bambino","Portfolio professionale di attore e modello bambino per pubblicità, cinema, televisione, cataloghi, moda, abbigliamento bambino e sportivo, calzature e progetti lifestyle.","Anteprima editoriale prima della pubblicazione","Anno di nascita|Altezza|Colore degli occhi|Capelli|Numero di scarpe|Gestione|Contatto professionale","2014|162 cm|Verdi|Biondi · Mossi|37 EU|Genitore / tutore|info@serdararminsargut.com","Scarica PDF|Portfolio ufficiale|Look selezionati|Figura intera|Classico|Sport|Lifestyle|Contatto professionale|Gestito da genitore / tutore|Istanbul, Turchia"),
 "pt-br": ("Português (Brasil)","ltr","Ator e modelo infantil","Portfólio profissional de ator e modelo infantil para publicidade, cinema, televisão, catálogo, moda, roupas infantis e esportivas, calçados e projetos de lifestyle.","Prévia editorial antes da publicação","Ano de nascimento|Altura|Cor dos olhos|Cabelo|Número do calçado|Gestão|Contato profissional","2014|162 cm|Verdes|Loiro · Ondulado|37 EU|Responsável / tutor|info@serdararminsargut.com","Baixar PDF|Portfólio oficial|Looks selecionados|Corpo inteiro|Clássico|Esporte|Lifestyle|Contato profissional|Gerenciado por responsável / tutor|Istambul, Turquia"),
 "uk": ("Українська","ltr","Дитячий актор і модель","Професійне портфоліо дитячого актора і моделі для реклами, кіно, телебачення, каталогів, моди, дитячого та спортивного одягу, взуття і lifestyle-проєктів.","Редакційний попередній перегляд до публікації","Рік народження|Зріст|Колір очей|Волосся|Розмір взуття|Представництво|Професійний контакт","2014|162 см|Зелені|Світле · Хвилясте|37 EU|Батьки / опікун|info@serdararminsargut.com","Завантажити PDF|Офіційне портфоліо|Вибрані образи|На повний зріст|Класичний|Спорт|Lifestyle|Професійний контакт|Під управлінням батьків / опікуна|Стамбул, Туреччина"),
 "pl": ("Polski","ltr","Aktor i model dziecięcy","Profesjonalne portfolio aktora i modela dziecięcego do reklam, filmu, telewizji, katalogów, mody, odzieży dziecięcej i sportowej, obuwia oraz projektów lifestyle.","Podgląd redakcyjny przed publikacją","Rok urodzenia|Wzrost|Kolor oczu|Włosy|Rozmiar obuwia|Zarządzanie|Kontakt zawodowy","2014|162 cm|Zielone|Blond · Falowane|37 EU|Rodzic / opiekun|info@serdararminsargut.com","Pobierz PDF|Oficjalne portfolio|Wybrane stylizacje|Pełna sylwetka|Klasyczny|Sport|Lifestyle|Kontakt zawodowy|Zarządzane przez rodzica / opiekuna|Stambuł, Turcja"),
 "bg": ("Български","ltr","Детски актьор и модел","Професионално портфолио на детски актьор и модел за реклама, кино, телевизия, каталози, мода, детско и спортно облекло, обувки и lifestyle проекти.","Редакционен преглед преди публикуване","Година на раждане|Ръст|Цвят на очите|Коса|Номер обувки|Управление|Професионален контакт","2014|162 см|Зелени|Руси · Вълнисти|37 EU|Родител / настойник|info@serdararminsargut.com","Изтегли PDF|Официално портфолио|Избрани визии|Цял ръст|Класически|Спорт|Lifestyle|Професионален контакт|Управлявано от родител / настойник|Истанбул, Турция"),
 "el": ("Ελληνικά","ltr","Παιδί ηθοποιός και μοντέλο","Επαγγελματικό portfolio παιδιού ηθοποιού και μοντέλου για διαφήμιση, κινηματογράφο, τηλεόραση, καταλόγους, μόδα, παιδικά και αθλητικά ρούχα, υποδήματα και lifestyle έργα.","Συντακτική προεπισκόπηση πριν από τη δημοσίευση","Έτος γέννησης|Ύψος|Χρώμα ματιών|Μαλλιά|Μέγεθος παπουτσιού|Διαχείριση|Επαγγελματική επικοινωνία","2014|162 εκ.|Πράσινα|Ξανθά · Κυματιστά|37 EU|Γονέας / κηδεμόνας|info@serdararminsargut.com","Λήψη PDF|Επίσημο portfolio|Επιλεγμένες εμφανίσεις|Ολόσωμο|Κλασικό|Αθλητικό|Lifestyle|Επαγγελματική επικοινωνία|Διαχείριση από γονέα / κηδεμόνα|Κωνσταντινούπολη, Τουρκία"),
 "sr-latn": ("Srpski (latinica)","ltr","Dečji glumac i model","Profesionalni portfolio dečjeg glumca i modela za reklame, film, televiziju, kataloge, modu, dečju i sportsku odeću, obuću i lifestyle projekte.","Urednički pregled pre objavljivanja","Godina rođenja|Visina|Boja očiju|Kosa|Veličina obuće|Zastupanje|Profesionalni kontakt","2014|162 cm|Zelene|Plava · Talasasta|37 EU|Roditelj / staratelj|info@serdararminsargut.com","Preuzmi PDF|Zvanični portfolio|Odabrani izgledi|Ceo stas|Klasično|Sport|Lifestyle|Profesionalni kontakt|Upravljanje roditelja / staratelja|Istanbul, Turska"),
 "sq": ("Shqip","ltr","Aktor dhe model fëmijë","Portofol profesional i aktorit dhe modelit fëmijë për reklamë, film, televizion, katalogë, modë, veshje për fëmijë e sportive, këpucë dhe projekte lifestyle.","Parapamje editoriale para publikimit","Viti i lindjes|Gjatësia|Ngjyra e syve|Flokët|Masa e këpucëve|Menaxhimi|Kontakt profesional","2014|162 cm|Të gjelbër|Biondë · Me onde|37 EU|Prind / kujdestar|info@serdararminsargut.com","Shkarko PDF|Portofoli zyrtar|Pamje të zgjedhura|I plotë|Klasik|Sport|Lifestyle|Kontakt profesional|Menaxhohet nga prindi / kujdestari|Stamboll, Turqi"),
 "fa": ("فارسی","rtl","بازیگر و مدل کودک","نمونه‌کار حرفه‌ای بازیگر و مدل کودک برای تبلیغات، سینما، تلویزیون، کاتالوگ، مد، پوشاک کودک و ورزشی، کفش و پروژه‌های سبک زندگی.","پیش‌نمایش تحریری پیش از انتشار","سال تولد|قد|رنگ چشم|مو|سایز کفش|مدیریت|تماس حرفه‌ای","2014|162 سانتی‌متر|سبز|بلوند · موج‌دار|37 EU|والد / سرپرست|info@serdararminsargut.com","دانلود PDF|نمونه‌کار رسمی|استایل‌های منتخب|تمام‌قد|کلاسیک|ورزشی|سبک زندگی|تماس حرفه‌ای|تحت مدیریت والد / سرپرست|استانبول، ترکیه"),
 "ur": ("اردو","rtl","بچوں کے اداکار اور ماڈل","اشتہارات، فلم، ٹیلی ویژن، کیٹلاگ، فیشن، بچوں اور اسپورٹس ویئر، جوتوں اور طرزِ زندگی کے منصوبوں کے لیے پیشہ ور بچوں کے اداکار اور ماڈل کا پورٹ فولیو۔","اشاعت سے پہلے اداراتی پیش نظارہ","پیدائش کا سال|قد|آنکھوں کا رنگ|بال|جوتے کا سائز|انتظام|پیشہ ورانہ رابطہ","2014|162 سینٹی میٹر|سبز|سنہرے · لہردار|37 EU|والد / سرپرست|info@serdararminsargut.com","PDF ڈاؤن لوڈ کریں|سرکاری پورٹ فولیو|منتخب انداز|مکمل قد|کلاسک|کھیل|طرزِ زندگی|پیشہ ورانہ رابطہ|والد / سرپرست کے زیر انتظام|استنبول، ترکیہ"),
 "hi": ("हिन्दी","ltr","बाल अभिनेता और मॉडल","विज्ञापन, फ़िल्म, टेलीविजन, कैटलॉग, फैशन, बच्चों और खेल परिधान, जूते तथा लाइफस्टाइल परियोजनाओं के लिए पेशेवर बाल अभिनेता और मॉडल पोर्टफोलियो।","प्रकाशन से पहले संपादकीय पूर्वावलोकन","जन्म वर्ष|कद|आँखों का रंग|बाल|जूते का आकार|प्रबंधन|पेशेवर संपर्क","2014|162 सेमी|हरे|सुनहरे · लहरदार|37 EU|माता-पिता / अभिभावक|info@serdararminsargut.com","PDF डाउनलोड|आधिकारिक पोर्टफोलियो|चुने हुए लुक|पूरा कद|क्लासिक|खेल|लाइफस्टाइल|पेशेवर संपर्क|माता-पिता / अभिभावक द्वारा प्रबंधित|इस्तांबुल, तुर्किये"),
 "zh-hans": ("简体中文","ltr","儿童演员与模特","面向广告、电影、电视、目录、时尚、童装、运动装、鞋履和生活方式项目的专业儿童演员与模特作品集。","发布前编辑预览","出生年份|身高|眼睛颜色|头发|鞋码|管理|专业联系","2014|162 厘米|绿色|金色 · 微卷|37 EU|父母 / 监护人|info@serdararminsargut.com","下载 PDF|官方作品集|精选造型|全身照|经典|运动|生活方式|专业联系|由父母 / 监护人管理|伊斯坦布尔，土耳其"),
 "ja": ("日本語","ltr","子役・キッズモデル","広告、映画、テレビ、カタログ、ファッション、子ども服、スポーツウェア、靴、ライフスタイル案件のための子役・キッズモデルのプロフェッショナルポートフォリオ。","公開前の編集プレビュー","生年|身長|瞳の色|髪|靴のサイズ|管理|業務連絡","2014|162 cm|緑|ブロンド · ウェーブ|37 EU|保護者|info@serdararminsargut.com","PDFをダウンロード|公式ポートフォリオ|選択されたルック|全身|クラシック|スポーツ|ライフスタイル|業務連絡|保護者による管理|イスタンブール、トルコ"),
 "ko": ("한국어","ltr","아역 배우 및 키즈 모델","광고, 영화, 텔레비전, 카탈로그, 패션, 아동복, 스포츠웨어, 신발 및 라이프스타일 프로젝트를 위한 아역 배우 및 키즈 모델 전문 포트폴리오입니다.","게시 전 편집 미리보기","출생 연도|키|눈 색|머리|신발 사이즈|관리|업무 문의","2014|162 cm|녹색|금발 · 웨이브|37 EU|부모 / 보호자|info@serdararminsargut.com","PDF 다운로드|공식 포트폴리오|선택된 룩|전신|클래식|스포츠|라이프스타일|업무 문의|부모 / 보호자 관리|이스탄불, 튀르키예"),
}

# A translated presentation is not a claim about the child's spoken languages.
# Keeping this disclosure in every locale prevents a casting reader from
# inferring language ability from the page selector.
LANGUAGE_NOTE = {
 "tr": "Sunum dili, Serdar’ın bu dili konuştuğu anlamına gelmez.",
 "en": "The presentation language does not indicate that Serdar speaks it.",
 "ru": "Язык презентации не означает, что Сердар говорит на этом языке.",
 "ar": "لغة العرض لا تعني أن سردار يتحدث هذه اللغة.",
 "az": "Təqdimat dili Serdarın bu dildə danışdığını göstərmir.",
 "de": "Die Sprache der Präsentation bedeutet nicht, dass Serdar diese Sprache spricht.",
 "fr": "La langue de présentation n’indique pas que Serdar parle cette langue.",
 "es": "El idioma de presentación no indica que Serdar hable ese idioma.",
 "kk": "Таныстырылым тілі Сердардың бұл тілде сөйлейтінін білдірмейді.",
 "uz": "Taqdimot tili Serdar bu tilda gaplashishini anglatmaydi.",
 "ky": "Презентациянын тили Сердардын бул тилде сүйлөй турганын билдирбейт.",
 "tk": "Tanyşdyrylyş dili Serdaryň bu dilde gürleýändigini aňlatmaýar.",
 "it": "La lingua di presentazione non indica che Serdar parli questa lingua.",
 "pt-br": "O idioma da apresentação não indica que Serdar fale esse idioma.",
 "uk": "Мова презентації не означає, що Сердар нею розмовляє.",
 "pl": "Język prezentacji nie oznacza, że Serdar mówi w tym języku.",
 "bg": "Езикът на представянето не означава, че Сердар говори този език.",
 "el": "Η γλώσσα παρουσίασης δεν σημαίνει ότι ο Serdar μιλά αυτή τη γλώσσα.",
 "sr-latn": "Jezik prezentacije ne znači da Serdar govori taj jezik.",
 "sq": "Gjuha e prezantimit nuk do të thotë se Serdar e flet atë gjuhë.",
 "fa": "زبان ارائه به این معنا نیست که سردار به این زبان صحبت می‌کند.",
 "ur": "پیشکش کی زبان کا مطلب یہ نہیں کہ سردار یہ زبان بولتے ہیں۔",
 "hi": "प्रस्तुति की भाषा का अर्थ यह नहीं है कि सेरदार यह भाषा बोलते हैं।",
 "zh-hans": "展示语言并不表示 Serdar 会说该语言。",
 "ja": "表示言語は、Serdarがその言語を話すことを示すものではありません。",
 "ko": "표시 언어는 Serdar가 해당 언어를 구사한다는 뜻이 아닙니다.",
}


def h(value: str) -> str:
    return html.escape(value, quote=True)


def split(value: str) -> list[str]:
    return value.split("|")


def page(code: str, data: tuple[str, ...]) -> str:
    label, direction, role, intro, notice, facts, values, words = data
    language_note = LANGUAGE_NOTE[code]
    fact_labels, fact_values, words = split(facts), split(values), split(words)
    assert len(fact_labels) == len(fact_values) == 7 and len(words) == 10
    lang_links = "".join(
        '<a{} href="./{}.html">{}</a>'.format(
            ' class="active" aria-current="page"' if other == code else "",
            other,
            h(other_data[0]),
        )
        for other, other_data in L.items()
    )
    alternate = "\n".join(
        f'<link rel="alternate" hreflang="{other}" href="{ORIGIN}/casting-card/{other}">' for other in L
    )
    facts_html = "".join(f'<div class="fact"><span>{h(k)}</span><strong>{h(v)}</strong><span>{h(k)}</span></div>' for k, v in zip(fact_labels, fact_values))
    photo_labels = words[3:7]
    looks_html = "".join(
        f'<figure class="look {klass}"><img height="1536" width="1024" src="{src}" alt="Serdar Armin Sargut portfolio photograph"><span>{h(caption)}</span></figure>'
        for (klass, src), caption in zip(LOOKS, photo_labels)
    )
    code_upper = code.upper()
    pdf_name = f"Serdar-Armin-Sargut-Comp-Card-{code_upper}.pdf"
    rtl = ' dir="rtl"' if direction == "rtl" else ""
    return f'''<!doctype html>
<html lang="{code}"{rtl} translate="no" class="notranslate"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="google" content="notranslate"><meta name="theme-color" content="#090909">
<meta name="robots" content="noindex,nofollow,noarchive">
<title>Serdar Armin Sargut | {h(role)} | Test preview</title>
<meta name="description" content="{h(intro)}"><link rel="canonical" href="{ORIGIN}/casting-card/{code}">
{alternate}
<meta property="og:type" content="profile"><meta property="og:title" content="Serdar Armin Sargut | {h(role)}">
<meta property="og:description" content="{h(intro)}"><meta property="og:url" content="{ORIGIN}/casting-card/{code}">
<meta property="og:image" content="{ORIGIN}{PHOTO}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>:root{{--bg:#090909;--panel:#121212;--ink:#f5f1e8;--muted:#aaa399;--line:#302d28;--gold:#cdb17c;--max:1180px}}*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 50% 0%,#1b1711 0,#090909 38%,#060606 100%);color:var(--ink);font-family:Arial,Helvetica,sans-serif;line-height:1.5}}a{{color:inherit}}.wrap{{width:min(var(--max),calc(100% - 28px));margin:auto}}nav{{position:sticky;top:0;z-index:30;background:rgba(9,9,9,.94);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}}nav .wrap{{display:flex;align-items:center;gap:14px;padding:11px 0;overflow-x:auto}}nav a{{text-decoration:none;color:var(--muted);font-size:.84rem;white-space:nowrap}}.brand{{font-weight:900;color:var(--ink);margin-right:auto}}.nav-current{{color:var(--gold)!important;border-color:var(--gold)!important;font-weight:800}}.preview{{background:#5b3c15;color:#fff4d9;text-align:center;padding:8px 12px;font-weight:800;font-size:.78rem;letter-spacing:.04em}}.card-shell{{width:min(1120px,calc(100% - 24px));margin:24px auto 46px;border:1px solid #2c2924;border-radius:26px;background:linear-gradient(150deg,#11100e,#080808 62%,#0c0a07);box-shadow:0 28px 80px rgba(0,0,0,.48);overflow:hidden}}.top{{display:grid;grid-template-columns:1fr 1.05fr;border-bottom:1px solid var(--line)}}.headshot-wrap{{padding:24px;border-right:1px solid var(--line)}}.headshot{{width:100%;height:100%;min-height:620px;object-fit:cover;object-position:center 17%;display:block;border:1px solid #575147;border-radius:17px}}.info{{padding:38px 34px 28px;display:flex;flex-direction:column;justify-content:center}}.eyebrow{{color:var(--gold);font-size:.73rem;font-weight:800;text-transform:uppercase;letter-spacing:.16em}}.location{{font-size:.72rem;color:#d5cfc4;letter-spacing:.16em;text-transform:uppercase;margin-top:7px}}h1{{font-family:Georgia,'Times New Roman',serif;font-size:clamp(3.25rem,6vw,5.7rem);font-weight:400;line-height:.9;letter-spacing:-.035em;margin:25px 0 16px}}.accent{{color:var(--gold)}}.lead{{color:#d5cec4;margin:0 0 10px;max-width:580px}}.facts{{margin-top:24px;border:1px solid rgba(205,177,124,.65);border-radius:15px;overflow:hidden}}.fact{{display:grid;grid-template-columns:1fr 1.15fr 1fr;gap:10px;align-items:center;padding:9px 13px;border-bottom:1px solid #39352e;font-size:.92rem}}.fact:last-child{{border-bottom:0}}.fact strong{{font-size:.96rem}}.actions{{display:flex;flex-wrap:wrap;gap:9px;margin-top:20px}}.btn{{display:inline-flex;min-height:42px;align-items:center;justify-content:center;padding:9px 15px;border-radius:999px;text-decoration:none;border:1px solid var(--gold);background:transparent;color:var(--gold);font-weight:800;font-size:.86rem}}.btn.primary{{background:var(--ink);border-color:var(--ink);color:#101010}}.pdf-language-note{{flex-basis:100%;margin:2px 0 0;color:#d5cec4;font-size:.8rem}}.language-disclaimer{{margin:10px 0 0;color:var(--muted);font-size:.76rem;line-height:1.42}}.language-switch{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}.language-switch a{{display:inline-flex;align-items:center;justify-content:center;min-height:34px;padding:6px 10px;border:1px solid var(--line);border-radius:999px;color:var(--muted);text-decoration:none;font-size:.76rem;font-weight:800;letter-spacing:.04em}}.language-switch a.active{{color:var(--gold);border-color:var(--gold)}}.looks{{padding:20px 24px 24px;border-bottom:1px solid var(--line)}}.looks-head{{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:14px}}.looks h2{{font-family:Georgia,'Times New Roman',serif;font-weight:400;font-size:clamp(1.9rem,4vw,3rem);margin:0}}.photo-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.look{{margin:0}}.look img{{width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;display:block;border-radius:12px;border:1px solid #39352f}}.look span{{display:block;text-align:center;margin-top:8px;font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gold)}}.bottom{{display:grid;grid-template-columns:1fr 320px}}.contact-panel{{padding:24px;border-right:1px solid var(--line)}}.contact-panel h3{{font-family:Georgia,serif;font-weight:400;color:var(--gold);font-size:1.45rem;margin:0 0 8px}}.contact-panel p{{margin:5px 0;color:#d5cec4;font-size:.88rem}}.contact-panel a{{color:var(--gold);text-decoration:none}}.qr-panel{{padding:22px;display:flex;gap:16px;align-items:center;justify-content:center}}.qr-panel img{{width:118px;height:118px;object-fit:contain;background:#fff;padding:7px;border-radius:10px}}footer{{text-align:center;color:#746e66;font-size:.76rem;padding:0 0 40px}}html[dir="rtl"] .info,html[dir="rtl"] .contact-panel{{text-align:right}}@media(max-width:860px){{.top,.bottom{{grid-template-columns:1fr}}.headshot-wrap{{border-right:0;border-bottom:1px solid var(--line);padding:14px}}.headshot{{min-height:0;max-height:72vh}}.info{{padding:28px 20px}}.photo-grid{{grid-template-columns:repeat(2,1fr)}}.contact-panel{{border-right:0;border-bottom:1px solid var(--line)}}.qr-panel{{justify-content:flex-start}}}}@media(max-width:440px){{.card-shell{{width:calc(100% - 12px);margin-top:10px;border-radius:18px}}.wrap{{width:calc(100% - 18px)}}nav .brand{{display:none}}.fact{{grid-template-columns:.95fr 1fr .95fr;padding:8px 9px;font-size:.8rem}}.photo-grid{{gap:7px}}.looks{{padding:17px 12px}}.actions .btn{{flex:1 1 46%}}}}@media print{{.preview,nav,.language-switch,footer{{display:none!important}}.card-shell{{width:196mm;margin:0 auto;border-radius:0;box-shadow:none}}}}</style>
<style>.fact{{grid-template-columns:1fr 1.15fr}}.fact>span:last-child{{display:none}}</style><style>@page{{size:A4 portrait;margin:7mm}}@media print{{*{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}body{{zoom:.5}}.preview,nav,.language-switch,footer{{display:none!important}}.card-shell{{width:392mm;margin:0;border-radius:0;box-shadow:none}}.headshot-wrap{{padding:7mm}}.headshot{{min-height:112mm;max-height:112mm;border-radius:3mm}}.info{{padding:8mm 7mm 5mm}}h1{{font-size:34pt;margin:6mm 0 4mm}}.lead{{font-size:8.7pt;line-height:1.35}}.facts{{margin-top:5mm}}.fact{{font-size:7.7pt;padding:2.1mm 2.8mm}}.fact strong{{font-size:8pt}}.looks{{padding:4mm 6mm 5mm}}.looks h2{{font-size:19pt}}.look span{{font-size:5.7pt;margin-top:1.4mm}}.contact-panel{{padding:5mm 6mm}}.contact-panel h3{{font-size:12pt}}.contact-panel p{{font-size:7pt;line-height:1.3}}.qr-panel{{padding:4mm}}.qr-panel img{{width:27mm;height:27mm;padding:1.5mm}}}}</style>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"ProfilePage","url":"{ORIGIN}/casting-card/{code}","name":"Serdar Armin Sargut | {h(role)}","description":"{h(intro)}","inLanguage":"{code}","mainEntity":{{"@type":"Person","name":"Serdar Armin Sargut","jobTitle":["Child Actor","Child Model"],"height":{{"@type":"QuantitativeValue","value":162,"unitCode":"CMT"}},"url":"{ORIGIN}/","email":"info@serdararminsargut.com"}}}}</script>
</head><body><nav><div class="wrap"><a class="brand" href="/">SAS</a><a href="/">{h(words[1])}</a><a class="nav-current" aria-current="page" href="/casting-card/{code}">Comp Card</a></div></nav><div class="preview">TEST PREVIEW · NOINDEX · {h(notice)}</div>
<main class="card-shell"><section class="top"><div class="headshot-wrap"><img height="1536" width="1536" class="headshot" src="{PHOTO}" alt="Serdar Armin Sargut portfolio portrait" fetchpriority="high"></div><div class="info"><div class="eyebrow">{h(role)}</div><div class="location">{h(words[9])}</div><h1>Serdar Armin<br><span class="accent">Sargut</span></h1><p class="lead">{h(intro)}</p><div class="facts">{facts_html}</div><div class="actions"><a class="btn primary" href="../pdfs/{pdf_name}" download>{h(words[0])}</a><a class="btn" href="{ORIGIN}/">{h(words[1])}</a><p class="pdf-language-note">{h(notice)} · {code_upper}</p></div><p class="language-disclaimer">{h(language_note)}</p><div class="language-switch" aria-label="Comp Card languages">{lang_links}</div></div></section><section class="looks"><div class="looks-head"><div><div class="eyebrow">{h(words[2])}</div><h2>{h(words[2])}</h2></div><div>{h(label)}</div></div><div class="photo-grid">{looks_html}</div></section><section class="bottom"><div class="contact-panel"><div><h3>{h(words[7])}</h3><p><strong>{h(words[8])}</strong></p><p><strong>Email:</strong> <a href="mailto:info@serdararminsargut.com">info@serdararminsargut.com</a></p><p><strong>{h(words[1])}:</strong> <a href="{ORIGIN}/">serdararminsargut.com</a></p></div></div><div class="qr-panel"><img height="450" width="450" src="/assets/portfolio-qr.png" alt="QR code to official portfolio"></div></section></main><footer>Serdar Armin Sargut · {h(words[8])}</footer></body></html>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for code, data in L.items():
        (OUT / f"{code}.html").write_text(page(code, data), encoding="utf-8")
    print(f"SERDAR_26_CANDIDATE_BUILT {len(L)}/26")


if __name__ == "__main__":
    main()
