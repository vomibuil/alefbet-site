# -*- coding: utf-8 -*-
"""Полная сборка SEO-разделов alefbet.tech + sitemap.xml.

Запуск:  python3 build.py
"""
import os
from gen_common import SITE

def main():
    import generate_glagoly, generate_slovar, generate_dictionary
    import generate_sleng, generate_temy, generate_alfavit

    verb_entries = generate_glagoly.generate()
    entries, en_slugs = generate_slovar.generate()
    generate_dictionary.generate()
    sleng = generate_sleng.generate()
    temy = generate_temy.generate()
    letters = generate_alfavit.generate()

    static_pages = ["", "support.html", "privacy.html", "terms.html",
                    "slovar/", "dictionary/", "sleng/", "temy/", "alfavit/", "glagoly/"]
    urls = ([f"{SITE}/{p}" for p in static_pages]
            + [f"{SITE}/slovar/{s}.html" for s, _ in entries]
            + [f"{SITE}/dictionary/{en_slugs[s]}.html" for s, _ in entries]
            + [f"{SITE}/glagoly/{s}.html" for s, _ in verb_entries]
            + [f"{SITE}/sleng/{e['slug']}.html" for e in sleng]
            + [f"{SITE}/temy/{t['slug']}.html" for t in temy]
            + [f"{SITE}/alfavit/{s}.html" for s in letters])
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc></url>" for u in urls]
    sm.append("</urlset>")
    with open(os.path.join(os.path.dirname(__file__), "sitemap.xml"), "w") as f:
        f.write("\n".join(sm))
    print(f"sitemap: {len(urls)} urls")

if __name__ == "__main__":
    main()
