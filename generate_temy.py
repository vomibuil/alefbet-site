# -*- coding: utf-8 -*-
"""Раздел /temy/ — тематические подборки слов (числа, дни недели, цвета...).

Данные: data/temy.json. Огласовки/транскрипции подтягиваются из Words.json
по русскому значению; значения из JSON — запасной вариант.
Запуск:  python3 generate_temy.py
"""
import json, os
from gen_common import (SITE, APP_URL, WORDS_JSON, esc, first_ru, shell, cta,
                        breadcrumb_ld, has_audio)

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

def index_page(topics):
    cards = "".join(
        f'<a class="hub-card" href="{t["slug"]}.html"><span class="hub-card-he" lang="he" dir="rtl">{esc(t["he_sample"])}</span>'
        f'<span class="hub-card-title">{esc(t["title"])}</span>'
        f'<span class="hub-card-sub">{len(t["items"])} слов</span></a>'
        for t in topics)
    body = f"""    <h1>Иврит по темам: тематические словарики</h1>
    <p class="sl-lead">Числа, дни недели, цвета, семья — и словарики для реальных ситуаций:
    супермаркет, больничная касса, банк. Каждая тема — с транскрипцией и озвучкой,
    полный словарь 11 000+ слов — в приложении <a href="{APP_URL}">AlefBet</a>.</p>
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
    for i, t in enumerate(topics):
        others = topics[i + 1:] + topics[:i]
        with open(os.path.join(OUT_DIR, f'{t["slug"]}.html'), "w") as f:
            f.write(page(t, lookup, slovar_by_id, others))
    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(index_page(topics))
    print(f"temy: {len(topics)} topic pages + index")
    return topics

if __name__ == "__main__":
    generate()
