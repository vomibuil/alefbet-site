# -*- coding: utf-8 -*-
"""Генератор SEO-страниц словаря для alefbet.tech.

Читает ../HebrewTranslator/Words.json и создаёт:
  slovar/<slug>.html   — страница на слово («как на иврите ...»)
  slovar/index.html    — каталог слов по алфавиту + ссылки на разделы

Запуск:  python3 generate_slovar.py [--levels A1]  (sitemap собирает build.py)
"""
import json, os, hashlib, argparse
from gen_common import (SITE, APP_URL, WORDS_JSON, POS_RU, esc, slugify, first_ru,
                        shell, word_card, cta, breadcrumb_ld, faq_ld, audio_button)
import re

OUT_DIR = os.path.join(os.path.dirname(__file__), "slovar")

def first_en(en):
    return re.split(r"[,;(]", en or "")[0].strip()

def slugify_en(en):
    s = first_en(en).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if s == "index":
        s = "index-word"
    return s or "word"

def build_entries(words, levels):
    """(slug, word) со стабильными слагами — общая база для /slovar/ и /dictionary/."""
    core = [w for w in words if w.get("level") in levels and w.get("ru") and w.get("he")]
    entries, used = [], {}
    for w in sorted(core, key=lambda x: (x.get("level"), first_ru(x["ru"]).lower())):
        base = slugify(first_ru(w["ru"]))
        slug = base
        n = used.get(base, 0)
        if n:
            slug = f"{base}-{n + 1}"
        used[base] = n + 1
        entries.append((slug, w))
    return entries

def build_en_slugs(entries):
    used, out = {}, {}
    for ru_slug, w in entries:
        base = slugify_en(w.get("en") or "")
        n = used.get(base, 0)
        out[ru_slug] = f"{base}-{n + 1}" if n else base
        used[base] = n + 1
    return out

def page(word, slug, related, en_slug, root_family, verb_slug):
    ru_short = first_ru(word["ru"])
    he = word["he"]
    tr = word.get("transcription") or ""
    pos_ru = POS_RU.get(word.get("pos") or "", word.get("pos") or "")
    level = word.get("level") or ""
    title = f"«{ru_short.capitalize()}» на иврите — {he} ({tr}) | AlefBet"
    desc = (f"Как будет «{ru_short}» на иврите: {he}, транскрипция «{tr}», "
            f"{pos_ru}, примеры употребления с переводом. Словарь AlefBet — 11 000+ слов иврита офлайн.")

    card = word_card(he=he, main=word["ru"], tr=tr, sub=f'англ.: {word.get("en") or ""}',
                     chips=(pos_ru, level), root_chip=word.get("shoresh") or "",
                     word_id=word.get("id"))

    verb_block = ""
    if word.get("pos") == "verb" and (word.get("past") or word.get("present") or word.get("future")):
        cells = ""
        for label, key in (("Прошедшее", "past"), ("Настоящее", "present"), ("Будущее", "future")):
            if word.get(key):
                cells += f"""<div class="sl-tense"><span class="sl-tense-label">{label}</span>
                <span lang="he" dir="rtl">{esc(word[key])}</span></div>"""
        binyan = f'<p class="sl-binyan">Биньян: <b>{esc(word["binyan"])}</b></p>' if word.get("binyan") else ""
        more = (f'<p class="sl-note"><a href="../glagoly/{verb_slug}.html">Спряжение глагола «{esc(ru_short)}» подробнее →</a></p>'
                if verb_slug else "")
        verb_block = f"""
      <h2>Формы глагола</h2>{binyan}
      <div class="sl-tenses">{cells}</div>{more}"""

    ex_block = ""
    if word.get("examples"):
        items = ""
        for ex in word["examples"][:3]:
            items += f"""<div class="sl-example">
          <p lang="he" dir="rtl" class="sl-example-he">{esc(ex.get("he"))}</p>
          <p class="sl-example-ru">{esc(ex.get("ru"))}</p></div>"""
        ex_block = f"""
      <h2>Примеры употребления</h2>{items}"""

    fam_block = ""
    if root_family:
        links = "".join(
            f'<li><a href="{href}">{esc(first_ru(r["ru"]))} <span lang="he" dir="rtl">{esc(r["he"])}</span></a></li>'
            for href, r in root_family)
        fam_block = f"""
      <h2>Однокоренные слова · {esc(word.get("shoresh") or "")}</h2>
      <ul class="sl-links">{links}</ul>"""

    rel_block = ""
    if related:
        links = "".join(
            f'<li><a href="{r_slug}.html">{esc(first_ru(r["ru"]))} <span lang="he" dir="rtl">{esc(r["he"])}</span></a></li>'
            for r_slug, r in related)
        rel_block = f"""
      <h2>Другие слова уровня {esc(level)}</h2>
      <ul class="sl-links">{links}</ul>"""

    body = f"""    <article>
      <p class="sl-breadcrumb"><a href="../index.html">AlefBet</a> → <a href="index.html">Словарь иврита</a> → {esc(ru_short)}</p>
      <h1>Как будет «{esc(ru_short)}» на иврите</h1>
      {card}{verb_block}{ex_block}
      {cta("ru")}{fam_block}{rel_block}
      <p class="sl-backlinks"><a href="index.html">← Весь словарь</a> <a href="../temy/">Слова по темам</a> <a href="../sleng/">Израильский сленг</a></p>
    </article>"""

    alternates = f"""
    <link rel="alternate" hreflang="ru" href="{SITE}/slovar/{slug}.html">
    <link rel="alternate" hreflang="en" href="{SITE}/dictionary/{en_slug}.html">
    <link rel="alternate" hreflang="x-default" href="{SITE}/dictionary/{en_slug}.html">"""

    jsonld = [
        faq_ld([(f"Как будет «{ru_short}» на иврите?",
                 f"«{ru_short.capitalize()}» на иврите — {he}, читается «{tr}». {pos_ru.capitalize()}, уровень {level}.")]),
        breadcrumb_ld([("AlefBet", f"{SITE}/"), ("Словарь иврита", f"{SITE}/slovar/"), (ru_short, None)]),
    ]
    return shell(lang="ru", title=title, desc=desc, canonical=f"{SITE}/slovar/{slug}.html",
                 body=body, alternates=alternates, jsonld=jsonld)

