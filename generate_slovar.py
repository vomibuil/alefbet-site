# -*- coding: utf-8 -*-
"""Генератор SEO-страниц словаря для alefbet.tech.

Читает ../HebrewTranslator/Words.json и создаёт:
  slovar/<slug>.html   — страница на слово («как на иврите ...»)
  slovar/index.html    — каталог слов по алфавиту
  sitemap.xml          — карта сайта (основные страницы + словарь)

Запуск:  python3 generate_slovar.py [--levels A1,A2,B1]
"""
import json, os, re, html, hashlib, argparse, shutil

SITE = "https://alefbet.tech"
APP_URL = "https://apps.apple.com/app/alefbet-hebrew-dictionary/id6782951189"
WORDS_JSON = os.path.join(os.path.dirname(__file__), "..", "HebrewTranslator", "Words.json")
OUT_DIR = os.path.join(os.path.dirname(__file__), "slovar")

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

def slugify(ru):
    s = ru.lower().strip()
    s = "".join(TRANSLIT.get(ch, ch) for ch in s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "slovo"

def esc(s):
    return html.escape(s or "", quote=True)

def first_ru(ru):
    # первое значение до запятой/точки с запятой — для заголовков
    return re.split(r"[,;(]", ru)[0].strip()

def page(word, slug, related):
    ru_short = first_ru(word["ru"])
    he = word["he"]
    tr = word.get("transcription") or ""
    pos_ru = POS_RU.get(word.get("pos") or "", word.get("pos") or "")
    level = word.get("level") or ""
    title = f"«{ru_short.capitalize()}» на иврите — {he} ({tr}) | AlefBet"
    desc = (f"Как будет «{ru_short}» на иврите: {he}, транскрипция «{tr}», "
            f"{pos_ru}, примеры употребления с переводом. Словарь AlefBet — 11 000+ слов иврита офлайн.")

    root_block = ""
    if word.get("shoresh"):
        root_block = f"""
      <div class="sl-root"><span class="sl-root-label">Корень · שורש</span>
        <span lang="he" dir="rtl">{esc(word["shoresh"])}</span></div>"""

    verb_block = ""
    if word.get("pos") == "verb" and (word.get("past") or word.get("present") or word.get("future")):
        cells = ""
        for label, key in (("Прошедшее", "past"), ("Настоящее", "present"), ("Будущее", "future")):
            if word.get(key):
                cells += f"""<div class="sl-tense"><span class="sl-tense-label">{label}</span>
                <span lang="he" dir="rtl">{esc(word[key])}</span></div>"""
        binyan = f'<p class="sl-binyan">Биньян: {esc(word["binyan"])}</p>' if word.get("binyan") else ""
        verb_block = f"""
      <h2>Формы глагола</h2>{binyan}
      <div class="sl-tenses">{cells}</div>"""

    ex_block = ""
    if word.get("examples"):
        items = ""
        for ex in word["examples"][:3]:
            items += f"""<div class="sl-example">
          <p lang="he" dir="rtl" class="sl-example-he">{esc(ex.get("he"))}</p>
          <p class="sl-example-ru">{esc(ex.get("ru"))}</p></div>"""
        ex_block = f"""
      <h2>Примеры</h2>{items}"""

    rel_block = ""
    if related:
        links = "".join(f'<li><a href="{r_slug}.html">{esc(first_ru(r["ru"]))} — <span lang="he" dir="rtl">{esc(r["he"])}</span></a></li>'
                        for r_slug, r in related)
        rel_block = f"""
      <h2>Другие слова уровня {esc(level)}</h2>
      <ul class="sl-related">{links}</ul>"""

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc)}">
    <link rel="canonical" href="{SITE}/slovar/{slug}.html">
    <link rel="icon" type="image/png" href="../logo.png">
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="slovar.css">
</head>
<body>

<nav class="nav-dark">
    <div class="nav-inner">
        <a href="../index.html" class="logo">
            <img class="logo-icon" src="../logo.png" alt="AlefBet logo" width="38" height="38">
            <span class="logo-text">AlefBet</span>
        </a>
        <ul class="nav-links">
            <li><a href="index.html">Словарь</a></li>
            <li><a href="../support.html">Поддержка</a></li>
        </ul>
        <a href="{APP_URL}" class="btn btn-white-sm">Скачать</a>
    </div>
</nav>

<main class="sl-main">
    <article>
      <p class="sl-breadcrumb"><a href="index.html">Словарь иврита</a> → {esc(ru_short)}</p>
      <h1>Как будет «{esc(ru_short)}» на иврите</h1>
      <div class="sl-card">
        <div class="sl-chips"><span class="sl-chip">{esc(pos_ru)}</span><span class="sl-chip">{esc(level)}</span></div>
        <div class="sl-he" lang="he" dir="rtl">{esc(he)}</div>
        <div class="sl-ru">{esc(word["ru"])}</div>
        <div class="sl-tr">{esc(tr)}</div>
        <div class="sl-en">англ.: {esc(word.get("en"))}</div>{root_block}
      </div>{verb_block}{ex_block}

      <aside class="sl-cta">
        <p><strong>AlefBet</strong> — словарь иврита с огласовками, формами глаголов и карточками. 11 000+ слов, работает офлайн.</p>
        <a href="{APP_URL}" class="btn btn-primary">Скачать в App Store</a>
      </aside>{rel_block}
    </article>
