"""MCP server: unofficial read-only access to cumhuriyet.com.tr news."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import http as _http
from . import news as _N

mcp = FastMCP("cumhuriyet-mcp")

INSTRUCTIONS = """\
Unofficial read-only MCP server for cumhuriyet.com.tr, one of
Türkiye's biggest national newspapers (founded 1924) — latest news,
homepage headlines, headlines by section, full article text,
keyword search, and the section list. Data comes from the site's
server-rendered pages and its Google News sitemap — no login, no
API key. The sitemap (/sitemaps/news.xml) lists the 608 newest
items with titles and publication times and is the source for
latest news and search (the site's own /arama/ search is
disallowed in robots.txt and returns no results). Section pages
(/<section>/: turkiye, siyaset, ekonomi, dunya, spor, kultur-sanat,
egitim, saglik, yasam, magazin, otomobil) list ~38 headlines each
with no pagination. There is no /son-dakika/ listing page.
Article pages carry a full NewsArticle JSON-LD block (title,
author, publish/modify dates, description, full body text). The
site's "wordCount" field is a character count, not words — the
word_count returned here is computed from the body. Read-only;
transport uses Chrome TLS impersonation; requests are spaced
~0.8s apart.
Built by Mohammad Abbasi (mohammad-abbasi-sh) — https://almanibama.ir · https://mabbasi.ir — Turkey MCP factory.\
"""


_SOURCE = "cumhuriyet.com.tr"
_DISCLAIMER = "Unofficial read-only data from cumhuriyet.com.tr; verify on the site before acting on it."


def _envelope() -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": _SOURCE,
        "disclaimer": _DISCLAIMER,
    }


def _ok(payload: dict) -> str:
    return json.dumps({**_envelope(), **payload}, ensure_ascii=False)


def _err(e: Exception) -> str:
    return _ok({"error": str(e)})


def _validate_limit(limit: int, lo: int = 1, hi: int = 30) -> int:
    if not lo <= limit <= hi:
        raise ValueError(f"limit must be between {lo} and {hi}")
    return limit


@mcp.tool()
def cumhuriyet_latest_news(limit: int = 10) -> str:
    """Latest Cumhuriyet news, newest first, from the site's Google
    News sitemap (608 newest items). limit 1..30. Returns items
    (title, article URL, publication time, section)."""
    try:
        _validate_limit(limit)
        rows = _N.parse_news_sitemap(_http.fetch_news_sitemap_xml())
    except (ValueError, _http.CumhuriyetError) as e:
        return _err(e)
    return _ok({"count": min(limit, len(rows)), "articles": rows[:limit]})


@mcp.tool()
def cumhuriyet_headlines(limit: int = 10) -> str:
    """Top stories on the Cumhuriyet homepage right now. limit 1..30.
    Returns headlines (title, article URL, summary when the listing
    carries one, section)."""
    try:
        _validate_limit(limit)
        rows = _N.parse_listing(_http.fetch_home_html())
    except (ValueError, _http.CumhuriyetError) as e:
        return _err(e)
    return _ok({"count": min(limit, len(rows)), "headlines": rows[:limit]})


@mcp.tool()
def cumhuriyet_section_news(section: str = "turkiye", limit: int = 10) -> str:
    """Headlines in one Cumhuriyet section. section: "turkiye"
    (default), "siyaset", "ekonomi", "dunya", "spor",
    "kultur-sanat", "egitim", "saglik", "yasam", "magazin",
    "otomobil". limit 1..30. Returns headlines (title, article URL,
    summary when the listing carries one)."""
    try:
        section = (section or "turkiye").strip().lower()
        if section not in _N.SECTIONS:
            raise ValueError(
                f"section must be one of {', '.join(_N.SECTIONS)}"
            )
        _validate_limit(limit)
        rows = _N.parse_listing(_http.fetch_section_html(section))
    except (ValueError, _http.CumhuriyetError) as e:
        return _err(e)
    return _ok({
            "section": section,
            "count": min(limit, len(rows)),
            "headlines": rows[:limit],
        })


@mcp.tool()
def cumhuriyet_get_article(article_url: str) -> str:
    """Full text of one Cumhuriyet article. article_url: the
    article's cumhuriyet.com.tr URL (as returned by the latest /
    headlines / section / search tools, e.g.
    "https://www.cumhuriyet.com.tr/turkiye/soma-ve-kangal-iscilerinden-konya-da-hak-arayisi-1-4-milyar-lira-alacagimiz-var-2559885").
    A bare 7-digit article id is also accepted. Returns title,
    author, publish/modify dates, description, image, word count
    and the full body text."""
    try:
        if not article_url or not article_url.strip():
            raise ValueError("article_url must not be empty")
        url = article_url.strip()
        if re.fullmatch(r"\d{7}", url):
            raise ValueError(
                "a bare article id is not enough — pass the full "
                "article URL (the id alone does not resolve to a page)"
            )
        html_text = _http.fetch_article_html(url)
        data = _N.parse_article(html_text)
    except (ValueError, _http.CumhuriyetError) as e:
        return _err(e)
    return _ok(data)


@mcp.tool()
def cumhuriyet_search_news(query: str, limit: int = 10) -> str:
    """Keyword search over the newest Cumhuriyet news: scans the
    titles of the 608 newest items in the site's Google News
    sitemap, matching the keyword in titles (Turkish-aware).
    query: e.g. "emekli", "deprem", "dolar". limit 1..30. Note: the
    site's own /arama/ search is disallowed in robots.txt and
    returns no results, so this searches the sitemap titles
    instead of a search backend."""
    try:
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        _validate_limit(limit)
        q = _N.tr_lower(query.strip())
        rows = [
            r for r in _N.parse_news_sitemap(_http.fetch_news_sitemap_xml())
            if q in _N.tr_lower(r["title"])
        ]
    except (ValueError, _http.CumhuriyetError) as e:
        return _err(e)
    return _ok({"query": query.strip(),
         "count": min(limit, len(rows)), "articles": rows[:limit]})


@mcp.tool()
def cumhuriyet_list_sections() -> str:
    """Cumhuriyet news sections usable with cumhuriyet_section_news,
    with their Turkish display names. No arguments."""
    return _ok({
        "sections": [
            {"slug": slug, "name": _N.SECTION_NAMES[slug]}
            for slug in _N.SECTIONS
        ],
    })


@mcp.tool()
def cumhuriyet_health() -> str:
    """Check whether cumhuriyet.com.tr is reachable right now.

    Returns status ok (HTTP 200), blocked (HTTP 403/429 — bot wall or
    rate limit) or error, plus the HTTP status and the probed URL.
    One polite request; it does not fetch any listings."""
    return _ok(_http.health_check())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
