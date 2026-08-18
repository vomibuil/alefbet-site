# -*- coding: utf-8 -*-
"""English SEO dictionary pages for alefbet.tech → /dictionary/.

Mirrors /slovar/ (same words, same slug base, hreflang pair).
Run:  python3 generate_dictionary.py  (sitemap is built by build.py)
"""
import json, os, hashlib, re
from gen_common import SITE, APP_URL, WORDS_JSON, esc, shell, word_card, cta, breadcrumb_ld, faq_ld
from generate_slovar import build_entries, build_en_slugs, first_en

OUT_DIR = os.path.join(os.path.dirname(__file__), "dictionary")

POS_EN = {
    "noun": "noun", "verb": "verb", "adjective": "adjective", "adverb": "adverb",
    "pronoun": "pronoun", "preposition": "preposition", "conjunction": "conjunction",
    "interjection": "interjection", "numeral": "numeral", "particle": "particle",
    "phrase": "phrase", "other": "other",
}

def page(word, slug, ru_slug, related):
    en_short = first_en(word.get("en") or "")
    he = word["he"]
    tr = word.get("transcription_en") or word.get("transcription") or ""
    pos = POS_EN.get(word.get("pos") or "", word.get("pos") or "")
    level = word.get("level") or ""
    title = f"“{en_short.capitalize()}” in Hebrew — {he} ({tr}) | AlefBet"
    desc = (f"How to say “{en_short}” in Hebrew: {he}, pronounced “{tr}”, "
            f"{pos}, with usage examples. AlefBet — 11,000+ Hebrew words offline.")

    card = word_card(he=he, main=word.get("en") or "", tr=tr, chips=(pos, level),
                     root_chip=word.get("shoresh") or "", word_id=word.get("id"))

    verb_block = ""
    if word.get("pos") == "verb" and (word.get("past") or word.get("present") or word.get("future")):
        cells = ""
        for label, key in (("Past", "past"), ("Present", "present"), ("Future", "future")):
            if word.get(key):
                cells += f"""<div class="sl-tense"><span class="sl-tense-label">{label}</span>
                <span lang="he" dir="rtl">{esc(word[key])}</span></div>"""
        binyan = f'<p class="sl-binyan">Binyan: <b>{esc(word["binyan"])}</b></p>' if word.get("binyan") else ""
        verb_block = f"""
      <h2>Verb forms</h2>{binyan}
      <div class="sl-tenses">{cells}</div>"""

    ex_block = ""
    if word.get("examples"):
        items = ""
        for ex in word["examples"][:3]:
            en_line = ex.get("en") or ex.get("ru") or ""
            items += f"""<div class="sl-example">
          <p lang="he" dir="rtl" class="sl-example-he">{esc(ex.get("he"))}</p>
          <p class="sl-example-ru">{esc(en_line)}</p></div>"""
        ex_block = f"""
      <h2>Examples</h2>{items}"""

    rel_block = ""
    if related:
        links = "".join(
            f'<li><a href="{r_slug}.html">{esc(first_en(r.get("en") or ""))} <span lang="he" dir="rtl">{esc(r["he"])}</span></a></li>'
            for r_slug, r in related)
        rel_block = f"""
      <h2>More {esc(level)} words</h2>
      <ul class="sl-links">{links}</ul>"""

    body = f"""    <article>
      <p class="sl-breadcrumb"><a href="../index.html">AlefBet</a> → <a href="index.html">Hebrew dictionary</a> → {esc(en_short)}</p>
      <h1>How to say “{esc(en_short)}” in Hebrew</h1>
      {card}{verb_block}{ex_block}
      {cta("en")}{rel_block}
      <p class="sl-backlinks"><a href="index.html">← Full dictionary</a></p>
    </article>"""

    alternates = f"""
    <link rel="alternate" hreflang="en" href="{SITE}/dictionary/{slug}.html">
    <link rel="alternate" hreflang="ru" href="{SITE}/slovar/{ru_slug}.html">
    <link rel="alternate" hreflang="x-default" href="{SITE}/dictionary/{slug}.html">"""

    jsonld = [
        faq_ld([(f"How do you say “{en_short}” in Hebrew?",
                 f"“{en_short.capitalize()}” in Hebrew is {he}, pronounced “{tr}”. {pos.capitalize()}, level {level}.")]),
        breadcrumb_ld([("AlefBet", f"{SITE}/"), ("Hebrew dictionary", f"{SITE}/dictionary/"), (en_short, None)]),
    ]
    return shell(lang="en", title=title, desc=desc, canonical=f"{SITE}/dictionary/{slug}.html",
                 body=body, alternates=alternates, jsonld=jsonld)

