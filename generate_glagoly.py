# -*- coding: utf-8 -*-
"""Раздел /glagoly/ — страницы спряжения глаголов иврита (A1–B1).

Запуск:  python3 generate_glagoly.py  (sitemap собирает build.py)
"""
import json, os
from gen_common import (SITE, APP_URL, WORDS_JSON, esc, slugify, first_ru,
                        shell, word_card, cta, breadcrumb_ld, faq_ld)

OUT_DIR = os.path.join(os.path.dirname(__file__), "glagoly")
LEVELS = ("A1", "A2", "B1")

BINYAN_RU = {
    "פָּעַל": "пааль", "פִּיעֵל": "пиэль", "הִתְפַּעֵל": "хитпаэль",
    "הִפְעִיל": "хифиль", "נִפְעַל": "нифаль", "פּוּעַל": "пуаль", "הוּפְעַל": "хуфаль",
}
BINYAN_ABOUT = {
    "пааль": "базовый биньян: простое активное действие",
    "пиэль": "интенсивное или направленное действие",
    "хитпаэль": "возвратное или взаимное действие",
    "хифиль": "каузатив: заставить или дать сделать",
    "нифаль": "пассив или состояние",
}

def verb_entries(words=None):
    """(slug, word) для всех глаголов A1–B1 с формами — стабильные слаги."""
    if words is None:
        words = json.load(open(WORDS_JSON))
    verbs = [w for w in words
             if w.get("pos") == "verb" and w.get("level") in LEVELS
             and w.get("ru") and w.get("he") and w.get("past")]
    entries, used = [], {}
    for w in sorted(verbs, key=lambda x: (x.get("level"), first_ru(x["ru"]).lower())):
        base = slugify(first_ru(w["ru"]))
        n = used.get(base, 0)
        slug = f"{base}-{n + 1}" if n else base
        used[base] = n + 1
        entries.append((slug, w))
    return entries

def page(word, slug, family, same_binyan):
    ru_short = first_ru(word["ru"])
    he, tr = word["he"], word.get("transcription") or ""
    binyan_he = word.get("binyan") or ""
    binyan = BINYAN_RU.get(binyan_he, binyan_he)
    title = f"Спряжение глагола «{ru_short}» на иврите — {he} ({tr}) | AlefBet"
    desc = (f"Глагол «{ru_short}» на иврите: {he} ({tr}), биньян {binyan}, корень {word.get('shoresh') or '—'}. "
            f"Формы прошедшего, настоящего и будущего времени с примерами.")

    card = word_card(he=he, main=word["ru"], tr=tr, sub=f'англ.: {word.get("en") or ""}',
                     chips=("глагол", f"биньян {binyan}", word.get("level")),
                     root_chip=word.get("shoresh") or "", word_id=word.get("id"))

    cells = ""
    for label, key in (("Прошедшее", "past"), ("Настоящее", "present"), ("Будущее", "future")):
        if word.get(key):
            cells += f"""<div class="sl-tense"><span class="sl-tense-label">{label}</span>
            <span lang="he" dir="rtl">{esc(word[key])}</span></div>"""
    about = BINYAN_ABOUT.get(binyan, "")
    binyan_line = f'<p class="sl-binyan">Биньян <b>{esc(binyan)}</b> <span lang="he" dir="rtl">{esc(binyan_he)}</span>{" — " + about if about else ""}.</p>'

    ex_block = ""
    if word.get("examples"):
        items = "".join(f"""<div class="sl-example">
          <p lang="he" dir="rtl" class="sl-example-he">{esc(ex.get("he"))}</p>
          <p class="sl-example-ru">{esc(ex.get("ru"))}</p></div>""" for ex in word["examples"][:3])
        ex_block = f"\n      <h2>Примеры употребления</h2>{items}"

    fam_block = ""
    if family:
        links = "".join(
            f'<li><a href="{href}">{esc(first_ru(r["ru"]))} <span lang="he" dir="rtl">{esc(r["he"])}</span></a></li>'
            for href, r in family)
        fam_block = f"""
      <h2>Однокоренные слова · {esc(word.get("shoresh") or "")}</h2>
      <ul class="sl-links">{links}</ul>"""

    rel_block = ""
    if same_binyan:
        links = "".join(
            f'<li><a href="{s}.html">{esc(first_ru(r["ru"]))} <span lang="he" dir="rtl">{esc(r["he"])}</span></a></li>'
            for s, r in same_binyan)
        rel_block = f"""
      <h2>Другие глаголы биньяна {esc(binyan)}</h2>
      <ul class="sl-links">{links}</ul>"""

    body = f"""    <article>
      <p class="sl-breadcrumb"><a href="../index.html">AlefBet</a> → <a href="index.html">Глаголы иврита</a> → {esc(ru_short)}</p>
      <h1>Глагол «{esc(ru_short)}» на иврите: спряжение {esc(he)}</h1>
      {card}
      <h2>Формы глагола</h2>
      {binyan_line}
      <div class="sl-tenses">{cells}</div>
      <p class="sl-note">Полные таблицы спряжения по лицам и родам — в приложении <a href="{APP_URL}">AlefBet</a>.</p>{ex_block}
      {cta("ru")}{fam_block}{rel_block}
      <p class="sl-backlinks"><a href="index.html">← Все глаголы</a> <a href="../slovar/">Словарь</a> <a href="../temy/">Слова по темам</a></p>
    </article>"""

    jsonld = [
        faq_ld([(f"Как спрягается глагол «{ru_short}» на иврите?",
                 f"«{ru_short.capitalize()}» на иврите — {he} ({tr}), биньян {binyan}. "
                 f"Прошедшее: {word.get('past') or '—'}, настоящее: {word.get('present') or '—'}, будущее: {word.get('future') or '—'}.")]),
        breadcrumb_ld([("AlefBet", f"{SITE}/"), ("Глаголы иврита", f"{SITE}/glagoly/"), (ru_short, None)]),
    ]
    return shell(lang="ru", title=title, desc=desc, canonical=f"{SITE}/glagoly/{slug}.html",
                 body=body, jsonld=jsonld)

