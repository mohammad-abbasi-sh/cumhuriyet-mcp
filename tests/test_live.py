"""Live tests for cumhuriyet_mcp — real requests to cumhuriyet.com.tr.

Requires network + Chrome TLS impersonation (curl-cffi). The server
is polite by design (~0.8s between requests), so this file takes
~20s. Run: python -m unittest discover -s tests -v

Headlines change during the day; tests assert structure and sane
ranges, not exact titles.
"""
import unittest

from cumhuriyet_mcp import http as H
from cumhuriyet_mcp import news as N


class TestLiveSections(unittest.TestCase):
    def test_turkiye(self):
        html_text = H.fetch_section_html("turkiye")
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 20)
        self.assertIn("cumhuriyet.com.tr", rows[0]["url"])

    def test_ekonomi(self):
        html_text = H.fetch_section_html("ekonomi")
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 20)

    def test_spor(self):
        html_text = H.fetch_section_html("spor")
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 10)

    def test_unknown_section_404(self):
        with self.assertRaises(H.CumhuriyetError):
            H.fetch_section_html("xyzabcqwerty")


class TestLiveLatest(unittest.TestCase):
    def test_news_sitemap(self):
        xml_text = H.fetch_news_sitemap_xml()
        rows = N.parse_news_sitemap(xml_text)
        self.assertGreater(len(rows), 100)
        self.assertTrue(rows[0]["title"])
        self.assertRegex(rows[0]["published_at"], r"^\d{4}-\d{2}-\d{2}T")

    def test_homepage(self):
        html_text = H.fetch_home_html()
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 50)
        self.assertIn("cumhuriyet.com.tr", rows[0]["url"])


class TestLiveArticle(unittest.TestCase):
    def test_known_article(self):
        html_text = H.fetch_article_html(
            "https://www.cumhuriyet.com.tr/turkiye/soma-ve-kangal-iscilerinden-"
            "konya-da-hak-arayisi-1-4-milyar-lira-alacagimiz-var-2559885"
        )
        a = N.parse_article(html_text)
        self.assertIn("Soma", a["title"])
        self.assertEqual(a["author"], "ANKA")
        self.assertGreater(a["word_count"], 100)

    def test_unknown_article_404(self):
        with self.assertRaises(H.CumhuriyetError):
            H.fetch_article_html(
                "https://www.cumhuriyet.com.tr/turkiye/boyle-bir-haber-yok-0000000"
            )


class TestLiveHealth(unittest.TestCase):
    def test_health_ok(self):
        result = H.health_check()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["http_status"], 200)


if __name__ == "__main__":
    unittest.main()
