# -*- coding: utf-8 -*-
"""Общий шаблон для всех SEO-разделов alefbet.tech (slovar, dictionary, sleng, temy, alfavit, glagoly)."""
import html, json as _json, os, re

SITE = "https://alefbet.tech"
APP_URL = "https://apps.apple.com/app/alefbet-hebrew-dictionary/id6782951189"
APP_ID = "6782951189"
WORDS_JSON = os.path.join(os.path.dirname(__file__), "..", "HebrewTranslator", "Words.json")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio", "w")

POS_RU = {
    "noun": "существительное", "verb": "глагол", "adjective": "прилагательное",
    "adverb": "наречие", "pronoun": "местоимение", "preposition": "предлог",
    "conjunction": "союз", "interjection": "междометие", "numeral": "числительное",
    "particle": "частица", "phrase": "выражение", "other": "другое",
}

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}

def esc(s):
    return html.escape(s or "", quote=True)

def slugify(ru):
    s = (ru or "").lower().strip()
    s = "".join(TRANSLIT.get(ch, ch) for ch in s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if s == "index":
        s = "index-slovo"
    return s or "slovo"

def first_ru(ru):
    return re.split(r"[,;(]", ru or "")[0].strip()

def has_audio(word_id):
    return bool(word_id) and os.path.exists(os.path.join(AUDIO_DIR, f"{word_id}.m4a"))

def audio_button(word_id, root=".."):
    """Кнопка озвучки; root — путь от страницы до корня сайта."""
    if not has_audio(word_id):
        return ""
    return (f'<button class="play" type="button" aria-label="Слушать произношение" '
            f'onclick="pl(this,\'{root}/audio/w/{word_id}.m4a\')">'
            f'<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8 5.5v13l11-6.5z"/></svg>'
            f'</button>')

AUDIO_JS = """<script>
var _a;function pl(b,src){if(_a){_a.pause();}_a=new Audio(src);_a.play();
b.classList.add('playing');_a.onended=function(){b.classList.remove('playing');};}
</script>"""

APPLE_SVG = '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>'

def badge(lang="ru"):
    top = "Загрузите в" if lang == "ru" else "Download on the"
    return (f'<a class="as-badge" href="{APP_URL}">{APPLE_SVG}'
            f'<span class="as-badge-text"><span class="as-badge-top">{top}</span>'
            f'<span class="as-badge-bottom">App Store</span></span></a>')

def cta(lang="ru"):
    if lang == "ru":
        text = ("<strong>AlefBet</strong> — словарь иврита в вашем кармане: 11 000+ слов с огласовками, "
                "корни, спряжения глаголов и флешкарты. Работает офлайн.")
    else:
        text = ("<strong>AlefBet</strong> — the Hebrew dictionary in your pocket: 11,000+ words with nikkud, "
                "roots, verb conjugations and flashcards. Works offline.")
    return (f'<aside class="cta-band"><span class="cta-band-alef" aria-hidden="true">א</span>'
            f'<div class="cta-band-inner"><p>{text}</p>{badge(lang)}</div></aside>')

NAV_RU = [("/slovar/", "Словарь"), ("/temy/", "Темы"), ("/sleng/", "Сленг"),
          ("/alfavit/", "Алфавит"), ("/glagoly/", "Глаголы")]
NAV_EN = [("/dictionary/", "Dictionary"), ("/support.html", "Support")]

def shell(*, lang, title, desc, canonical, body, root="..", alternates="", jsonld=None, nav=None):
    """Каркас страницы. body — содержимое <main>, root — относительный путь к корню."""
    nav_items = nav if nav is not None else (NAV_RU if lang == "ru" else NAV_EN)
    nav_links = "".join(f'<li><a href="{root}{href}">{label}</a></li>' for href, label in nav_items)
    dl = "Скачать" if lang == "ru" else "Download"
    ld = ""
    if jsonld:
        blocks = jsonld if isinstance(jsonld, list) else [jsonld]
        ld = "".join(f'<script type="application/ld+json">{_json.dumps(b, ensure_ascii=False)}</script>'
                     for b in blocks)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc)}">
    <meta name="apple-itunes-app" content="app-id={APP_ID}">
    <link rel="canonical" href="{canonical}">{alternates}
    <link rel="icon" type="image/png" href="{root}/logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700&family=Noto+Sans+Hebrew:wght@300;400&display=swap">
    <link rel="stylesheet" href="{root}/styles.css">
    <link rel="stylesheet" href="{root}/site.css">{ld}
</head>
<body>

<nav>
    <div class="nav-inner">
        <a href="{root}/index.html" class="logo">
            <img class="logo-icon" src="{root}/logo.png" alt="AlefBet logo" width="38" height="38">
            <span class="logo-text">AlefBet</span>
        </a>
        <ul class="nav-links">{nav_links}</ul>
        <a href="{APP_URL}" class="btn-nav-dl">{dl}</a>
    </div>
</nav>

<main class="sl-main">
{body}
</main>

<footer>
    <div class="footer-inner">
        <span class="footer-copy">&copy; 2026 Ilia Liubimov. All rights reserved.</span>
        <ul class="footer-links">
            <li><a href="{root}/slovar/">Словарь</a></li>
            <li><a href="{root}/temy/">Темы</a></li>
            <li><a href="{root}/sleng/">Сленг</a></li>
            <li><a href="{root}/alfavit/">Алфавит</a></li>
            <li><a href="{root}/glagoly/">Глаголы</a></li>
            <li><a href="{root}/dictionary/">Dictionary</a></li>
            <li><a href="{root}/privacy.html">Privacy</a></li>
            <li><a href="{root}/terms.html">Terms</a></li>
            <li><a href="{root}/support.html">Support</a></li>
        </ul>
    </div>
</footer>
{AUDIO_JS}
</body>
</html>"""

def breadcrumb_ld(items):
    """items: [(name, url|None)] — последний без url."""
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name,
             **({"item": url} if url else {})}
            for i, (name, url) in enumerate(items)
        ],
    }

def faq_ld(pairs):
    """pairs: [(вопрос, ответ)]"""
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ],
    }

def word_card(*, he, main, tr, sub="", chips=(), root_chip="", word_id=None, site_root=".."):
    """Фирменная карточка-флешкарта с призрачной буквой и озвучкой."""
    ghost = next((ch for ch in (he or "") if "א" <= ch <= "ת"), "א")
    chips_html = "".join(f'<span class="sl-chip">{esc(c)}</span>' for c in chips if c)
    sub_html = f'<div class="sl-en">{esc(sub)}</div>' if sub else ""
    root_html = ""
    if root_chip:
        root_html = (f'<div class="sl-root"><span class="sl-root-label">Корень · שורש</span>'
                     f'<span lang="he" dir="rtl">{esc(root_chip)}</span></div>')
    return f"""<div class="sl-card">
        <span class="sl-ghost" aria-hidden="true">{ghost}</span>
        <div class="sl-chips">{chips_html}</div>
        <div class="sl-he-row"><span class="sl-he" lang="he" dir="rtl">{esc(he)}</span>{audio_button(word_id, site_root)}</div>
        <div class="sl-ru">{esc(main)}</div>
        <div class="sl-tr">{esc(tr)}</div>{sub_html}{root_html}
      </div>"""
