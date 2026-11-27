"""Offline tests for cumhuriyet_mcp.news — recorded real cumhuriyet.com.tr pages.

Fixtures are real pages fetched 2026-11-27 (plain curl, browser UA):
- homepage.html: / (139 deduped article links incl. 13 columnist
  pieces; titles split across fragments are joined).
- section-turkiye.html: /turkiye/ (38 articles, all with summaries;
  display title repeats as img alt + title anchor).
- section-ekonomi.html: /ekonomi/ (38 articles, all with summaries).
- news.xml: /sitemaps/news.xml (608 items, newest first; first is
  the Soma/Kangal story, 2026-11-27T12:19:00+03:00).
- article.html: son-dakika drug-probe story 2559822 (DHA, published
  2026-11-27T09:26:00+03:00, 74 words; the site's wordCount field
  says 591 — that is the articleBody CHARACTER count).
- article-turkiye.html: Soma/Kangal story 2559885 (ANKA, published
  2026-11-27T12:19:00+03:00, 299 words).
"""
import os
import unittest

from cumhuriyet_mcp import news as N

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _read(name: str) -> str:
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


class TestListingParse(unittest.TestCase):
    def test_homepage(self):
        rows = N.parse_listing(_read("homepage.html"))
        self.assertEqual(len(rows), 139)
        self.assertEqual(
            rows[0]["title"],
            "TFF resmen duyurdu Süper Lig yayın ihalesinin tarihi belli oldu",
        )
        self.assertEqual(rows[0]["section"], "spor")
        self.assertTrue(rows[0]["url"].endswith("-2559884"))

    def test_homepage_columnists(self):
        rows = N.parse_listing(_read("homepage.html"))
        cols = [r for r in rows if r.get("section") == "yazarlar"]
        self.assertEqual(len(cols), 13)
        self.assertEqual(cols[0]["title"], "Muhalefetin kurgulanması")
        self.assertTrue(cols[0]["url"].endswith("-2559745"))

    def test_turkiye(self):
        rows = N.parse_listing(_read("section-turkiye.html"))
        self.assertEqual(len(rows), 38)
        first = rows[0]
        self.assertEqual(
            first["title"],
            "Soma ve Kangal işçileri eylemde... '1,4 milyar lira alacağımız var'",
        )
        self.assertTrue(first["url"].endswith("-2559885"))
        self.assertIn("Konya", first["summary"])
        self.assertEqual(first["section"], "turkiye")

    def test_ekonomi(self):
        rows = N.parse_listing(_read("section-ekonomi.html"))
        self.assertEqual(len(rows), 38)
        self.assertIn("Emekli zammı", rows[0]["title"])
        self.assertEqual(rows[0]["section"], "ekonomi")

    def test_all_summaries(self):
        for name in ("section-turkiye.html", "section-ekonomi.html"):
            for r in N.parse_listing(_read(name)):
                self.assertIn("summary", r)
                self.assertGreater(len(r["summary"]), 50)

    def test_all_have_url_title(self):
        for name in ("homepage.html", "section-turkiye.html",
                     "section-ekonomi.html"):
            for r in N.parse_listing(_read(name)):
                self.assertIn("cumhuriyet.com.tr", r["url"])
                self.assertTrue(r["title"])
                self.assertNotIn("/galeri/", r["url"])
                self.assertNotIn("/video/", r["url"])
                self.assertNotIn("/oyun/", r["url"])


class TestSitemapParse(unittest.TestCase):
    def test_count_and_order(self):
        rows = N.parse_news_sitemap(_read("news.xml"))
        self.assertEqual(len(rows), 608)
        first = rows[0]
        self.assertEqual(
            first["title"],
            "Soma ve Kangal işçilerinden Konya’da hak arayışı: "
            "'1,4 milyar lira alacağımız var'",
        )
        self.assertEqual(first["published_at"], "2026-11-27T12:19:00+03:00")
        self.assertEqual(first["section"], "turkiye")
        self.assertTrue(first["url"].endswith("-2559885"))

    def test_newest_first(self):
        rows = N.parse_news_sitemap(_read("news.xml"))
        self.assertGreaterEqual(
            rows[0]["published_at"], rows[1]["published_at"]
        )
        self.assertEqual(rows[1]["section"], "spor")

    def test_sections_cover_sitemap_taxonomy(self):
        rows = N.parse_news_sitemap(_read("news.xml"))
        sections = {r.get("section") for r in rows}
        self.assertIn("astroloji", sections)
        self.assertIn("yazarlar", sections)
        self.assertIn("ekonomi", sections)

    def test_all_have_url_title_date(self):
        for r in N.parse_news_sitemap(_read("news.xml")):
            self.assertIn("cumhuriyet.com.tr", r["url"])
            self.assertTrue(r["title"])
            self.assertRegex(r["published_at"], r"^\d{4}-\d{2}-\d{2}T")


class TestArticleParse(unittest.TestCase):
    def setUp(self):
        self.a = N.parse_article(_read("article.html"))

    def test_core(self):
        self.assertEqual(
            self.a["title"],
            "Son Dakika... Ünlülere uyuşturucu soruşturmasında yeni gelişme: "
            "3 isim tutuklandı",
        )
        self.assertEqual(self.a["author"], "DHA")
        self.assertEqual(self.a["date_published"], "2026-11-27T09:26:00+03:00")
        self.assertEqual(self.a["date_modified"], "2026-11-27T09:43:46+03:00")
        self.assertEqual(self.a["section"], "Türkiye")
        # Real word count (the site's wordCount field = 591 chars).
        self.assertEqual(self.a["word_count"], 74)

    def test_body(self):
        self.assertIn("Muammer Kapucuoğlu", self.a["body"])
        self.assertIn("adli kontrol", self.a["body"])

    def test_image_and_url(self):
        self.assertTrue(
            self.a["image"].startswith("https://media.cumhuriyet.com.tr/")
        )
        self.assertTrue(self.a["url"].endswith("-2559822"))

    def test_turkiye_article(self):
        b = N.parse_article(_read("article-turkiye.html"))
        self.assertEqual(b["author"], "ANKA")
        self.assertEqual(b["section"], "Türkiye")
        self.assertEqual(b["word_count"], 299)
        self.assertIn("Soma", b["body"])
        self.assertTrue(b["url"].endswith("-2559885"))

    def test_no_body(self):
        with self.assertRaises(ValueError):
            N.parse_article("<html><body>no article here</body></html>")


class TestTrHelpers(unittest.TestCase):
    def test_tr_lower(self):
        self.assertEqual(N.tr_lower("İstanbul"), "istanbul")
        self.assertEqual(N.tr_lower("IĞDIR"), "ığdır")
        self.assertEqual(N.tr_lower("Şoför"), "şoför")

    def test_tr_title(self):
        self.assertEqual(N.tr_title("AKTÜALİTE"), "Aktüalite")
        self.assertEqual(N.tr_title("EKONOMİ"), "Ekonomi")
        self.assertEqual(N.tr_title("GÜNDEM"), "Gündem")


if __name__ == "__main__":
    unittest.main()
