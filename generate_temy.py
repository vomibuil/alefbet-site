# -*- coding: utf-8 -*-
"""Раздел /temy/ — тематические подборки слов (числа, дни недели, цвета...).

Данные: data/temy.json. Огласовки/транскрипции подтягиваются из Words.json
по русскому значению; значения из JSON — запасной вариант.
Запуск:  python3 generate_temy.py
"""
import json, os
from gen_common import (SITE, APP_URL, WORDS_JSON, esc, first_ru, shell, cta,
                        breadcrumb_ld, has_audio, app_url, badge)

DATA = os.path.join(os.path.dirname(__file__), "data", "temy.json")
OUT_DIR = os.path.join(os.path.dirname(__file__), "temy")

LEVEL_ORDER = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4, "C2": 5}

def build_lookup(words):
    """первое русское значение (lower) → слово с минимальным уровнем"""
    lookup = {}
    for w in words:
        if not (w.get("ru") and w.get("he")):
            continue
        key = first_ru(w["ru"]).lower()
        cur = lookup.get(key)
        if cur is None or LEVEL_ORDER.get(w.get("level"), 9) < LEVEL_ORDER.get(cur.get("level"), 9):
            lookup[key] = w
    return lookup

def row(item, lookup, slovar_by_id, no_lookup=False):
    w = None if no_lookup else lookup.get(item["ru"].lower())
    he = w["he"] if w else item["he"]
    tr = (w.get("transcription") if w else None) or item["tr"]
    ru_label = esc(item["ru"])
    if w and w.get("id") in slovar_by_id:
        ru_label = f'<a href="../slovar/{slovar_by_id[w["id"]]}.html">{ru_label}</a>'
    play = ""
    if w and has_audio(w.get("id")):
        play = (f'<button class="play play-inline" type="button" aria-label="Слушать произношение" '
                f'onclick="pl(this,\'../audio/w/{w["id"]}.m4a\')">'
                f'<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M8 5.5v13l11-6.5z"/></svg></button>')
    return (f'<li><span lang="he" dir="rtl">{esc(he)}</span>'
            f'<span class="wl-ru">{ru_label}</span>'
            f'<span class="wl-tr">{esc(tr)}</span>{play}</li>')

def page(topic, lookup, slovar_by_id, others):
    rows = "".join(row(it, lookup, slovar_by_id, topic.get("no_lookup", False)) for it in topic["items"])
    note = f'<p class="sl-note">{topic["note"]}</p>' if topic.get("note") else ""
    rel = "".join(
        f'<a class="hub-card" href="{t["slug"]}.html"><span class="hub-card-he" lang="he" dir="rtl">{esc(t["he_sample"])}</span>'
        f'<span class="hub-card-title">{esc(t["title"])}</span></a>'
        for t in others[:6])
    body = f"""    <article>
      <p class="sl-breadcrumb"><a href="../index.html">AlefBet</a> → <a href="index.html">Слова по темам</a> → {esc(topic["title"])}</p>
      <h1>{esc(topic["title"])}</h1>
      <p class="sl-lead">{topic["intro"]}</p>
      <h2>Слова с транскрипцией</h2>
      <ul class="sl-wordlist">{rows}</ul>
      {note}
      {cta("ru")}
      <h2>Другие темы</h2>
      <div class="hub-grid">{rel}</div>
      <p class="sl-backlinks"><a href="index.html">← Все темы</a> <a href="../slovar/">Словарь</a> <a href="../alfavit/">Алфавит</a></p>
    </article>"""
    jsonld = [breadcrumb_ld([("AlefBet", f"{SITE}/"), ("Слова по темам", f"{SITE}/temy/"),
                             (topic["title"], None)])]
    return shell(lang="ru", title=f'{topic["title"]} — с транскрипцией и произношением | AlefBet',
                 desc=topic["desc"], canonical=f'{SITE}/temy/{topic["slug"]}.html',
                 body=body, jsonld=jsonld)

# --- Темы по тегу Words.json (1.6: «Ханука») — слова берутся по topics, а не по русскому значению ---

def _skel(he):
    return "".join(c for c in he if "\u05d0" <= c <= "\u05ea" or c == " ")

def tag_words(words, tag, lead=()):
    """Слова темы: сначала lead (самые «праздничные», в заданном порядке), затем остальные по частотности."""
    ws = [w for w in words if tag in (w.get("topics") or [])]
    rank = {s: i for i, s in enumerate(lead)}
    return sorted(ws, key=lambda w: (rank.get(_skel(w["he"]), len(rank)), w.get("freq") or 10**9, w["he"]))

def tag_row(w, lang, examples=False):
    tr = w.get("transcription_en") if lang == "en" else w.get("transcription")
    tr = tr or w.get("transcription") or ""
    root = ".." if lang == "ru" else ".."
    play = ""
    if has_audio(w.get("id")):
        label = "Слушать произношение" if lang == "ru" else "Listen"
        play = (f'<button class="play play-inline" type="button" aria-label="{label}" '
                f'onclick="pl(this,\'{root}/audio/w/{w["id"]}.m4a\')">'
                f'<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M8 5.5v13l11-6.5z"/></svg></button>')
    ex = ""
    if examples and w.get("examples"):
        e = w["examples"][0]
        ex = (f'<span class="wl-ex"><span lang="he" dir="rtl">{esc(e["he"])}</span> — '
              f'{esc(e["en"] if lang == "en" else e["ru"])}</span>')
    return (f'<li><span lang="he" dir="rtl">{esc(w["he"])}</span>'
            f'<span class="wl-ru">{esc(w["en"] if lang == "en" else w["ru"])}</span>'
            f'<span class="wl-tr">{esc(tr)}</span>{play}{ex}</li>')