def index_page(entries):
    by_letter = {}
    for slug, w in entries:
        by_letter.setdefault(first_ru(w["ru"])[:1].upper() or "#", []).append((slug, w))
    sections = ""
    for letter in sorted(by_letter):
        links = "".join(
            f'<li><a href="{slug}.html">{esc(first_ru(w["ru"]))} — <span lang="he" dir="rtl">{esc(w["he"])}</span></a></li>'
            for slug, w in sorted(by_letter[letter], key=lambda p: first_ru(p[1]["ru"]).lower()))
        sections += f'<h2 id="{esc(letter)}">{esc(letter)}</h2><ul class="sl-index-list">{links}</ul>'
    nav_letters = "".join(f'<a href="#{esc(l)}">{esc(l)}</a>' for l in sorted(by_letter))
    binyan_cards = "".join(
        f'<div class="al-fact"><span class="al-fact-label">{esc(name)}</span>'
        f'<span class="al-fact-value" lang="he" dir="rtl">{esc(he)}</span></div>'
        for he, name in BINYAN_RU.items() if name in BINYAN_ABOUT)
    body = f"""    <h1>Глаголы иврита: спряжения и биньяны</h1>
    <p class="sl-lead">{len(entries)} глаголов уровней A1–B1 с корнем, биньяном и формами трёх времён.
    Полные таблицы спряжения по лицам — в приложении <a href="{APP_URL}">AlefBet</a>.</p>
    <h2>Пять основных биньянов</h2>
    <div class="al-facts">{binyan_cards}</div>
    <h2>Все глаголы</h2>
    <p class="sl-letters">{nav_letters}</p>
    {sections}
    {cta("ru")}"""
    return shell(lang="ru",
                 title=f"Спряжение глаголов иврита — {len(entries)} глаголов с биньянами | AlefBet",
                 desc=f"Спряжение глаголов иврита: {len(entries)} глаголов A1–B1 с корнями, биньянами, формами времён и примерами. Бесплатный справочник AlefBet.",
                 canonical=f"{SITE}/glagoly/", body=body)

def generate():
    words = json.load(open(WORDS_JSON))
    entries = verb_entries(words)
    slug_by_id = {w["id"]: s for s, w in entries}

    try:
        from generate_slovar import build_entries
        slovar_by_id = {w["id"]: s for s, w in build_entries(words, {"A1"})}
    except Exception:
        slovar_by_id = {}

    by_root = {}
    for w in words:
        if w.get("shoresh") and w.get("id"):
            by_root.setdefault(w["shoresh"], []).append(w)

    def family(word):
        fam = []
        for r in by_root.get(word.get("shoresh") or "", []):
            if r["id"] == word.get("id"):
                continue
            if r["id"] in slovar_by_id:
                fam.append((f'../slovar/{slovar_by_id[r["id"]]}.html', r))
            elif r["id"] in slug_by_id:
                fam.append((f'{slug_by_id[r["id"]]}.html', r))
        return fam[:8]

    by_binyan = {}
    for s, w in entries:
        by_binyan.setdefault(w.get("binyan"), []).append((s, w))

    import hashlib
    def pick_same_binyan(slug, binyan):
        pool = [(s, w) for s, w in by_binyan.get(binyan, []) if s != slug]
        if not pool:
            return []
        h = int(hashlib.md5(slug.encode()).hexdigest(), 16)
        step = max(1, len(pool) // 6)
        return [pool[(h + i * step) % len(pool)] for i in range(min(6, len(pool)))]

    if os.path.isdir(OUT_DIR):
        for f in os.listdir(OUT_DIR):
            if f.endswith(".html"):
                os.remove(os.path.join(OUT_DIR, f))
    os.makedirs(OUT_DIR, exist_ok=True)

    for slug, w in entries:
        with open(os.path.join(OUT_DIR, f"{slug}.html"), "w") as f:
            f.write(page(w, slug, family(w), pick_same_binyan(slug, w.get("binyan"))))
    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(index_page(entries))
    print(f"glagoly: {len(entries)} verb pages + index")
    return entries

if __name__ == "__main__":
    generate()
