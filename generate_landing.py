# -*- coding: utf-8 -*-
"""Лендинг alefbet.tech «Полночь» (1.6): RU в корне (index.html), EN — en/index.html.
Один шаблон + строки STR. Стили — landing.css. Запуск: python3 generate_landing.py
"""
import os
from gen_common import SITE, APP_ID, APPLE_SVG, app_url, esc

HERE = os.path.dirname(os.path.abspath(__file__))

STR = {
    "ru": {
        "title": "AlefBet — словарь иврита с огласовками, корнями и озвучкой",
        "desc": "12 747 слов с огласовками и транскрипцией, все формы глаголов, корни, 13 тем и карточки. "
                "Ищи слово в любой форме. Бесплатно для iPhone, работает офлайн.",
        "og": "img/v16/og_ru.png", "ct": "site_ru",
        "meta": "12 747 слов · 13 тем · v1.6",
        "h1": "Словарь иврита,<br><em>который понятен</em>",
        "lead": "Огласовки, корни, все формы глаголов и озвучка. Для тех, кто учит иврит в Израиле — и не только.",
        "btn": "Скачать в App Store", "sub": "бесплатно · iPhone · работает офлайн",
        "s1l": "01 · Поиск по любой форме", "s1h": "Вводи как слышишь —<br><em>найдём начальную форму</em>",
        "s1p": "Набери глагол в любом времени и лице — приложение покажет инфинитив и подпишет, что это за форма.",
        "s1t": ["прош. время · я", "идти, ходить"],
        "s2l": "02 · Каждое слово целиком", "s2h": "Корень, биньян,<br><em>все времена</em>",
        "s2p": "Огласовки, транскрипция с ударением, примеры и однокоренные слова. Переводы на русский и английский.",
        "s3l": "03 · Учёба", "s3h": "10 карточек в день —<br><em>и стрик растёт</em>",
        "minis": [("13", "тем: ульпан, работа, армия, сленг…"), ("🔥 12", "дней подряд — сколько у тебя?"),
                  ("A1–C2", "уровни как в ульпане"), ("0 ₪", "базовые слова и 5 тем бесплатно")],
        "hl": "Сезон · 4–12 декабря", "hh": "🕎 Ханука на иврите",
        "hp": "28 слов к празднику с озвучкой — סביבון, סופגנייה, נס גדול היה פה. Бесплатно.",
        "hmore": "Слова Хануки →", "hhref": "temy/hanuka-na-ivrite.html",
        "fh": "Начни с первых<br><em>пяти слов</em>",
        "fp": "Выбери цель — алия, работа, армия — и приложение подберёт темы.",
        "foot": [("slovar/", "Словарь"), ("glagoly/", "Глаголы"), ("sleng/", "Сленг"), ("temy/", "Темы"),
                 ("alfavit/", "Алфавит"), ("support.html", "Поддержка"), ("privacy.html", "Конфиденциальность"),
                 ("terms.html", "Условия")],
        "img": "Скриншот приложения AlefBet: ",
    },
    "en": {
        "title": "AlefBet — Hebrew dictionary with nikud, roots and audio",
        "desc": "12,747 words with nikud and transliteration, every verb form, roots, 13 topics and flashcards. "
                "Search any form of a word. Free for iPhone, works offline.",
        "og": "img/v16/og_en.png", "ct": "site_en",
        "meta": "12,747 words · 13 topics · v1.6",
        "h1": "The Hebrew dictionary<br><em>you actually understand</em>",
        "lead": "Nikud, roots, every verb form and audio. Built for people learning Hebrew in Israel — and everywhere else.",
        "btn": "Download on the App Store", "sub": "free · iPhone · works offline",
        "s1l": "01 · Search any form", "s1h": "Type it the way you hear it —<br><em>we find the base form</em>",
        "s1p": "Enter a verb in any tense or person — the app shows the infinitive and tells you which form it is.",
        "s1t": ["past · I", "to go, to walk"],
        "s2l": "02 · Every word, in full", "s2h": "Root, binyan,<br><em>every tense</em>",
        "s2p": "Nikud, stress-marked transliteration, examples and words from the same root. Translations in English and Russian.",
        "s3l": "03 · Study", "s3h": "10 cards a day —<br><em>grow your streak</em>",
        "minis": [("13", "topics: ulpan, work, army, slang…"), ("🔥 12", "days in a row — what’s yours?"),
                  ("A1–C2", "levels like in ulpan"), ("Free", "core words and 5 topics")],
        "hl": "Season · Dec 4–12", "hh": "🕎 Hanukkah in Hebrew",
        "hp": "28 holiday words with audio — סביבון, סופגנייה, נס גדול היה פה. Free.",
        "hmore": "Hanukkah words →", "hhref": "hanukkah-in-hebrew.html",
        "fh": "Start with your<br><em>first five words</em>",
        "fp": "Pick a goal — aliyah, work, army — and the app picks your topics.",
        "foot": [("../dictionary/", "Dictionary"), ("../slovar/", "Словарь"), ("../glagoly/", "Verbs (RU)"),
                 ("../support.html", "Support"), ("../privacy.html", "Privacy"), ("../terms.html", "Terms")],
        "img": "AlefBet app screenshot: ",
    },
}


def he(word):
    return f'<bdi class="he" lang="he" dir="rtl">{word}</bdi>'