SECTION_CARDS = """
      <h2>Разделы</h2>
      <div class="hub-grid">
        <a class="hub-card" href="../temy/"><span class="hub-card-he">בְּעִבְרִית</span>
          <span class="hub-card-title">Слова по темам</span>
          <span class="hub-card-sub">Числа, дни недели, цвета, семья, еда и словарики для жизни в Израиле</span></a>
        <a class="hub-card" href="../sleng/"><span class="hub-card-he">סבבה</span>
          <span class="hub-card-title">Израильский сленг</span>
          <span class="hub-card-sub">Сабаба, ялла, тахлес — что значат слова, которые слышно на улице</span></a>
        <a class="hub-card" href="../alfavit/"><span class="hub-card-he">א־ב</span>
          <span class="hub-card-title">Алфавит иврита</span>
          <span class="hub-card-sub">22 буквы с произношением, конечными формами и примерами</span></a>
        <a class="hub-card" href="../glagoly/"><span class="hub-card-he">לִכְתּוֹב</span>
          <span class="hub-card-title">Глаголы и спряжения</span>
          <span class="hub-card-sub">Биньяны, корни и формы времён почти 2 000 глаголов</span></a>
      </div>"""

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
    nav_letters = "".join(f'<a href="#{esc(l)}">{esc(l)}</a>' for l in sorted(by_letter))
    body = f"""    <h1>Русско-ивритский словарь</h1>
    <p class="sl-lead">Частотные слова иврита с огласовками (никуд), транскрипцией, озвучкой и примерами.
    Полная версия — 11&nbsp;000+ слов — в приложении <a href="{APP_URL}">AlefBet</a>.</p>
    {SECTION_CARDS}
    <h2>Все слова</h2>
    <p class="sl-letters">{nav_letters}</p>
    {sections}
    {cta("ru")}"""
    alternates = f"""
    <link rel="alternate" hreflang="ru" href="{SITE}/slovar/">
    <link rel="alternate" hreflang="en" href="{SITE}/dictionary/">
    <link rel="alternate" hreflang="x-default" href="{SITE}/dictionary/">"""
    return shell(lang="ru",
                 title=f"Русско-ивритский словарь онлайн — {len(entries)} слов с транскрипцией и озвучкой | AlefBet",
                 desc=f"Как будет по-иврите: {len(entries)} частотных слов с огласовками, транскрипцией, озвучкой и примерами. Бесплатный онлайн-словарь иврита AlefBet.",
                 canonical=f"{SITE}/slovar/", body=body, alternates=alternates)

def generate(levels={"A1"}):
    """Создаёт страницы, возвращает (entries, en_slugs) для build.py."""
    words = json.load(open(WORDS_JSON))
    entries = build_entries(words, levels)
    en_slugs = build_en_slugs(entries)
    slug_by_id = {w["id"]: s for s, w in entries if w.get("id")}

    # глагольные страницы (может не быть при первом запуске)
    try:
        from generate_glagoly import verb_entries
        verb_slug_by_id = {w["id"]: s for s, w in verb_entries(words)}
    except Exception:
        verb_slug_by_id = {}

    # однокоренные: по всем словам базы, ссылки только на существующие страницы
    by_root = {}
    for w in words:
        if w.get("shoresh") and w.get("id"):
            by_root.setdefault(w["shoresh"], []).append(w)

    def root_family(word):
        fam = []
        for r in by_root.get(word.get("shoresh") or "", []):
            if r["id"] == word.get("id"):
                continue
            if r["id"] in slug_by_id:
                fam.append((f'{slug_by_id[r["id"]]}.html', r))
            elif r["id"] in verb_slug_by_id:
                fam.append((f'../glagoly/{verb_slug_by_id[r["id"]]}.html', r))
        return fam[:8]

    if os.path.isdir(OUT_DIR):
        for f in os.listdir(OUT_DIR):
            if f.endswith(".html"):
                os.remove(os.path.join(OUT_DIR, f))
    os.makedirs(OUT_DIR, exist_ok=True)

    def pick_related(slug, level):
        pool = [(s, w) for s, w in entries if w.get("level") == level and s != slug]
        if not pool:
            return []
        h = int(hashlib.md5(slug.encode()).hexdigest(), 16)
        step = max(1, len(pool) // 6)
        return [pool[(h + i * step) % len(pool)] for i in range(min(6, len(pool)))]

    for slug, w in entries:
        html_out = page(w, slug, pick_related(slug, w.get("level")), en_slugs[slug],
                        root_family(w), verb_slug_by_id.get(w.get("id")))
        with open(os.path.join(OUT_DIR, f"{slug}.html"), "w") as f:
            f.write(html_out)

    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(index_page(entries))

    print(f"slovar: {len(entries)} word pages + index")
    return entries, en_slugs

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="A1")
    args = ap.parse_args()
    generate(set(args.levels.split(",")))
