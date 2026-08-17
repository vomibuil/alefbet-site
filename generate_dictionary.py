# -*- coding: utf-8 -*-
"""Генератор английских SEO-страниц словаря для alefbet.tech (США-аудитория).

Зеркало /slovar/ на английском («how to say X in Hebrew»):
  dictionary/<slug>.html — страница на слово
  dictionary/index.html  — каталог по алфавиту

Слова и слаги берутся из generate_slovar.build_entries — пары ru↔en стабильны,
hreflang с обеих сторон ссылается на одни и те же файлы. Sitemap пишет
generate_slovar.py (включает оба раздела).

Запуск:  python3 generate_dictionary.py [--levels A1]
Порядок: оба генератора независимы, но после изменения Words.json запускать оба.
"""
import argparse, hashlib, json, os, re, unicodedata

from generate_slovar import (
    APP_URL, SITE, TRANSLIT, WORDS_JSON,
    build_en_slugs, build_entries, esc, first_en,
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "dictionary")

def pron(tr):
    """Кириллическая транскрипция → латиница для англоязычных: «аба́» → "aba"."""
    s = unicodedata.normalize("NFD", (tr or "").lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return "".join(TRANSLIT.get(ch, ch) for ch in s)

def page(word, slug, related, ru_slug):
    en_short = first_en(word["en"])
    he = word["he"]
    tr = pron(word.get("transcription"))
    pos = word.get("pos") or ""
    level = word.get("level") or ""
    title = f"{en_short.capitalize()} in Hebrew — {he} ({tr}) | AlefBet"
    desc = (f'How to say "{en_short}" in Hebrew: {he}, pronounced "{tr}", '
            f"{pos}, with example sentences. AlefBet — offline Hebrew dictionary with 11,000+ words.")

    root_block = ""
    if word.get("shoresh"):
        root_block = f"""
      <div class="sl-root"><span class="sl-root-label">Root · שורש</span>
        <span lang="he" dir="rtl">{esc(word["shoresh"])}</span></div>"""

    verb_block = ""
    if word.get("pos") == "verb" and (word.get("past") or word.get("present") or word.get("future")):
        cells = ""
        for label, key in (("Past", "past"), ("Present", "present"), ("Future", "future")):
            if word.get(key):
                cells += f"""<div class="sl-tense"><span class="sl-tense-label">{label}</span>
                <span lang="he" dir="rtl">{esc(word[key])}</span></div>"""
        binyan = f'<p class="sl-binyan">Binyan: {esc(word["binyan"])}</p>' if word.get("binyan") else ""
        verb_block = f"""
      <h2>Verb forms</h2>{binyan}
      <div class="sl-tenses">{cells}</div>"""

    ex_block = ""
    if word.get("examples"):
        items = ""
        for ex in word["examples"][:3]:
            items += f"""<div class="sl-example">
          <p lang="he" dir="rtl" class="sl-example-he">{esc(ex.get("he"))}</p>
          <p class="sl-example-ru">{esc(ex.get("en"))}</p></div>"""
        ex_block = f"""
      <h2>Examples</h2>{items}"""

    rel_block = ""
    if related:
        links = "".join(f'<li><a href="{r_slug}.html">{esc(first_en(r["en"]))} — <span lang="he" dir="rtl">{esc(r["he"])}</span></a></li>'
                        for r_slug, r in related)
        rel_block = f"""
      <h2>More {esc(level)} words</h2>
      <ul class="sl-related">{links}</ul>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc)}">
    <link rel="canonical" href="{SITE}/dictionary/{slug}.html">
    <link rel="alternate" hreflang="en" href="{SITE}/dictionary/{slug}.html">
    <link rel="alternate" hreflang="ru" href="{SITE}/slovar/{ru_slug}.html">
    <link rel="alternate" hreflang="x-default" href="{SITE}/dictionary/{slug}.html">
    <link rel="icon" type="image/png" href="../logo.png">
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="../slovar/slovar.css">
</head>
<body>

<nav class="nav-dark">
    <div class="nav-inner">
        <a href="../index.html" class="logo">
            <img class="logo-icon" src="../logo.png" alt="AlefBet logo" width="38" height="38">
            <span class="logo-text">AlefBet</span>
        </a>
        <ul class="nav-links">
            <li><a href="index.html">Dictionary</a></li>
            <li><a href="../support.html">Support</a></li>
        </ul>
        <a href="{APP_URL}" class="btn btn-white-sm">Download</a>
    </div>
</nav>

<main class="sl-main">
    <article>
      <p class="sl-breadcrumb"><a href="index.html">Hebrew dictionary</a> → {esc(en_short)}</p>
      <h1>How to say &ldquo;{esc(en_short)}&rdquo; in Hebrew</h1>
      <div class="sl-card">
        <div class="sl-chips"><span class="sl-chip">{esc(pos)}</span><span class="sl-chip">{esc(level)}</span></div>
        <div class="sl-he" lang="he" dir="rtl">{esc(he)}</div>
        <div class="sl-ru">{esc(word["en"])}</div>
        <div class="sl-tr">{esc(tr)}</div>{root_block}
      </div>{verb_block}{ex_block}

      <aside class="sl-cta">
        <p><strong>AlefBet</strong> — Hebrew dictionary with vowel marks (nikkud), verb conjugations and flashcards. 11,000+ words, works offline.</p>
        <a href="{APP_URL}" class="btn btn-primary">Download on the App Store</a>
      </aside>{rel_block}
    </article>
</main>

<footer>
    <div class="footer-inner">
        <span class="footer-copy">&copy; 2025 Ilia Liubimov. All rights reserved.</span>
        <ul class="footer-links">
            <li><a href="index.html">Dictionary</a></li>
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
        letter = (first_en(w["en"])[:1] or "#").upper()
        by_letter.setdefault(letter, []).append((slug, w))
    sections = ""
    for letter in sorted(by_letter):
        links = "".join(
            f'<li><a href="{slug}.html">{esc(first_en(w["en"]))} — <span lang="he" dir="rtl">{esc(w["he"])}</span></a></li>'
            for slug, w in sorted(by_letter[letter], key=lambda p: first_en(p[1]["en"]).lower()))
        sections += f'<h2 id="{esc(letter)}">{esc(letter)}</h2><ul class="sl-index-list">{links}</ul>'
    nav_letters = "".join(f'<a href="#{esc(l)}">{esc(l)}</a> ' for l in sorted(by_letter))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hebrew–English Dictionary Online — {len(entries)} words with pronunciation | AlefBet</title>
    <meta name="description" content="How to say it in Hebrew: {len(entries)} essential Hebrew words with vowel marks, pronunciation and example sentences. Free online Hebrew dictionary by AlefBet.">
    <link rel="canonical" href="{SITE}/dictionary/">
    <link rel="alternate" hreflang="en" href="{SITE}/dictionary/">
    <link rel="alternate" hreflang="ru" href="{SITE}/slovar/">
    <link rel="alternate" hreflang="x-default" href="{SITE}/dictionary/">
    <link rel="icon" type="image/png" href="../logo.png">
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="../slovar/slovar.css">
</head>
<body>
<nav class="nav-dark">
    <div class="nav-inner">
        <a href="../index.html" class="logo">
            <img class="logo-icon" src="../logo.png" alt="AlefBet logo" width="38" height="38">
            <span class="logo-text">AlefBet</span>
        </a>
        <ul class="nav-links">
            <li><a href="../support.html">Support</a></li>
        </ul>
        <a href="{APP_URL}" class="btn btn-white-sm">Download</a>
    </div>
</nav>
<main class="sl-main">
    <h1>Hebrew–English Dictionary</h1>
    <p>Essential Hebrew words with vowel marks (nikkud), pronunciation and example sentences. The full dictionary — 11,000+ words — is in the <a href="{APP_URL}">AlefBet app</a>.</p>
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
    entries = build_entries(words, levels)
    en_slugs = build_en_slugs(entries)
    # (en_slug, word) + обратная связь на ru-слаг для hreflang
    en_entries = [(en_slugs[ru_slug], w) for ru_slug, w in entries]
    ru_by_en = {en_slugs[ru_slug]: ru_slug for ru_slug, _ in entries}

    if os.path.isdir(OUT_DIR):
        for f in os.listdir(OUT_DIR):
            if f.endswith(".html"):
                os.remove(os.path.join(OUT_DIR, f))
    os.makedirs(OUT_DIR, exist_ok=True)

    # связанные слова: детерминированный выбор по хэшу слага (как в /slovar/)
    def pick_related(slug, level):
        pool = [(s, w) for s, w in en_entries if w.get("level") == level and s != slug]
        if not pool:
            return []
        h = int(hashlib.md5(slug.encode()).hexdigest(), 16)
        step = max(1, len(pool) // 6)
        return [pool[(h + i * step) % len(pool)] for i in range(min(6, len(pool)))]

    for slug, w in en_entries:
        with open(os.path.join(OUT_DIR, f"{slug}.html"), "w") as f:
            f.write(page(w, slug, pick_related(slug, w.get("level")), ru_by_en[slug]))

    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(index_page(en_entries))

    print(f"generated {len(en_entries)} word pages + index in dictionary/")

if __name__ == "__main__":
    main()