</main>

<footer>
    <div class="footer-inner">
        <span class="footer-copy">&copy; 2025 Ilia Liubimov. All rights reserved.</span>
        <ul class="footer-links">
            <li><a href="index.html">Словарь</a></li>
            <li><a href="../privacy.html">Privacy</a></li>
            <li><a href="../terms.html">Terms</a></li>
        </ul>
    </div>
</footer>

</body>
</html>"""

def index_page(entries):
    by_letter = {}
    for slug, w in entries:
        letter = first_ru(w["ru"])[:1].upper() or "#"
        by_letter.setdefault(letter, []).append((slug, w))
    sections = ""
    for letter in sorted(by_letter):
        links = "".join(
            f'<li><a href="{slug}.html">{esc(first_ru(w["ru"]))} — <span lang="he" dir="rtl">{esc(w["he"])}</span></a></li>'
            for slug, w in sorted(by_letter[letter], key=lambda p: first_ru(p[1]["ru"]).lower()))
        sections += f'<h2 id="{esc(letter)}">{esc(letter)}</h2><ul class="sl-index-list">{links}</ul>'
    nav_letters = "".join(f'<a href="#{esc(l)}">{esc(l)}</a> ' for l in sorted(by_letter))
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Русско-ивритский словарь онлайн — {len(entries)} слов с транскрипцией | AlefBet</title>
    <meta name="description" content="Как будет по-иврите: {len(entries)} частотных слов с огласовками, транскрипцией и примерами. Бесплатный онлайн-словарь иврита AlefBet.">
    <link rel="canonical" href="{SITE}/slovar/">
    <link rel="icon" type="image/png" href="../logo.png">
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="slovar.css">
</head>
<body>
<nav class="nav-dark">
    <div class="nav-inner">
        <a href="../index.html" class="logo">
            <img class="logo-icon" src="../logo.png" alt="AlefBet logo" width="38" height="38">
            <span class="logo-text">AlefBet</span>
        </a>
        <ul class="nav-links">
            <li><a href="../support.html">Поддержка</a></li>
        </ul>
        <a href="{APP_URL}" class="btn btn-white-sm">Скачать</a>
    </div>
</nav>
<main class="sl-main">
    <h1>Русско-ивритский словарь</h1>
    <p>Частотные слова иврита с огласовками (никуд), транскрипцией и примерами. Полная версия — {'{:,}'.format(11000).replace(',', ' ')}+ слов — в приложении <a href="{APP_URL}">AlefBet</a>.</p>
    <p class="sl-letters">{nav_letters}</p>
    {sections}
</main>
<footer>
    <div class="footer-inner">
        <span class="footer-copy">&copy; 2025 Ilia Liubimov. All rights reserved.</span>
        <ul class="footer-links">
            <li><a href="../privacy.html">Privacy</a></li>
            <li><a href="../terms.html">Terms</a></li>
            <li><a href="../support.html">Support</a></li>
        </ul>
    </div>
</footer>
</body>
</html>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="A1")
    args = ap.parse_args()
    levels = set(args.levels.split(","))

    words = json.load(open(WORDS_JSON))
    core = [w for w in words if w.get("level") in levels and w.get("ru") and w.get("he")]

    # стабильные слаги с разрешением коллизий
    entries, used = [], {}
    for w in sorted(core, key=lambda x: (x.get("level"), first_ru(x["ru"]).lower())):
        base = slugify(first_ru(w["ru"]))
        slug = base
        n = used.get(base, 0)
        if n:
            slug = f"{base}-{n + 1}"
        used[base] = n + 1
        entries.append((slug, w))

    if os.path.isdir(OUT_DIR):
        for f in os.listdir(OUT_DIR):
            if f.endswith(".html"):
                os.remove(os.path.join(OUT_DIR, f))
    os.makedirs(OUT_DIR, exist_ok=True)

    # связанные слова: детерминированный выбор по хэшу слага
    def pick_related(slug, level):
        pool = [(s, w) for s, w in entries if w.get("level") == level and s != slug]
        if not pool:
            return []
        h = int(hashlib.md5(slug.encode()).hexdigest(), 16)
        step = max(1, len(pool) // 6)
        return [pool[(h + i * step) % len(pool)] for i in range(min(6, len(pool)))]

    for slug, w in entries:
        with open(os.path.join(OUT_DIR, f"{slug}.html"), "w") as f:
            f.write(page(w, slug, pick_related(slug, w.get("level"))))

    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(index_page(entries))

    # sitemap
    static_pages = ["", "support.html", "privacy.html", "terms.html", "slovar/"]
    urls = [f"{SITE}/{p}" for p in static_pages] + [f"{SITE}/slovar/{s}.html" for s, _ in entries]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc></url>" for u in urls]
    sm.append("</urlset>")
    with open(os.path.join(os.path.dirname(__file__), "sitemap.xml"), "w") as f:
        f.write("\n".join(sm))

    print(f"generated {len(entries)} word pages, index, sitemap ({len(urls)} urls)")

if __name__ == "__main__":
    main()
