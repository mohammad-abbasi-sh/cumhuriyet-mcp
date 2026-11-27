"""Stdlib parsing for cumhuriyet.com.tr server-rendered news pages.

Verified live 2026-11-27 against real pages (fixtures in tests/):
- Homepage (553KB): 139 deduped article links. Each article appears
  in several anchors; the title is split across short text fragments
  inside one anchor (e.g. ['TFF resmen duyurdu', 'Süper Lig yayın
  ihalesinin tarihi belli oldu']) — joined with a space. Image alts
  are empty on the homepage.
- Section pages (/turkiye/ 331KB, /ekonomi/ 332KB): ~38 unique
  articles each; every article has 3 anchors — an image anchor
  (alt = display title), a title anchor (display title text) and a
  summary anchor (longer description text). No <strong> tags. No
  pagination ("Daha Fazla Göster" is client-side). Article hrefs are
  /<section>/<slug>-<7-digit-id>.
- Google News sitemap (/sitemaps/news.xml, 316KB): 608 items, newest
  first, each with <loc>, <news:title> and <news:publication_date>.
  This is the source for latest news and for keyword search (the
  site's own /arama/ is disallowed in robots.txt and returns a
  shell with no results).
- Article pages (~300KB): full NewsArticle JSON-LD (headline,
  description, author as a list of Person dicts, dateCreated/
  datePublished/dateModified, articleSection, articleBody as one
  plain-text block). The site's "wordCount" field equals the
  articleBody CHARACTER count, not words — real word count is
  computed from the body here. No image/keywords in the JSON-LD;
  og:image is taken from the page meta instead.
- No /son-dakika/ listing page (404) — breaking news is the newest
  sitemap entries. Columnist pages (/yazarlar/, /yazarlar/*) expose
  no author/article links server-side, so there is no columnist
  tool in v1.
"""
from __future__ import annotations

import html
import json
import re

# Sections verified live 2026-11-27 (HTTP 200). teknoloji, bilim and
# gundem are 404 on this site.
SECTIONS = (
    "turkiye", "siyaset", "ekonomi", "dunya", "spor",
    "kultur-sanat", "egitim", "saglik", "yasam", "magazin", "otomobil",
)

SECTION_NAMES = {
    "turkiye": "Türkiye",
    "siyaset": "Siyaset",
    "ekonomi": "Ekonomi",
    "dunya": "Dünya",
    "spor": "Spor",
    "kultur-sanat": "Kültür Sanat",
    "egitim": "Eğitim",
    "saglik": "Sağlık",
    "yasam": "Yaşam",
    "magazin": "Magazin",
    "otomobil": "Otomobil",
}

_TR_UPPER_TO_LOWER = str.maketrans({
    "İ": "i", "I": "ı", "Ş": "ş", "Ğ": "ğ",
    "Ü": "ü", "Ö": "ö", "Ç": "ç",
})


def tr_lower(s: str) -> str:
    """Turkish-aware lowercase (str.lower() mangles İ -> i + dot)."""
    return s.translate(_TR_UPPER_TO_LOWER).lower()


def tr_title(s: str) -> str:
    """Turkish-aware title case for one word (str.title() mangles İ)."""
    s = tr_lower(s.strip())
    return s[:1].upper() + s[1:] if s else s


