# cumhuriyet-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/cumhuriyet-mcp

Unofficial **read-only** MCP server for **Cumhuriyet** (www.cumhuriyet.com.tr) — one of Türkiye's biggest national newspapers (founded 1924): **latest news** (from the Google News sitemap), **homepage headlines**, **headlines by section**, **full article text**, **keyword search**, and the **section list**.

> Part of the "Turkey MCP factory". Not affiliated with Cumhuriyet. Data comes from Cumhuriyet's own server-rendered pages and its Google News sitemap — no login, no API key, read-only.

## For AI agents

- **Latest news**: `cumhuriyet_latest_news` returns the newest items from `/sitemaps/news.xml` (608 newest items, title, publication time, section, URL), newest first.
- **Headlines**: `cumhuriyet_headlines` returns the top stories on the homepage right now (title, URL, summary when the listing carries one, section) — including the day's columnist pieces.
- **Section news**: `cumhuriyet_section_news` takes a section — `"turkiye"` (default), `"siyaset"`, `"ekonomi"`, `"dunya"`, `"spor"`, `"kultur-sanat"`, `"egitim"`, `"saglik"`, `"yasam"`, `"magazin"`, `"otomobil"` — and returns ~38 headlines per section (title, URL, summary).
- **Article**: `cumhuriyet_get_article` takes a full cumhuriyet.com.tr URL and returns title, author, publish/modify dates, description, image, word count and the full body text (from the page's NewsArticle JSON-LD).
- **Search**: `cumhuriyet_search_news` scans the titles of the 608 newest items in the Google News sitemap by keyword — `"emekli"`, `"deprem"`, `"dolar"` — Turkish-aware (dotted/dotless I handled, so `"İSTANBUL"` matches `"İstanbul"`).
- **Sections**: `cumhuriyet_list_sections` returns the sections usable with `cumhuriyet_section_news`, with Turkish display names.
- Every response carries `fetched_at` (UTC) and `source: cumhuriyet.com.tr`.

## Install

```bash
uvx cumhuriyet-mcp
```

Or add to your MCP client config (e.g. Claude Desktop):

```json
{
  "mcpServers": {
    "cumhuriyet": {
      "command": "uvx",
      "args": ["cumhuriyet-mcp"]
    }
  }
}
```

## Tools

| Tool | What it does |
| --- | --- |
| `cumhuriyet_latest_news` | Latest news from the Google News sitemap, newest first |
| `cumhuriyet_headlines` | Top stories on the homepage right now |
| `cumhuriyet_section_news` | Headlines in one section |
| `cumhuriyet_get_article` | Full text of one article (full URL) |
| `cumhuriyet_search_news` | Keyword search over the 608 newest sitemap titles |
| `cumhuriyet_list_sections` | News sections usable with `cumhuriyet_section_news` |
| `cumhuriyet_health` | Is cumhuriyet.com.tr reachable right now? |

## Example

Latest news, 27 November 2026:

```json
{ "count": 2,
  "articles": [
    { "published_at": "2026-11-27T12:19:00+03:00", "section": "turkiye",
      "title": "Soma ve Kangal işçilerinden Konya’da hak arayışı: '1,4 milyar lira alacağımız var'",
      "url": "https://www.cumhuriyet.com.tr/turkiye/soma-ve-kangal-iscilerinden-konya-da-hak-arayisi-1-4-milyar-lira-alacagimiz-var-2559885" },
    { "published_at": "2026-11-27T12:18:00+03:00", "section": "spor",
      "title": "TFF resmen duyurdu: Süper Lig yayın ihalesinin tarihi belli oldu",
      "url": "https://www.cumhuriyet.com.tr/spor/tff-resmen-duyurdu-super-lig-yayin-ihalesinin-tarihi-belli-oldu-2559884" } ] }
```

An article, 27 November 2026:

```json
{ "title": "Soma ve Kangal işçilerinden Konya’da hak arayışı: '1,4 milyar lira alacağımız var'",
  "author": "ANKA",
  "date_published": "2026-11-27T12:19:00+03:00",
  "section": "Türkiye", "word_count": 299,
  "body": "Manisa’nın Soma ve Sivas’ın Kangal ilçelerindeki termik santrallerde çalışan işçiler, ücret ve diğer alacaklarının ödenmesi, iş güvencelerinin sağlanması için Konya’da eylem yaptı. …" }
```

## Caveats

- Search is a **scan of the 608 newest titles in the Google News sitemap**, not a full-archive search: the site's own search (`/arama/`) is disallowed in robots.txt and returns no results, so there is no search API to call.
- Section pages have **no pagination** ("Daha Fazla Göster" is client-side) — each carries ~38 items, so `cumhuriyet_section_news` sees the current page only.
- There is **no `/son-dakika/` listing page** (404) — latest news comes from the sitemap instead.
- Listing titles are the site's **display titles**, which can differ slightly from the article headline (e.g. the Türkiye listing shows "Soma ve Kangal işçileri eylemde..." while the article headline is "Soma ve Kangal işçilerinden Konya’da hak arayışı..."); `cumhuriyet_get_article` returns the real headline.
- The site's `wordCount` field equals the articleBody **character** count, not words — the `word_count` returned here is computed from the body text.
- **Video** (`/video/`), **gallery** (`/galeri/`) and **games** (`/oyun/`) pages are not text news and are excluded from listings. Columnist pieces (`/yazarlar/<author>/...`) are included in listings; the columnist index pages themselves expose no article links server-side.
- Article bodies come from the page's NewsArticle JSON-LD (`articleBody`, one plain-text block); if a page has no JSON-LD, the HTML paragraphs are used as a fallback.
- Transport uses Chrome TLS impersonation; requests are spaced ~0.8s apart.

## Development

```bash
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/test_news.py -v    # offline, recorded fixtures
.venv/bin/python -m pytest tests/test_live.py -v    # live, against www.cumhuriyet.com.tr
.venv/bin/python tests/smoke_live.py                # daily CI probe
```

## License

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — free for personal and non-commercial use; commercial use needs a separate license.

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