def tag_page(topic, words, lang):
    ws = tag_words(words, topic["topic_tag"], topic.get("lead", ()))
    rows = "".join(tag_row(w, lang, topic.get("examples", False)) for w in ws)
    ru_url, en_url = f'{SITE}/temy/{topic["slug"]}.html', f'{SITE}/en/{topic["en_slug"]}.html'
    alts = (f'\n    <link rel="alternate" hreflang="ru" href="{ru_url}">'
            f'\n    <link rel="alternate" hreflang="en" href="{en_url}">'
            f'\n    <link rel="alternate" hreflang="x-default" href="{ru_url}">')
    t = topic if lang == "ru" else {k[3:]: v for k, v in topic.items() if k.startswith("en_")}
    store = app_url("site_hanuka")
    free = ("Тема «Ханука» бесплатна в приложении AlefBet — с озвучкой, карточками и тестом."
            if lang == "ru" else "The Hanukkah topic is free in the AlefBet app — with audio, flashcards and a quiz.")
    crumbs = ('<a href="../index.html">AlefBet</a> → <a href="index.html">Слова по темам</a> → ' if lang == "ru"
              else '<a href="index.html">AlefBet</a> → ')
    h2 = (f"{len(ws)} слов с транскрипцией и примерами" if lang == "ru"
          else f"{len(ws)} words with transliteration and examples")
    body = f"""    <article>
      <p class="sl-breadcrumb">{crumbs}{esc(t["title"])}</p>
      <h1>{esc(t["title"])}</h1>
      <p class="sl-lead">{t["intro"]}</p>
      <h2>{h2}</h2>
      <ul class="sl-wordlist">{rows}</ul>
      <aside class="cta-band"><span class="cta-band-alef" aria-hidden="true">א</span>
        <div class="cta-band-inner"><p>{free}</p>{badge(lang).replace(APP_URL, store)}</div></aside>
    </article>"""
    canon = ru_url if lang == "ru" else en_url
    return shell(lang=lang, title=t["page_title"], desc=t["desc"], canonical=canon, body=body,
                 alternates=alts, jsonld=[breadcrumb_ld([("AlefBet", f"{SITE}/" if lang == "ru" else f"{SITE}/en/"), (t["title"], None)])])

def generate_tagged():
    """Только страницы тем по тегу (+ индекс /temy/): остальные 13 тем не перегенерируются."""
    topics = json.load(open(DATA))
    words = json.load(open(WORDS_JSON))
    for t in topics:
        if not t.get("topic_tag"):
            continue
        with open(os.path.join(OUT_DIR, f'{t["slug"]}.html'), "w") as f:
            f.write(tag_page(t, words, "ru"))
        os.makedirs(os.path.join(os.path.dirname(__file__), "en"), exist_ok=True)
        with open(os.path.join(os.path.dirname(__file__), "en", f'{t["en_slug"]}.html'), "w") as f:
            f.write(tag_page(t, words, "en"))
        t["count"] = len(tag_words(words, t["topic_tag"]))
    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(index_page(topics))
    print("temy: tagged pages + index")

def index_page(topics):
    cards = "".join(
        f'<a class="hub-card" href="{t["slug"]}.html"><span class="hub-card-he" lang="he" dir="rtl">{esc(t["he_sample"])}</span>'
        f'<span class="hub-card-title">{esc(t["title"])}</span>'
        f'<span class="hub-card-sub">{t.get("count") or len(t.get("items", []))} слов</span></a>'
        for t in topics)
    body = f"""    <h1>Иврит по темам: тематические словарики</h1>
    <p class="sl-lead">Числа, дни недели, цвета, семья — и словарики для реальных ситуаций:
    супермаркет, больничная касса, банк. Каждая тема — с транскрипцией и озвучкой,
    полный словарь 12 700+ слов — в приложении <a href="{APP_URL}">AlefBet</a>.</p>
    <div class="hub-grid">{cards}</div>
    {cta("ru")}"""
    return shell(lang="ru",
                 title="Иврит по темам — числа, дни недели, цвета, слова для репатрианта | AlefBet",
                 desc="Тематические словарики иврита с транскрипцией: числа, дни недели, месяцы, цвета, семья, еда, супермаркет, врач, банк, транспорт и работа.",
                 canonical=f"{SITE}/temy/", body=body)

def generate():
    topics = json.load(open(DATA))
    words = json.load(open(WORDS_JSON))
    lookup = build_lookup(words)
    from generate_slovar import build_entries
    slovar_by_id = {w["id"]: s for s, w in build_entries(words, {"A1"}) if w.get("id")}

    os.makedirs(OUT_DIR, exist_ok=True)
    for f in os.listdir(OUT_DIR):
        if f.endswith(".html"):
            os.remove(os.path.join(OUT_DIR, f))
    plain = [t for t in topics if not t.get("topic_tag")]
    for t in topics:
        if t.get("topic_tag"):
            t["count"] = len(tag_words(words, t["topic_tag"]))
            with open(os.path.join(OUT_DIR, f'{t["slug"]}.html'), "w") as f:
                f.write(tag_page(t, words, "ru"))
    for i, t in enumerate(plain):
        others = plain[i + 1:] + plain[:i]
        with open(os.path.join(OUT_DIR, f'{t["slug"]}.html'), "w") as f:
            f.write(page(t, lookup, slovar_by_id, others))
    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(index_page(topics))
    print(f"temy: {len(topics)} topic pages + index")
    return topics

if __name__ == "__main__":
    import sys
    generate_tagged() if "--tagged" in sys.argv else generate()