def _clean(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------- listings

# Anything under these path segments is not a text news article.
# NOTE: /yazarlar/<author>/<slug>-<id> columnist pieces ARE text
# articles and are included — only the /yazarlar/ index and group
# pages (no -<id> suffix) never match the article regex.
_SKIP_SEGMENTS = ("/galeri/", "/video/", "/oyun/")

_ARTICLE_RE = re.compile(
    r'<a\b[^>]*href="(https?://www\.cumhuriyet\.com\.tr/[a-z-]+/[^"]+?-\d{7})"[^>]*>(.*?)</a>',
    re.S,
)


def parse_listing(html_text: str) -> list[dict]:
    """Article links on a listing page (homepage or /<section>/) ->
    [{url, title, summary?, section}].

    Each article appears in several anchors: an image anchor (img
    alt = display title), a title anchor (display title text) and,
    on section pages, a summary anchor (longer description text).
    On the homepage the title is split across short text fragments
    inside one anchor. So all snippets are collected per URL first,
    then the title is derived: the snippet that repeats (alt +
    title anchor) wins; otherwise a long snippet is the summary and
    the remaining fragments join into the title.
    """
    snippets: dict[str, list[str]] = {}
    order: list[str] = []
    for href, inner in _ARTICLE_RE.findall(html_text):
        if any(seg in href for seg in _SKIP_SEGMENTS):
            continue
        texts: list[str] = []
        alt = re.search(r'<img\b[^>]*alt="([^"]*)"', inner)
        if alt and alt.group(1).strip():
            texts.append(_clean(alt.group(1)))
        raw = html.unescape(re.sub(r"<[^>]+>", "\n", inner))
        for ln in raw.split("\n"):
            ln = ln.strip()
            if ln:
                texts.append(_clean(ln))
        if not texts:
            continue  # image anchor with empty alt; text anchor carries it
        if href not in snippets:
            snippets[href] = []
            order.append(href)
        snippets[href].extend(texts)

    rows: list[dict] = []
    for href in order:
        texts = snippets[href]
        counts: dict[str, int] = {}
        uniq: list[str] = []
        for t in texts:
            if t not in counts:
                counts[t] = 1
                uniq.append(t)
            else:
                counts[t] += 1
        repeated = [t for t in uniq if counts[t] >= 2]
        if repeated:
            title = max(repeated, key=len)
            others = [
                t for t in uniq
                if t != title and len(t) >= 80 and len(t) > 1.5 * len(title)
            ]
            row: dict = {"url": href, "title": title}
            if others:
                row["summary"] = max(others, key=len)[:400]
        elif len(uniq) >= 2 and len(uniq[-1]) >= 100 and len(uniq[-1]) > 2 * len(uniq[0]):
            title, summary = uniq[0], max(uniq, key=len)
            row = {"url": href, "title": title}
            if summary != title:
                row["summary"] = summary[:400]
        else:
            row = {"url": href, "title": " ".join(uniq)}
        section = href.split("/")[3] if href.count("/") >= 3 else ""
        if re.fullmatch(r"[a-z0-9-]+", section or ""):
            row["section"] = section
        rows.append(row)
    return rows


# ---------------------------------------------------------------- news sitemap

_NS = {
    "s": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "n": "http://www.google.com/schemas/sitemap-news/0.9",
}


def parse_news_sitemap(xml_text: str) -> list[dict]:
    """Google News sitemap -> [{url, title, published_at, section}]
    in sitemap order (newest first). Parsed with ElementTree — the
    entries carry optional extra elements (e.g. news:keywords)
    between publication_date and title, so a flat regex misses some.
    """
    import xml.etree.ElementTree as ET

    xml_text = xml_text.lstrip("\ufeff")
    root = ET.fromstring(xml_text)
    rows: list[dict] = []
    for url_el in root.findall("s:url", _NS):
        loc_el = url_el.find("s:loc", _NS)
        news_el = url_el.find("n:news", _NS)
        if loc_el is None or loc_el.text is None or news_el is None:
            continue
        loc = loc_el.text.strip()
        if any(seg in loc for seg in _SKIP_SEGMENTS):
            continue
        title_el = news_el.find("n:title", _NS)
        date_el = news_el.find("n:publication_date", _NS)
        row = {
            "url": loc,
            "title": _clean(title_el.text) if title_el is not None else "",
            "published_at": date_el.text.strip()
            if date_el is not None and date_el.text else "",
        }
        if not row["title"]:
            continue
        parts = loc.split("/")
        if len(parts) >= 4 and re.fullmatch(r"[a-z0-9-]+", parts[3]):
            row["section"] = parts[3]
        rows.append(row)
    return rows


# ---------------------------------------------------------------- article

def parse_article(html_text: str) -> dict:
    """Article page -> title, author, dates, description, image,
    body (full text), word_count, section, url."""
    for m in re.finditer(
        r'<script type="application/ld\+json">(.*?)</script>',
        html_text, re.S,
    ):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "NewsArticle":
            return _article_from_jsonld(data, html_text)
    # Fallback: h1 + the property="articleBody" div.
    return _article_from_html(html_text)


def _article_from_jsonld(data: dict, html_text: str) -> dict:
    out: dict = {}
    out["title"] = _clean(data.get("headline"))
    out["description"] = _clean(data.get("description"))
    author = data.get("author")
    names: list[str] = []
    if isinstance(author, list):
        for a in author:
            if isinstance(a, dict) and a.get("name"):
                names.append(_clean(a["name"]))
            elif isinstance(a, str):
                names.append(_clean(a))
    elif isinstance(author, dict) and author.get("name"):
        names.append(_clean(author["name"]))
    elif isinstance(author, str):
        names.append(_clean(author))
    if names:
        out["author"] = ", ".join(names)
    out["date_published"] = data.get("datePublished") or ""
    out["date_modified"] = data.get("dateModified") or ""
    img = re.search(
        r'<meta[^>]+property="og:image"[^>]+content="([^"]*)"', html_text
    )
    if img:
        out["image"] = html.unescape(img.group(1))
    out["section"] = _clean(data.get("articleSection"))
    page = data.get("mainEntityOfPage")
    if isinstance(page, dict) and page.get("@id"):
        out["url"] = page["@id"]
    elif isinstance(page, str):
        out["url"] = page
    body = data.get("articleBody")
    if not body or not str(body).strip():
        raise ValueError("article has no body text (articleBody empty)")
    out["body"] = re.sub(r"\s+", " ", str(body)).strip()
    # NOTE: the site's wordCount field equals len(articleBody) in
    # characters, not words — compute the real word count instead.
    out["word_count"] = len(out["body"].split())
    return {k: v for k, v in out.items() if v not in (None, "", [])}


def _article_from_html(html_text: str) -> dict:
    out: dict = {}
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.S)
    if m:
        out["title"] = _clean(m.group(1))
    if not out.get("title"):
        m = re.search(r"<title>(.*?)</title>", html_text, re.S)
        if m:
            out["title"] = _clean(m.group(1)).split(" | Cumhuriyet")[0]

    def _meta(name: str) -> str | None:
        mm = re.search(
            rf'<meta[^>]+(?:property|name)="{re.escape(name)}"[^>]+content="([^"]*)"',
            html_text,
        )
        return html.unescape(mm.group(1)) if mm else None

    out["description"] = _meta("description") or _meta("og:description") or ""
    out["image"] = _meta("og:image") or ""
    m = re.search(r'<link rel="canonical" href="([^"]+)"', html_text)
    if m:
        out["url"] = m.group(1)
    m = re.search(r"<time[^>]*>([^<]+)</time>", html_text)
    if m:
        out["date_modified"] = _clean(m.group(1))

    i = html_text.find('property="articleBody"')
    if i < 0:
        raise ValueError("no article body found on this page")
    region = html_text[i:i + 120000]
    paras = []
    for pm in re.finditer(r"<p[^>]*>(.*?)</p>", region, re.S):
        text = _clean(pm.group(1))
        if text:
            paras.append(text)
    if not paras:
        raise ValueError("no article body paragraphs found on this page")
    out["body"] = "\n\n".join(paras)
    out["word_count"] = len(out["body"].split())
    out["paragraph_count"] = len(paras)
    return {k: v for k, v in out.items() if v not in (None, "")}