def he_inline(text):
    """Иврит внутри русского/английского текста: подряд идущие ивритские слова — одним
    изолированным блоком (иначе bidi переворачивает фразу), запятая/точка закрывают блок."""
    out, run = [], []

    def flush():
        if run:
            out.append(he(" ".join(run)))
            run.clear()

    for tok in text.split(" "):
        word = tok.rstrip(",.")
        if any("\u05d0" <= c <= "\u05ea" for c in word):
            run.append(word)
            if word != tok:            # пунктуация после слова — конец фразы
                flush()
                out[-1] += tok[len(word):]
        else:
            flush()
            out.append(tok)
    flush()
    return " ".join(out)


def img(src, alt, *, lazy, cls=""):
    lz = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{src}" alt="{esc(alt)}" width="600" height="1304"{lz}>'


def page(lang):
    s = STR[lang]
    r = "" if lang == "ru" else "../"            # путь к корню сайта
    canon = f"{SITE}/" if lang == "ru" else f"{SITE}/en/"
    store = app_url(s["ct"])
    sw = ('<b>RU</b> · <a href="en/index.html" hreflang="en">EN</a>' if lang == "ru"
          else '<a href="../index.html" hreflang="ru">RU</a> · <b>EN</b>')
    minis = "".join(f'<div class="mini"><b>{b}</b><span>{esc(t)}</span></div>' for b, t in s["minis"])
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in s["s1t"])
    foot = "".join(f'<li><a href="{h}">{esc(t)}</a></li>' for h, t in s["foot"])
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(s["title"])}</title>
<meta name="description" content="{esc(s["desc"])}">
<meta name="theme-color" content="#0B0A14">
<meta name="apple-itunes-app" content="app-id={APP_ID}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="ru" href="{SITE}/">
<link rel="alternate" hreflang="en" href="{SITE}/en/">
<link rel="alternate" hreflang="x-default" href="{SITE}/">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(s["title"])}">
<meta property="og:description" content="{esc(s["desc"])}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/{s["og"]}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="{r}logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=JetBrains+Mono:wght@500&family=Noto+Sans+Hebrew:wght@400;600&display=swap">
<link rel="stylesheet" href="{r}landing.css">
</head>
<body>
<header class="nav"><a class="logo" href="{r if r else './'}"><i aria-hidden="true">א</i>AlefBet</a><nav class="lang" aria-label="Language">{sw}</nav></header>
<main>
<section class="sec hero"><span class="hud tl"></span><span class="hud br"></span><div class="wrap hero-grid">
  <div>
    <div class="meta"><span class="dot"></span>{esc(s["meta"])}</div>
    <h1>{s["h1"]}</h1>
    <p>{esc(s["lead"])}</p>
    <a class="btn" href="{store}">{APPLE_SVG}{esc(s["btn"])}</a>
    <div class="sub">{esc(s["sub"])}</div>
  </div>
  <div class="phones">
    <div class="ph l">{img(f"{r}img/v16/{lang}_word.webp", s["img"] + "word card", lazy=False)}</div>
    <div class="ph r">{img(f"{r}img/v16/{lang}_studydark.webp", s["img"] + "study", lazy=False)}</div>
  </div>
</div></section>

<section class="sec"><div class="wrap split">
  <div class="text">
    <div class="label">{esc(s["s1l"])}</div>
    <h2>{s["s1h"]}</h2>
    <p>{esc(s["s1p"])}</p>
    <div class="card"><div class="form-row">{he("הָלַכְתִּי")}<span class="arrow" aria-hidden="true">→</span>{he("לָלֶכֶת")}</div>
      <div class="tags">{tags}</div></div>
  </div>
  {img(f"{r}img/v16/{lang}_search.webp", s["img"] + "search", lazy=True, cls="shot")}
</div></section>

<section class="sec"><div class="wrap split rev">
  <div class="text">
    <div class="label">{esc(s["s2l"])}</div>
    <h2>{s["s2h"]}</h2>
    <p>{esc(s["s2p"])}</p>
  </div>
  {img(f"{r}img/v16/{lang}_word.webp", s["img"] + "word", lazy=True, cls="shot")}
</div></section>

<section class="sec"><div class="wrap">
  <div class="label">{esc(s["s3l"])}</div>
  <h2>{s["s3h"]}</h2>
  <div class="grid">{minis}</div>
</div></section>

<section class="sec"><div class="wrap">
  <a class="hanuka" href="{s["hhref"]}">
    <div class="label">{esc(s["hl"])}</div>
    <h2>{esc(s["hh"])}</h2>
    <p>{he_inline(esc(s["hp"]))}</p>
    <span class="more">{esc(s["hmore"])}</span>
  </a>
</div></section>

<section class="sec final"><div class="wrap">
  <h2>{s["fh"]}</h2>
  <p>{esc(s["fp"])}</p>
  <a class="btn" href="{store}">{APPLE_SVG}{esc(s["btn"])}</a>
</div></section>
</main>
<footer class="foot"><div class="wrap"><ul>{foot}</ul>&copy; 2026 AlefBet</div></footer>
</body>
</html>
"""


def generate():
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page("ru"))
    os.makedirs(os.path.join(HERE, "en"), exist_ok=True)
    with open(os.path.join(HERE, "en", "index.html"), "w", encoding="utf-8") as f:
        f.write(page("en"))
    print("landing: index.html + en/index.html")


if __name__ == "__main__":
    generate()
