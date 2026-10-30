"""Проверки собранного сайта alefbet.tech. Запуск из website/:
    python3 -m unittest tests/check_site.py -v
"""
import os, re, sys, unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import gen_common  # noqa: E402


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


class SeoPages(unittest.TestCase):
    def test_app_url_without_token(self):
        with mock.patch.object(gen_common, "PROVIDER_TOKEN", ""):
            self.assertEqual(gen_common.app_url("site_ru"),
                             "https://apps.apple.com/app/id6782951189?ct=site_ru&mt=8")

    def test_app_url_with_token(self):
        with mock.patch.object(gen_common, "PROVIDER_TOKEN", "123"):
            self.assertEqual(gen_common.app_url("site_ru"),
                             "https://apps.apple.com/app/id6782951189?pt=123&ct=site_ru&mt=8")

    def test_no_old_count(self):
        for p in ["dictionary/air.html", "slovar/vozduh.html", "temy/eda-na-ivrite.html"]:
            html = read(p)
            self.assertNotRegex(html, r"11[ ,]000", p)
            self.assertRegex(html, r"12[ ,]700\+", p)

    def test_en_logo_points_to_en(self):
        self.assertIn('href="../en/index.html" class="logo"', read("dictionary/air.html"))
        self.assertIn('href="../index.html" class="logo"', read("slovar/vozduh.html"))


class Landing(unittest.TestCase):
    RU, EN = "index.html", "en/index.html"

    def test_landing_langs(self):
        self.assertIn('<html lang="ru"', read(self.RU))
        self.assertIn('<html lang="en"', read(self.EN))

    def test_landing_hreflang(self):
        for p in (self.RU, self.EN):
            h = read(p)
            self.assertIn('hreflang="ru" href="https://alefbet.tech/"', h, p)
            self.assertIn('hreflang="en" href="https://alefbet.tech/en/"', h, p)
            self.assertIn('hreflang="x-default" href="https://alefbet.tech/"', h, p)

    def test_landing_store_links(self):
        for p, ct in ((self.RU, "ct=site_ru"), (self.EN, "ct=site_en")):
            links = re.findall(r'href="(https://apps\.apple\.com[^"]*)"', read(p))
            self.assertGreaterEqual(len(links), 2, p)
            for l in links:
                self.assertIn(ct, l, p)

    def test_landing_counts(self):
        ru, en = read(self.RU), read(self.EN)
        self.assertIn("12 747", ru); self.assertIn("13 тем", ru)
        self.assertIn("12,747", en); self.assertIn("13 topics", en)

    def test_hebrew_isolated(self):
        for p in (self.RU, self.EN):
            h = read(p)
            for w in ("הָלַכְתִּי", "לָלֶכֶת"):
                self.assertRegex(h, r'(<bdi[^>]*>|dir="rtl"[^>]*>)\s*' + w, (p, w))

    def test_hebrew_phrase_one_run(self):
        # фраза из нескольких слов изолируется целиком, иначе bidi переворачивает порядок слов
        for p in (self.RU, self.EN):
            self.assertRegex(read(p), r'<bdi[^>]*>נס גדול היה פה</bdi>', p)

    def test_images_sized(self):
        for p in (self.RU, self.EN):
            imgs = re.findall(r"<img\b[^>]*>", read(p))
            self.assertGreaterEqual(len(imgs), 3, p)
            for i, tag in enumerate(imgs):
                self.assertIn("width=", tag, (p, tag)); self.assertIn("height=", tag, (p, tag))
                if i >= 2:
                    self.assertIn('loading="lazy"', tag, (p, tag))

    def test_switcher(self):
        self.assertIn('href="en/index.html"', read(self.RU))
        self.assertIn('href="../index.html"', read(self.EN))

    def test_hanuka_link(self):
        self.assertIn('href="temy/hanuka-na-ivrite.html"', read(self.RU))
        self.assertIn('href="hanukkah-in-hebrew.html"', read(self.EN))


class Hanukkah(unittest.TestCase):
    RU, EN = "temy/hanuka-na-ivrite.html", "en/hanukkah-in-hebrew.html"

    def rows(self, html):
        lst = re.search(r'<ul class="sl-wordlist">(.*?)</ul>', html, re.S).group(1)
        return re.findall(r"<li>.*?</li>", lst, re.S)

    def test_hanuka_ru(self):
        h = read(self.RU)
        self.assertEqual(len(self.rows(h)), 28)
        self.assertGreaterEqual(h.count('class="wl-ex"'), 28)
        self.assertIn("ct=site_hanuka", h)
        self.assertIn('hreflang="en" href="https://alefbet.tech/en/hanukkah-in-hebrew.html"', h)
        self.assertIn('hreflang="ru" href="https://alefbet.tech/temy/hanuka-na-ivrite.html"', h)

    def test_hanuka_en(self):
        h = read(self.EN)
        self.assertIn('<html lang="en"', h)
        self.assertEqual(len(self.rows(h)), 28)
        self.assertIn("Hanukkah", h)
        self.assertIn('hreflang="ru" href="https://alefbet.tech/temy/hanuka-na-ivrite.html"', h)
        self.assertIn("ct=site_hanuka", h)

    def test_hanuka_specific_words_first(self):
        for p in (self.RU, self.EN):
            first = self.rows(read(p))[:4]
            self.assertIn("חֲנוּכָּה", first[0], p)
            self.assertTrue(any("סְבִיבוֹן" in r for r in first), p)

    def test_hanuka_intro_hebrew_isolated(self):
        for p in (self.RU, self.EN):
            h = read(p)
            self.assertRegex(h, r'<bdi[^>]*>חג האורים</bdi>', p)
            self.assertRegex(h, r'<bdi[^>]*>נ ג ה פ</bdi>', p)

    def test_other_temy_unchanged(self):
        self.assertNotIn("wl-ex", read("temy/eda-na-ivrite.html"))

    def test_missing_audio_no_button(self):
        import generate_temy
        w = {"id": "x-no-audio", "he": "נֵס", "ru": "чудо", "en": "miracle", "transcription": "нэс",
             "examples": [{"he": "נֵס גָּדוֹל", "ru": "большое чудо", "en": "a great miracle"}]}
        with mock.patch.object(generate_temy, "has_audio", lambda _id: False):
            row = generate_temy.tag_row(w, "ru", examples=True)
        self.assertNotIn('class="play', row)
        self.assertIn('class="wl-ex"', row)


class ReviewFixes(unittest.TestCase):
    def test_en_breadcrumb_points_to_en(self):
        h = read("dictionary/air.html")
        self.assertIn('<p class="sl-breadcrumb"><a href="../en/index.html">AlefBet</a>', h)
        self.assertNotIn('"item": "https://alefbet.tech/"', h)
        self.assertIn('"item": "https://alefbet.tech/en/"', h)
        self.assertNotIn('"item": "https://alefbet.tech/"', read("en/hanukkah-in-hebrew.html"))

    def test_landing_fonts_have_fallback(self):
        css = read("landing.css")
        for decl in re.findall(r"font:([^;}]*)", css):
            if "Manrope" in decl or "JetBrains" in decl:
                self.assertIn(",", decl, decl)

    def test_legal_pages_link_en(self):
        for p in ("support.html", "privacy.html", "terms.html"):
            h = read(p)
            self.assertNotRegex(h, r'href="index\.html', p)
            self.assertIn('href="en/index.html', h, p)


if __name__ == "__main__":
    unittest.main()
