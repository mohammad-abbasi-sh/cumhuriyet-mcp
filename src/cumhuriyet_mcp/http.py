"""HTTP layer for cumhuriyet_mcp.

cumhuriyet.com.tr serves its homepage, section pages (/<section>/:
turkiye, siyaset, ekonomi, dunya, spor, kultur-sanat, egitim,
saglik, yasam, magazin, otomobil), article pages
(/<section>/<slug>-<7-digit-id>) and the Google News sitemap
(/sitemaps/news.xml) fully server-rendered — no login, no API key,
no session cookies needed. Plain HTTP 200 with a browser UA
(verified live 2026-11-27). The transport still uses curl-cffi
Chrome impersonation, the same proven pattern as the other
Turkey-factory servers. Requests are kept gentle (one at a time,
~0.8s apart) and read-only.

Caveats found while probing (2026-11-27): the site's own search
(/arama/) is disallowed in robots.txt and returns a shell with no
results — keyword search here scans the news sitemap instead.
Section pages have no pagination ("Daha Fazla Göster" is
client-side); each carries ~38 items. There is no /son-dakika/
listing page (404) — latest news comes from the sitemap. The
columnist pages (/yazarlar/) expose no author/article links
server-side. teknoloji, bilim and gundem sections are 404.
"""
from __future__ import annotations

import time
from urllib.parse import quote

from curl_cffi import requests as _r

BASE = "https://www.cumhuriyet.com.tr"
TIMEOUT = 30.0
MIN_INTERVAL = 0.8  # seconds between requests — be polite

_HEADERS = {
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

_last_fetch = 0.0


class CumhuriyetError(RuntimeError):
    pass


_PROFILES = ("chrome120", "chrome131", "safari17_0")
_MAX_ATTEMPTS = 2  # one retry with the next profile
_RETRY_BACKOFF = 1.0  # seconds between attempts
_profile_idx = 0  # sticky: profile that last succeeded


def _request(url: str, headers: dict, timeout: float = TIMEOUT):
    """GET with fingerprint rotation.

    Starts at the sticky profile (chrome120 on a fresh process), retries
    once with the next profile on HTTP 403/429 or a transport error, then
    returns the last response (so the caller raises the specific 403/429
    error) or raises a network error if every attempt failed at the
    transport.
    """
    global _profile_idx
    last_exc: Exception | None = None
    for k in range(_MAX_ATTEMPTS):
        profile = _PROFILES[(_profile_idx + k) % len(_PROFILES)]
        try:
            resp = _r.get(url, impersonate=profile, headers=headers, timeout=timeout)
        except Exception as e:
            last_exc = e
            if k + 1 < _MAX_ATTEMPTS:
                time.sleep(_RETRY_BACKOFF)
                continue
            raise CumhuriyetError(f"network error fetching {url}: {e}") from e
        if resp.status_code in (403, 429):
            if k + 1 < _MAX_ATTEMPTS:
                time.sleep(_RETRY_BACKOFF)
                continue
            return resp
        _profile_idx = (_profile_idx + k) % len(_PROFILES)
        return resp
    raise CumhuriyetError(f"network error fetching {url}: {last_exc}") from last_exc


def _get(url: str) -> str:
    global _last_fetch
    wait = MIN_INTERVAL - (time.monotonic() - _last_fetch)
    if wait > 0:
        time.sleep(wait)
    try:
        resp = _request(url, _HEADERS)
    except CumhuriyetError:
        raise
    except Exception as e:
        raise CumhuriyetError(f"network error fetching {url}: {e}") from e
    finally:
        _last_fetch = time.monotonic()
    if resp.status_code == 403:
        raise CumhuriyetError(
            "cumhuriyet.com.tr refused the request (HTTP 403, bot wall) — try again later"
        )
    if resp.status_code == 429:
        raise CumhuriyetError(
            "cumhuriyet.com.tr rate-limited the request (HTTP 429) — try again later"
        )
    if resp.status_code in (404, 410):
        raise CumhuriyetError(
            f"page not found (HTTP {resp.status_code}): {url} — check the "
            "section / article URL"
        )
    if resp.status_code != 200:
        raise CumhuriyetError(f"unexpected HTTP {resp.status_code} fetching {url}")
    return resp.text


def fetch_home_html() -> str:
    return _get(f"{BASE}/")


def fetch_section_html(section: str) -> str:
    """Section listing: /<section>/ (turkiye, siyaset, ekonomi, ...)."""
    return _get(f"{BASE}/{quote(section)}/")


def fetch_news_sitemap_xml() -> str:
    """Google News sitemap: /sitemaps/news.xml (608 recent items)."""
    return _get(f"{BASE}/sitemaps/news.xml")


def fetch_article_html(article_url: str) -> str:
    """Article page (full URL or path)."""
    if article_url.startswith("http"):
        url = article_url
    else:
        url = f"{BASE}/{article_url.lstrip('/')}"
    if "cumhuriyet.com.tr" not in url:
        raise CumhuriyetError(f"not a cumhuriyet.com.tr URL: {article_url}")
    return _get(url)


def health_check() -> dict:
    """One polite probe of the source site.

    Returns {"status": "ok"|"blocked"|"error", "http_status": int|None,
    "url": ..., "detail": ...}. Used by the `cumhuriyet_health` tool
    and the daily smoke CI.
    """
    url = "https://www.cumhuriyet.com.tr/"
    try:
        fetch_home_html()
    except CumhuriyetError as e:
        msg = str(e)
        if "403" in msg:
            return {"status": "blocked", "http_status": 403, "url": url, "detail": msg}
        if "429" in msg:
            return {"status": "blocked", "http_status": 429, "url": url, "detail": msg}
        return {"status": "error", "http_status": None, "url": url, "detail": msg}
    return {"status": "ok", "http_status": 200, "url": url}
