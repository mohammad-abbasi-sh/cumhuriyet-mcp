# cumhuriyet-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/cumhuriyet-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای **جمهوریت** (www.cumhuriyet.com.tr) — یکی از بزرگ‌ترین روزنامه‌های ملی ترکیه (از ۱۹۲۴): **تازه‌ترین خبرها** (از نقشهٔ سایت Google News)، **تیترهای صفحهٔ اصلی**، **تیترهای هر بخش**، **متن کامل خبرها**، **جست‌وجوی کلیدواژه** و **فهرست بخش‌ها**.

> بخشی از پروژهٔ «کارخانهٔ MCP ترکیه». وابسته به جمهوریت نیست. داده‌ها از صفحه‌های عمومی خود سایت و نقشهٔ سایت Google News گرفته می‌شود — بدون ورود، بدون کلید API، فقط‌خواندنی.

## برای عامل‌های هوش مصنوعی

- **تازه‌ترین خبرها**: `cumhuriyet_latest_news` تازه‌ترین خبرها را از `/sitemaps/news.xml` برمی‌گرداند (۶۰۸ مورد تازه، تیتر، زمان انتشار، بخش، نشانی)، از تازه‌ترین به قدیمی‌ترین.
- **تیترها**: `cumhuriyet_headlines` تیترهای برتر صفحهٔ اصلی را همین حالا برمی‌گرداند (تیتر، نشانی، خلاصه در صورت وجود، بخش) — شامل ستون‌های روز.
- **خبرهای بخش**: `cumhuriyet_section_news` یک بخش می‌گیرد — `"turkiye"` (پیش‌فرض)، `"siyaset"`، `"ekonomi"`، `"dunya"`، `"spor"`، `"kultur-sanat"`، `"egitim"`، `"saglik"`، `"yasam"`، `"magazin"`، `"otomobil"` — و برای هر بخش حدود ۳۸ تیتر برمی‌گرداند (تیتر، نشانی، خلاصه).
- **متن خبر**: `cumhuriyet_get_article` نشانی کامل یک خبر جمهوریت را می‌گیرد و تیتر، نویسنده، تاریخ انتشار/به‌روزرسانی، توضیح، تصویر، تعداد کلمات و متن کامل را برمی‌گرداند (از بلوک NewsArticle JSON-LD صفحه).
- **جست‌وجو**: `cumhuriyet_search_news` تیترهای ۶۰۸ مورد تازهٔ نقشهٔ سایت Google News را با کلیدواژه می‌گردد — `"emekli"`، `"deprem"`، `"dolar"` — با حساسیت به ترکی (I نقطه‌دار/بی‌نقطه درست مدیریت می‌شود؛ `"İSTANBUL"` با `"İstanbul"` هم‌خوانی دارد).
- **بخش‌ها**: `cumhuriyet_list_sections` بخش‌های قابل‌استفاده با `cumhuriyet_section_news` را با نام ترکی برمی‌گرداند.
- هر پاسخ `fetched_at` (UTC) و `source: cumhuriyet.com.tr` دارد.

## نصب

```bash
uvx cumhuriyet-mcp
```

یا به تنظیمات کلاینت MCP خود اضافه کنید (مثلاً Claude Desktop):

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

## ابزارها

| ابزار | چه می‌کند |
| --- | --- |
| `cumhuriyet_latest_news` | تازه‌ترین خبرها از نقشهٔ سایت Google News، از تازه‌ترین به قدیمی‌ترین |
| `cumhuriyet_headlines` | تیترهای برتر صفحهٔ اصلی همین حالا |
| `cumhuriyet_section_news` | تیترهای یک بخش |
| `cumhuriyet_get_article` | متن کامل یک خبر (نشانی کامل) |
| `cumhuriyet_search_news` | جست‌وجوی کلیدواژه در ۶۰۸ تیتر تازهٔ نقشهٔ سایت |
| `cumhuriyet_list_sections` | بخش‌های خبری قابل‌استفاده با `cumhuriyet_section_news` |
| `cumhuriyet_health` | آیا cumhuriyet.com.tr همین حالا در دسترس است؟ |

## نمونه

تازه‌ترین خبرها، ۲۷ نوامبر ۲۰۲۶:

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

یک خبر، ۲۷ نوامبر ۲۰۲۶:

```json
{ "title": "Soma ve Kangal işçilerinden Konya’da hak arayışı: '1,4 milyar lira alacağımız var'",
  "author": "ANKA",
  "date_published": "2026-11-27T12:19:00+03:00",
  "section": "Türkiye", "word_count": 299,
  "body": "Manisa’nın Soma ve Sivas’ın Kangal ilçelerindeki termik santrallerde çalışan işçiler, ücret ve diğer alacaklarının ödenmesi, iş güvencelerinin sağlanması için Konya’da eylem yaptı. …" }
```

## نکته‌ها

- جست‌وجو **پویش ۶۰۸ تیتر تازهٔ نقشهٔ سایت Google News** است، نه جست‌وجوی کامل بایگانی: جست‌وجوی خود سایت (`/arama/`) در robots.txt ممنوع است و نتیجه‌ای برنمی‌گرداند، پس API جست‌وجویی برای فراخوانی نیست.
- صفحه‌های بخش **صفحه‌بندی ندارند** («Daha Fazla Göster» سمت کاربر است) — هر کدام حدود ۳۸ مورد دارند، پس `cumhuriyet_section_news` فقط صفحهٔ جاری را می‌بیند.
- **صفحهٔ فهرست `/son-dakika/` وجود ندارد** (۴۰۴) — تازه‌ترین خبرها به‌جای آن از نقشهٔ سایت می‌آیند.
- تیترهای فهرست **تیترهای نمایشی** سایت‌اند و ممکن است کمی با تیتر خبر فرق کنند (مثلاً فهرست ترکیه «Soma ve Kangal işçileri eylemde...» نشان می‌دهد در حالی که تیتر خبر «Soma ve Kangal işçilerinden Konya’da hak arayışı...» است)؛ `cumhuriyet_get_article` تیتر واقعی را برمی‌گرداند.
- فیلد `wordCount` سایت تعداد **کاراکتر** articleBody است، نه کلمه — `word_count` برگردانده‌شده در اینجا از متن محاسبه می‌شود.
- صفحه‌های **ویدیو** (`/video/`)، **گالری** (`/galeri/`) و **بازی** (`/oyun/`) خبر متنی نیستند و از فهرست‌ها کنار گذاشته می‌شوند. ستون‌ها (`/yazarlar/<نویسنده>/...`) در فهرست‌ها هستند؛ خود صفحه‌های فهرست ستون‌نویسان در سمت سرور پیوند خبر نشان نمی‌دهند.
- متن خبرها از بلوک NewsArticle JSON-LD صفحه (`articleBody`، یک بلوک متن ساده) گرفته می‌شود؛ اگر صفحه JSON-LD نداشته باشد، پاراگراف‌های HTML به‌عنوان جایگزین استفاده می‌شوند.
- انتقال با جعل هویت TLS کروم انجام می‌شود؛ درخواست‌ها با فاصلهٔ حدود ۰٫۸ ثانیه فرستاده می‌شوند.

## توسعه

```bash
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/test_news.py -v    # آفلاین، با نمونه‌های ضبط‌شده
.venv/bin/python -m pytest tests/test_live.py -v    # زنده، در برابر www.cumhuriyet.com.tr
.venv/bin/python tests/smoke_live.py                # بررسی روزانهٔ CI
```

## مجوز

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — برای استفادهٔ شخصی و غیرتجاری رایگان است؛ استفادهٔ تجاری به مجوز جداگانه نیاز دارد.

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
