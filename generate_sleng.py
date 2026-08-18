# -*- coding: utf-8 -*-
"""Раздел /sleng/ — «что значит …»: израильский сленг и разговорные выражения.

Данные: data/sleng.json.  Запуск:  python3 generate_sleng.py
"""
import json, os
from gen_common import SITE, esc, shell, cta, breadcrumb_ld, faq_ld

DATA = os.path.join(os.path.dirname(__file__), "data", "sleng.json")
OUT_DIR = os.path.join(os.path.dirname(__file__), "sleng")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio", "s")

def audio_button(slug):
    if not os.path.exists(os.path.join(AUDIO_DIR, f"{slug}.m4a")):
        return ""
    return (f'<button class="play" type="button" aria-label="Слушать произношение" '
            f'onclick="pl(this,\'../audio/s/{slug}.m4a\')">'
            f'<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8 5.5v13l11-6.5z"/></svg>'
            f'</button>')

def page(e, related):
    word, he, tr = e["word"], e["he"], e["tr"]
    title = f"{word} ({he}) — что значит на иврите | AlefBet"
    desc = f"Что значит «{word.lower()}» на иврите: {he} ({tr}) — {e['short']}. Происхождение, примеры употребления и перевод."
    ghost = next((ch for ch in he if "א" <= ch <= "ת"), "א")
    register = f'<span class="sl-chip">{esc(e["register"])}</span>' if e.get("register") else ""

    ex_items = ""
    for ex in e.get("examples", []):
        ex_items += f"""<div class="sl-example">
          <p lang="he" dir="rtl" class="sl-example-he">{esc(ex["he"])}</p>
          <p class="sl-example-ru"><em>{esc(ex["tr"])}</em> — {esc(ex["ru"])}</p></div>"""

    rel_links = "".join(
        f'<li><a href="{r["slug"]}.html">{esc(r["word"].lower())} <span lang="he" dir="rtl">{esc(r["he"])}</span></a></li>'
        for r in related)

    body = f"""    <article>
      <p class="sl-breadcrumb"><a href="../index.html">AlefBet</a> → <a href="index.html">Израильский сленг</a> → {esc(word.lower())}</p>
      <h1>Что значит «{esc(word.lower())}» на иврите</h1>
      <div class="sl-card">
        <span class="sl-ghost" aria-hidden="true">{ghost}</span>
        <div class="sl-chips"><span class="sl-chip">разговорное</span>{register}</div>
        <div class="sl-he-row"><span class="sl-he" lang="he" dir="rtl">{esc(he)}</span>{audio_button(e["slug"])}</div>
        <div class="sl-ru">{esc(e["short"])}</div>
        <div class="sl-tr">{esc(tr)}</div>
      </div>
      <p class="sg-origin">Происхождение: {esc(e.get("origin") or "иврит")}</p>
      <h2>Значение</h2>
      <p class="sg-body">{e["body"]}</p>
      <h2>Примеры</h2>{ex_items}
      {cta("ru")}
      <h2>Ещё из израильского сленга</h2>
      <ul class="sl-links">{rel_links}</ul>
      <p class="sl-backlinks"><a href="index.html">← Весь сленг</a> <a href="../slovar/">Словарь иврита</a> <a href="../temy/">Слова по темам</a></p>
    </article>"""

    jsonld = [
        faq_ld([(f"Что значит «{word.lower()}» на иврите?",
                 f"«{word}» ({he}, {tr}) — {e['short']}. {e.get('origin', '').capitalize()}.")]),
        breadcrumb_ld([("AlefBet", f"{SITE}/"), ("Израильский сленг", f"{SITE}/sleng/"), (word, None)]),
    ]
    return shell(lang="ru", title=title, desc=desc, canonical=f"{SITE}/sleng/{e['slug']}.html",
                 body=body, jsonld=jsonld)

def index_page(entries):
    cards = "".join(
        f'<a class="hub-card" href="{e["slug"]}.html"><span class="hub-card-he" lang="he" dir="rtl">{esc(e["he"])}</span>'
        f'<span class="hub-card-title">{esc(e["word"])}</span>'
        f'<span class="hub-card-sub">{esc(e["short"])}</span></a>'
        for e in sorted(entries, key=lambda x: x["word"].lower()))
    body = f"""    <h1>Израильский сленг: что значат слова, которые слышно на улице</h1>
    <p class="sl-lead">Сабаба, ялла, тахлес, капара — {len(entries)} слов и выражений, которые не найти в учебнике,
    но без которых не понять живой иврит. С произношением, происхождением и примерами.</p>
    <div class="hub-grid">{cards}</div>
    {cta("ru")}"""
    return shell(lang="ru",
                 title=f"Израильский сленг — {len(entries)} слов с переводом и произношением | AlefBet",
                 desc="Что значит сабаба, ялла, ахла, тахлес, капара и другие слова израильского сленга: перевод, произношение, происхождение и примеры.",
                 canonical=f"{SITE}/sleng/", body=body)

def generate():
    entries = json.load(open(DATA))
    os.makedirs(OUT_DIR, exist_ok=True)
    for f in os.listdir(OUT_DIR):
        if f.endswith(".html"):
            os.remove(os.path.join(OUT_DIR, f))
    n = len(entries)
    for i, e in enumerate(entries):
        related = [entries[(i + k) % n] for k in range(1, 7)]
        with open(os.path.join(OUT_DIR, f'{e["slug"]}.html'), "w") as f:
            f.write(page(e, related))
    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(index_page(entries))
    print(f"sleng: {n} pages + index")
    return entries

if __name__ == "__main__":
    generate()
