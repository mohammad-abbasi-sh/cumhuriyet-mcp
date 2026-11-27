# cumhuriyet-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/cumhuriyet-mcp

**Cumhuriyet** (www.cumhuriyet.com.tr) için resmi olmayan, **salt okunur** MCP sunucusu — Türkiye'nin en büyük ulusal gazetelerinden biri (1924'ten beri): **son haberler** (Google Haberler site haritasından), **ana sayfa manşetleri**, **bölüm manşetleri**, **haberlerin tam metni**, **anahtar kelime araması** ve **bölüm listesi**.

> "Turkey MCP factory" projesinin bir parçasıdır. Cumhuriyet ile bağlantısı yoktur. Veriler Cumhuriyet'in herkese açık sayfalarından ve Google Haberler site haritasından alınır — giriş gerekmez, API anahtarı gerekmez, salt okunur.

## Yapay zekâ ajanları için

- **Son haberler**: `cumhuriyet_latest_news`, `/sitemaps/news.xml` dosyasındaki en yeni haberleri döndürür (en yeni 608 öğe, başlık, yayın saati, bölüm, URL), en yeniden en eskiye.
- **Manşetler**: `cumhuriyet_headlines`, ana sayfadaki öne çıkan haberleri döndürür (başlık, URL, listede varsa özet, bölüm) — günün köşe yazıları da dahildir.
- **Bölüm haberleri**: `cumhuriyet_section_news` bir bölüm alır — `"turkiye"` (varsayılan), `"siyaset"`, `"ekonomi"`, `"dunya"`, `"spor"`, `"kultur-sanat"`, `"egitim"`, `"saglik"`, `"yasam"`, `"magazin"`, `"otomobil"` — ve bölüm başına ~38 manşet döndürür (başlık, URL, özet).
- **Haber metni**: `cumhuriyet_get_article` tam bir cumhuriyet.com.tr URL'si alır ve başlık, yazar, yayın/güncelleme tarihleri, açıklama, görsel, kelime sayısı ve tam metni döndürür (sayfadaki NewsArticle JSON-LD bloğundan).
- **Arama**: `cumhuriyet_search_news`, Google Haberler site haritasındaki en yeni 608 başlığı anahtar kelimeyle tarar — `"emekli"`, `"deprem"`, `"dolar"` — Türkçe duyarlıdır (noktalı/noktasız I ayırt edilir, `"İSTANBUL"` `"İstanbul"` ile eşleşir).
- **Bölümler**: `cumhuriyet_list_sections`, `cumhuriyet_section_news` ile kullanılabilen bölümleri Türkçe adlarıyla döndürür.
- Her yanıt `fetched_at` (UTC) ve `source: cumhuriyet.com.tr` taşır.

## Kurulum

```bash
uvx cumhuriyet-mcp
```

Ya da MCP istemcinizin ayarlarına ekleyin (ör. Claude Desktop):

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

## Araçlar

| Araç | Ne yapar |
| --- | --- |
| `cumhuriyet_latest_news` | Google Haberler site haritasından son haberler, en yeniden en eskiye |
| `cumhuriyet_headlines` | Ana sayfadaki öne çıkan haberler |
| `cumhuriyet_section_news` | Bir bölümdeki manşetler |
| `cumhuriyet_get_article` | Bir haberin tam metni (tam URL) |
| `cumhuriyet_search_news` | En yeni 608 site haritası başlığında anahtar kelime araması |
| `cumhuriyet_list_sections` | `cumhuriyet_section_news` ile kullanılabilen haber bölümleri |
| `cumhuriyet_health` | cumhuriyet.com.tr şu anda erişilebilir mi? |

## Örnek

Son haberler, 27 Kasım 2026:

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

Bir haber, 27 Kasım 2026:

```json
{ "title": "Soma ve Kangal işçilerinden Konya’da hak arayışı: '1,4 milyar lira alacağımız var'",
  "author": "ANKA",
  "date_published": "2026-11-27T12:19:00+03:00",
  "section": "Türkiye", "word_count": 299,
  "body": "Manisa’nın Soma ve Sivas’ın Kangal ilçelerindeki termik santrallerde çalışan işçiler, ücret ve diğer alacaklarının ödenmesi, iş güvencelerinin sağlanması için Konya’da eylem yaptı. …" }
```

## Dikkat edilecekler

- Arama, Google Haberler site haritasındaki **en yeni 608 başlığın taranmasıdır**, tam arşiv araması değildir: sitenin kendi araması (`/arama/`) robots.txt'de yasaklıdır ve sonuç döndürmez, bu yüzden çağrılacak bir arama API'si yoktur.
- Bölüm sayfalarında **sayfalama yoktur** ("Daha Fazla Göster" istemci tarafındadır) — her biri ~38 öğe taşır, bu yüzden `cumhuriyet_section_news` yalnızca güncel sayfayı görür.
- **`/son-dakika/` liste sayfası yoktur** (404) — son haberler site haritasından alınır.
- Liste başlıkları sitenin **görünüm başlıklarıdır** ve haber başlığından biraz farklı olabilir (ör. Türkiye listesi "Soma ve Kangal işçileri eylemde..." gösterirken haber başlığı "Soma ve Kangal işçilerinden Konya’da hak arayışı..."dır); `cumhuriyet_get_article` gerçek başlığı döndürür.
- Sitenin `wordCount` alanı kelime değil, articleBody **karakter** sayısıdır — burada döndürülen `word_count` metinden hesaplanır.
- **Video** (`/video/`), **galeri** (`/galeri/`) ve **oyun** (`/oyun/`) sayfaları metin haber değildir ve listelerden çıkarılır. Köşe yazıları (`/yazarlar/<yazar>/...`) listelere dahildir; köşe yazarları dizin sayfalarının kendileri sunucu tarafında haber bağlantısı göstermez.
- Haber gövdeleri sayfadaki NewsArticle JSON-LD bloğundan (`articleBody`, tek bir düz metin bloğu) alınır; JSON-LD yoksa yedek olarak HTML paragrafları kullanılır.
- Aktarım Chrome TLS kimlik bürünmesi kullanır; istekler ~0,8 sn arayla gönderilir.

## Geliştirme

```bash
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/test_news.py -v    # çevrimdışı, kayıtlı örnekler
.venv/bin/python -m pytest tests/test_live.py -v    # canlı, www.cumhuriyet.com.tr'ye karşı
.venv/bin/python tests/smoke_live.py                # günlük CI denetimi
```

## Lisans

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — kişisel ve ticari olmayan kullanım için ücretsizdir; ticari kullanım için ayrı bir lisans gerekir.

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