def index_page(pairs):
    by_letter = {}
    for slug, ru_slug, w in pairs:
        letter = (first_en(w.get("en") or "")[:1] or "#").upper()
        by_letter.setdefault(letter, []).append((slug, w))
    sections = ""
    for letter in sorted(by_letter):
        links = "".join(
            f'<li><a href="{slug}.html">{esc(first_en(w.get("en") or ""))} — <span lang="he" dir="rtl">{esc(w["he"])}</span></a></li>'
            for slug, w in sorted(by_letter[letter], key=lambda p: first_en(p[1].get("en") or "").lower()))
        sections += f'<h2 id="{esc(letter)}">{esc(letter)}</h2><ul class="sl-index-list">{links}</ul>'
    nav_letters = "".join(f'<a href="#{esc(l)}">{esc(l)}</a>' for l in sorted(by_letter))
    body = f"""    <h1>English–Hebrew dictionary</h1>
    <p class="sl-lead">Frequent Hebrew words with nikkud (vowel marks), transcription, audio and examples.
    The full dictionary — 11,000+ words — is in the <a href="{APP_URL}">AlefBet app</a>.</p>
    <p class="sl-letters">{nav_letters}</p>
    {sections}
    {cta("en")}"""
    alternates = f"""
    <link rel="alternate" hreflang="en" href="{SITE}/dictionary/">
    <link rel="alternate" hreflang="ru" href="{SITE}/slovar/">
    <link rel="alternate" hreflang="x-default" href="{SITE}/dictionary/">"""
    return shell(lang="en",
                 title=f"English–Hebrew dictionary online — {len(pairs)} words with transcription | AlefBet",
                 desc=f"How to say it in Hebrew: {len(pairs)} frequent words with nikkud, transcription, audio and examples. Free online Hebrew dictionary by AlefBet.",
                 canonical=f"{SITE}/dictionary/", body=body, alternates=alternates)

def generate():
    words = json.load(open(WORDS_JSON))
    entries = build_entries(words, {"A1"})
    en_slugs = build_en_slugs(entries)
    pairs = [(en_slugs[ru_slug], ru_slug, w) for ru_slug, w in entries]

    if os.path.isdir(OUT_DIR):
        for f in os.listdir(OUT_DIR):
            if f.endswith(".html"):
                os.remove(os.path.join(OUT_DIR, f))
    os.makedirs(OUT_DIR, exist_ok=True)

    def pick_related(slug, level):
        pool = [(s, w) for s, _, w in pairs if w.get("level") == level and s != slug]
        if not pool:
            return []
        h = int(hashlib.md5(slug.encode()).hexdigest(), 16)
        step = max(1, len(pool) // 6)
        return [pool[(h + i * step) % len(pool)] for i in range(min(6, len(pool)))]

    for slug, ru_slug, w in pairs:
        with open(os.path.join(OUT_DIR, f"{slug}.html"), "w") as f:
            f.write(page(w, slug, ru_slug, pick_related(slug, w.get("level"))))
    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(index_page(pairs))
    print(f"dictionary: {len(pairs)} word pages + index")
    return pairs

if __name__ == "__main__":
    generate()
