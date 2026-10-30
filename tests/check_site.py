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


if __name__ == "__main__":
    unittest.main()
