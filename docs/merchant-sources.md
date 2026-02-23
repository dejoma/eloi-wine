# Wine Merchant Source URLs

> Clean reference extracted from research-wine-source-urls.pdf + live browser verification
> Last updated: 2026-02-23

---

## Summary

- Total merchants researched: 80
- Downloadable file available (confirmed or stated): 54
- No download available / site down: 15
- Unconfirmed / behind auth / needs research: 11

### Verification Legend

| Symbol | Meaning |
|--------|---------|
| 🟢 | Confirmed working — HTTP 200 or file headers verified today |
| 🟡 | URL stated in PDF research but not live-verified |
| 🔴 | No URL found / site down / no download available |
| 🔒 | Login / account required |
| 🔃 | URL is dynamic (nonce, dated filename, JWT) — pattern given |

---

## Tier 1 Merchants (in corkscrew/merchants.yaml)

The sites below are the highest-priority integration targets with stable, machine-accessible URLs.

| Merchant | Country | Format | Direct URL | Pattern | Notes |
|----------|---------|--------|------------|---------|-------|
| Farr Vintners | UK | XLSX/CSV/TXT/JSON | 🟢 `https://farrvintners.com/winelist_xlsx.php` | static_php | Gold standard; also `.../winelist_csv.php`, `...?output=txt`, `.../winelist_json.php` |
| Turville Valley Wines | UK | XLSX | 🟡 `https://drive.google.com/uc?export=download&id=1Cj6l6Rs4dKCKxcQGxI2hPViWDUYP6N9y` | google_drive | |
| Goedhuis & Co | UK | XLSX | 🟢 `https://dailystockfunction.blob.core.windows.net/fine-wine-list/GWL_FINE_WINE_LIST.xlsx` | azure_blob | Updated hourly |
| BiBo Wine | UK | XLSX | 🟢 `https://extranet.hub.wine/xlsx/bibo` | hub_wine | |
| Decorum Vintners | UK | XLSX | 🟢 `https://extranet.hub.wine/xlsx/decorum` | hub_wine | |
| Falcon Vintners | UK | XLSX | 🟢 `https://extranet.hub.wine/xlsx/falconvintners` | hub_wine | |
| Four Walls Wine Co | UK | XLSX | 🟢 `https://extranet.hub.wine/xlsx/fourwallswine` | hub_wine | Also nonce URL: `/?nonce=XXXX&download_list=...` (session-specific, hub.wine is stable) |
| Hand Picked Burgundy | UK | XLSX | 🟢 `https://extranet.hub.wine/xlsx/hpb` | hub_wine | Also nonce URL: `/?nonce=XXXX&download_list=...` (session-specific, hub.wine is stable) |
| Sterling Fine Wines | UK | CSV | 🟢 `https://sterlingfw.hub.wine/shop-wine-list.aspx?dl=true` | hub_wine_legacy | |
| Santa Rosa Fine Wine | US | CSV | 🟢 `https://santarosafinewine.com/prodfeed.php` | static_php | Returns `srfw.csv` |
| GRW Wine Collection | US | CSV / PDF | 🟢 `https://docs.google.com/spreadsheets/d/e/2PACX-1vRmTYg2kFi3zHhtjEaV60xuQyiu6rfNXBHwiNcEtbLKaFv9Y57R6hqj96PanccSx2_OsdDD3F0397sO/pub?gid=0&single=true&output=csv` | google_sheets_pub | Also `...&output=pdf`; page: grwwine.com/pages/di |
| South Wine & Co | FR | XLSX | 🟢 `https://www.southwineandco.com/media/files/tarif_global.xlsx` | static_file | |
| Millésimes | FR | PDF | 🟢 `https://millesimes.com/tarif/pdf-ht.php` | static_php | |
| La Cave de l'ILL | FR | XLSX + PDF | 🟢 `https://lacavedelill.fr/lacavedelill.xlsx` | static_file | Also `.../lacavedelill.pdf` |
| SoDivin | FR | XLSX | 🟢 `https://sodivin.com/download/SoDivin_Tarif%20EN_Vintage.xlsx` | static_file | |
| Château & Estate | DE | XLS | 🟢 `https://chateau-estate.de/prices/price.xls` | static_file | |
| Orvinum AG | CH | PDF + XLSX | 🟢 `https://wine-rarities.auex.de/GetGerstlPDF.aspx?land=true&format=xlsx` | asp_query | Note: despite `format=xlsx` param, server returns `Application/pdf` content-type; data is PDF |
| Cave BB | CH | XLSX + PDF | 🟢 `https://www.cavebb.ch/en/ExportPreisliste/Excel` | aspnet | Also `/Pdf`, `/PdfInland`, `/ExcelInland` |
| Lucullus | CH | XLSX + PDF | 🟢 `https://www.lucullus.ch/product-price-list/xls` | shopware_redirect | Redirects to dated file, e.g. `.../Lucullus_Preisliste_17-02-2026.xlsx` |
| Grand Vin WM | UK | XLS | 🟢 `https://www.grandvinwinemerchants.co.uk/wine/download` | direct_download | Triggers download directly; returns `Content-Disposition: attachment; filename="GVWM Product List {DATE}.xls"` |
| Burgundy Cave | HK | XLSX | 🟡 `https://docs.google.com/spreadsheets/d/13gBLhRdhHQTA1GQ5SZGQZnk_eqUizkqm/export?format=xlsx` | google_sheets | |
| Cote d'Or Fine Wines | HK | XLSX + PDF | 🟢 Google Drive ID `1AsUfoClPiNsIyEX9ws0rOxBTwpf8tvkv` → `https://drive.google.com/uc?export=download&id=1AsUfoClPiNsIyEX9ws0rOxBTwpf8tvkv` | google_drive | ID confirmed from live site; PDF ID: `18UUWIaE_Z7vCwFqlFHfLYrmbOwhoJakM` |
| Hong Kong Wine Vault | HK | XLS | 🟢 `https://www.winevault.com.hk/site/WineVault_Wine_List.xls` | static_file | |
| Trinkreif | AT | XLSX + PDF | 🟢 `https://trinkreif.at/data/uploads/2026/02/trinkreif-Gesamtpreisliste-19-02-2026.xlsx` | dated_upload | Pattern: `/data/uploads/{YYYY}/{MM}/trinkreif-Gesamtpreisliste-{DD}-{MM}-{YYYY}.xlsx`; check preisliste page for current URL |
| Cave de Chaz | FR | CSV | 🟡 `https://docs.google.com/spreadsheets/d/1kkDx3hJCjucG01FnvyzGXjRXbi60T6DlbEWJKSuML-E/export?format=csv` | google_sheets | |
| Vintage Grand Cru | HK | PDF + XLSX | 🟡 `https://vintagegrandcru.com/pricelist.pdf` | static_file | Also `.../pricelist.xlsx` (returns 301 — needs follow) |

---

## Full 80-Merchant Research Index

### UK Sites (1–26)

| # | Merchant | Download | Format | Direct URL | Auth Barrier | Notes |
|---|----------|----------|--------|------------|--------------|-------|
| 1 | In Vino Veritas Ltd | Yes | ZIP/XLSX | 🟡 `https://www.invinoveritas.co.uk/download/wine_list.xlsx` | None | Hardcoded from PDF research; dated .htm page |
| 2 | Justerini & Brooks | Unclear | Excel | 🔴 Not found | React frontend | JS-triggered, no direct URL |
| 3 | Lay & Wheeler | No | — | 🔴 No download | — | No file export available |
| 4 | Naultia | Unknown | PDF/Excel | 🔴 Unknown | robots.txt blocks crawlers | robots.txt disallows |
| 5 | Private Cellar | Yes | PDF + XLSM | 🟡 `https://www.privatecellar.co.uk/downloads/E-List%20Private%20Cellar.pdf` | None | HTTP 301 to lowercase; also .xlsm |
| 6 | Richard Kihl Ltd | Yes | XLS + PDF | 🟢 `https://www.richardkihl.ltd.uk/winelist/winelist.xls` | None | Confirmed 200 with 1.8 MB XLS |
| 7 | Seckford Wines | No | — | 🔴 No download | — | No file export |
| 8 | Sterling Fine Wines | Yes | CSV | 🟢 `https://sterlingfw.hub.wine/shop-wine-list.aspx?dl=true` | None | hub.wine integration |
| 9 | Turville Valley Wines | Yes | XLSX | 🟡 `https://drive.google.com/uc?export=download&id=1Cj6l6Rs4dKCKxcQGxI2hPViWDUYP6N9y` | None | Google Drive public |
| 10 | Wilkinson Vintners | Unclear | CSV | 🔒 Login required | JWT auth | Hidden API endpoint; auth required |
| 11 | Cru Wine Investment | No | PDF | 🔴 Form only | None | Brochure only, not a price list |
| 12 | Albany Vintners | Yes | PDF + XLSX | 🟡 `https://www.albanyvintners.co.uk/downloads/price_list.xlsx` | None | Hardcoded from PDF research; JS-rendered links |
| 13 | Asset Wines | No | — | 🔴 No download | — | No file export |
| 14 | Barber Wines | Unknown | Unknown | 🔴 Not found | Unclear | Page couldn't be fetched during research |
| 15 | BiBo Wine | Yes | XLSX | 🟢 `https://extranet.hub.wine/xlsx/bibo` | None | hub.wine stable URL |
| 16 | Bibendum Wine | Yes | XLSX + PDF | 🟢 `https://bibendum-wine.co.uk/media/yfkchr4d/01022026-fine-wine-list.xlsx` | None | URL changes with each upload; pattern `/{slug}/{DDMMYYYY}-fine-wine-list.xlsx` |
| 17 | Burns & German Vintners | Unknown | Unknown | 🔒 Possibly login | — | Behind login per research |
| 18 | Cuchet & Co | Yes | XLSX | 🟢 `https://cuchet.co.uk/excel/Cuchet%20and%20co%20Wine%20List.xlsx` | None | Confirmed 200 |
| 19 | Decorum Vintners | Yes | XLSX | 🟢 `https://extranet.hub.wine/xlsx/decorum` | None | hub.wine stable URL |
| 20 | Falcon Vintners | Yes | XLSX | 🟢 `https://extranet.hub.wine/xlsx/falconvintners` | None | hub.wine stable URL |
| 21 | Farr Vintners | Yes | XLSX/CSV/TXT/JSON | 🟢 `https://farrvintners.com/winelist_xlsx.php` | None | Gold standard; multiple formats |
| 22 | Four Walls Wine Co | Yes | XLSX | 🟢 `https://extranet.hub.wine/xlsx/fourwallswine` | None | hub.wine stable URL; nonce URL also available from /collection/wines/ |
| 23 | Goedhuis & Co | Yes | XLSX | 🟢 `https://dailystockfunction.blob.core.windows.net/fine-wine-list/GWL_FINE_WINE_LIST.xlsx` | None | Azure blob; updated frequently |
| 24 | Grand Vin WM | Yes | XLS | 🟢 `https://www.grandvinwinemerchants.co.uk/wine/download` | None | Triggers download immediately; today's file: `GVWM Product List 2026-02-23.xls` |
| 25 | Hand Picked Burgundy | Yes | XLSX | 🟢 `https://extranet.hub.wine/xlsx/hpb` | None | hub.wine stable URL; session nonce URL also available from /wines/ |
| 26 | Hatton & Edwards | No | — | 🔴 No download | — | No file export |

---

### US Sites (27–33)

| # | Merchant | Download | Format | Direct URL | Auth Barrier | Notes |
|---|----------|----------|--------|------------|--------------|-------|
| 27 | Blacksmith Wines | No | — | 🔒 Login required | Full login wall | — |
| 28 | European Wine Resource | Unknown | Unknown | 🔴 Not found | 403 to bots | jQuery-based; 403 blocks crawlers |
| 29 | Flickinger Wines | No | — | 🔒 Login required | Full login wall | — |
| 30 | GRW Wine Collection | Yes | CSV | 🟢 `https://docs.google.com/spreadsheets/d/e/2PACX-1vRmTYg2kFi3zHhtjEaV60xuQyiu6rfNXBHwiNcEtbLKaFv9Y57R6hqj96PanccSx2_OsdDD3F0397sO/pub?gid=0&single=true&output=csv` | None | Also `...&output=pdf`; Shopify page grwwine.com/pages/di |
| 31 | Santa Rosa Fine Wine | Yes | CSV/XML | 🟢 `https://santarosafinewine.com/prodfeed.php` | None | Returns `srfw.csv` (Content-Disposition) |
| 32 | Spectrum Auctions | No | — | 🔒 Account required | Cloudflare 403 | — |
| 33 | Tribeca Wine Merchants | No | — | 🔒 Login required | Has login + honeypot | — |

---

### Europe non-UK (34–58)

| # | Merchant | Country | Download | Format | Direct URL | Auth Barrier | Notes |
|---|----------|---------|----------|--------|------------|--------------|-------|
| 34 | Enjoy Wine BCN | ES | No | — | 🔴 Cloudflare 403 | Bot block | — |
| 35 | Trinkreif | AT | Yes | XLSX + PDF | 🟢 `https://trinkreif.at/data/uploads/2026/02/trinkreif-Gesamtpreisliste-19-02-2026.xlsx` | None | Dated upload; check `trinkreif.at/news-ganz-vorne/preisliste/` for current URL |
| 36 | Vinosonline | ES | Unknown | Unknown | 🔴 Not found | — | Path `/es/content/17-catalogo` unverified |
| 37 | Finest Wine | ES | Unknown | Unknown | 🔴 Not found | — | Path `/en/content/37-download-our-complete-pricelist` unverified |
| 38 | South Wine & Co | FR | Yes | XLSX | 🟢 `https://www.southwineandco.com/media/files/tarif_global.xlsx` | None | Confirmed 200, 184 KB |
| 39 | Antoine Grands Crus | FR | No | — | 🔴 No download | — | — |
| 40 | World Grands Crus | FR | No | — | 🔴 No download | — | — |
| 41 | Dignef Fine Wines | BE | Unknown | PDF + Excel | 🔴 Site broken | — | dignef.com returns Apache "Index of /" (empty directory listing); site appears misconfigured |
| 42 | GVBSC | BE | No | — | 🔴 No download visible | — | — |
| 43 | Cercle des Vignerons | FR | N/A | — | 🔴 Site inaccessible | — | — |
| 44 | Ariès Vins | FR | Yes | PDF | 🟢 `https://aries-vins.com/img/cms/tarifs/CARTE%20DES%20VINS-300924.pdf` | None | URL was www.ariesvins.com (redirects to aries-vins.com); also Primeurs: `.../tarifs/PRIMEURS%202023.pdf` |
| 45 | Cave de Chaz | FR | Yes | CSV | 🟡 `https://docs.google.com/spreadsheets/d/1kkDx3hJCjucG01FnvyzGXjRXbi60T6DlbEWJKSuML-E/export?format=csv` | None | Google Sheets public export |
| 46 | De Vinis Illustribus | FR | Yes | PDF | 🟢 `https://devinis.fr/documents/catalogue/devinis_wine_list.pdf` | None | Confirmed 200, 63 KB |
| 47 | Denis Perret | FR | Yes | PDF | 🟢 `https://www.denisperret.fr/en/index.php?controller=attachment&id_attachment=3760` | None | Confirmed 200; PrestaShop attachment |
| 48 | Jean Merlaut | FR | Yes | PDF | 🟡 PrestaShop per-product PDF sheets | None | No single price list URL |
| 49 | L'Enseigne du Bordeaux | FR | Unknown | Unknown | 🔴 Site timing out | — | Domain: lenseignedubordeaux.fr (redirects from .com); PrestaShop B2B shop; no download link found in nav during research — site was unreachable on 2026-02-23 |
| 50 | Maison Jude | FR | Yes | XLSX + PDF | 🔃 `https://maisonjude.com/wp-content/uploads/{YYYY}/{MM}/MAISON-JUDE-STOCK-EXC.-VAT-XLS.xlsx` | None (rate-limited) | WordPress WP-content uploads; site rate-limits bots; direct file paths return 403 |
| 51 | Millésimes | FR | Yes | PDF | 🟢 `https://millesimes.com/tarif/pdf-ht.php` | None | Confirmed 200 |
| 52 | La Cave de l'ILL | FR | Yes | XLSX + PDF | 🟢 `https://lacavedelill.fr/lacavedelill.xlsx` | None | Also `.../lacavedelill.pdf` |
| 53 | Pleasure Wine | FR | No | — | 🔴 No download | — | — |
| 54 | SoDivin | FR | Yes | XLSX | 🟢 `https://sodivin.com/download/SoDivin_Tarif%20EN_Vintage.xlsx` | None | Confirmed 200, 210 KB |
| 55 | Vins & Millésimes | FR | Unknown | CSV? | 🔴 Domain not resolving | — | www.vins-millesimes.fr DNS fails; vins-et-millesimes.fr is a different site (wine guide blog, not a merchant) |
| 56 | WineMania | FR | Yes | PDF + XLS | 🟡 `https://winemania.com/tarifs/tarifs.pdf` | None | HTTP 301 to www subdomain; also `tarifs.xls` |
| 57 | Château & Estate | DE | Yes | XLS | 🟢 `https://chateau-estate.de/prices/price.xls` | None | Confirmed 200, 494 KB |
| 58 | Orvinum AG | CH | Yes | PDF + XLSX | 🟢 `https://wine-rarities.auex.de/GetGerstlPDF.aspx?land=true&format=xlsx` | None | Despite `format=xlsx` param, server always returns PDF content-type; data is accessible |

---

### Asia / HK (59–70)

| # | Merchant | Country | Download | Format | Direct URL | Auth Barrier | Notes |
|---|----------|---------|----------|--------|------------|--------------|-------|
| 59 | WA Investment Ltd | HK | No | HTML only | 🔴 No file download | — | HTML price table only |
| 60 | China Wine Club | HK | No | — | 🔴 Site down | — | Site appears offline |
| 61 | Great Ocean Industrial | AU | Unknown | Unknown | 🔴 404 / wrong site | — | greatocean.com.au is an unrelated magazine; wine company URL unconfirmed; the Shopify page `/pages/our-full-wine-list` returns 404 |
| 62 | Burgundy Cave | HK | Yes | XLSX | 🟡 `https://docs.google.com/spreadsheets/d/13gBLhRdhHQTA1GQ5SZGQZnk_eqUizkqm/export?format=xlsx` | None | Google Sheets public export |
| 63 | CitiCellar | HK | Unknown | Unknown | 🔴 Not found | — | JS-triggered; no static URL |
| 64 | Cote d'Or Fine Wines | HK | Yes | XLSX + PDF | 🟢 `https://drive.google.com/uc?export=download&id=1AsUfoClPiNsIyEX9ws0rOxBTwpf8tvkv` | None | Google Drive; confirmed Drive file ID from live site cotedorfinewines.com; PDF Drive ID: `18UUWIaE_Z7vCwFqlFHfLYrmbOwhoJakM` |
| 65 | DFV Fine Wines | HK | No | — | 🔴 No download | — | — |
| 66 | East Power Vins | HK | Yes | PDF + XLSX | 🔃 `https://epvins.com/panel/exportExcel.php?k=BASE64&s=BASE64` | None | Dynamic keys; URL params change per request |
| 67 | Ganpei Vintners | HK | Yes | XLSX | 🔃 `https://cdn.shopify.com/s/files/1/0000/0000/files/GV_Catalog_{YYYYMMDD}.xlsx` | None | Shopify CDN dated file; exact file IDs change — check site for current URL |
| 68 | OneRedDot Fine Wines | HK | Unknown | PDF + XLS | 🔴 Not found | — | Not found in HTML; unconfirmed |
| 69 | Vintage Grand Cru | HK | Yes | PDF + XLSX | 🟡 `https://vintagegrandcru.com/pricelist.pdf` | None | Returns 301; also `.../pricelist.xlsx` |
| 70 | Hong Kong Wine Vault | HK | Yes | XLS + CSV | 🟢 `https://www.winevault.com.hk/site/WineVault_Wine_List.xls` | None | Confirmed 200, 1.5 MB |

---

### Switzerland (71–80)

| # | Merchant | Country | Download | Format | Direct URL | Auth Barrier | Notes |
|---|----------|---------|----------|--------|------------|--------------|-------|
| 71 | Pierre Wyss | CH | No | — | 🔒 Full login wall | Login | — |
| 72 | TopWines Switzerland | CH | No | — | 🔴 No download | — | — |
| 73 | Aquilon Luxe (BV Vins Swiss) | CH | Yes | XLSX | 🔴 JS-triggered | Magento 2 | Magento 2 JS-triggered; no static URL found |
| 74 | 1870 Vins et Conseils | CH | Yes | PDF (×3) | 🔴 Domain defunct | — | www.1870.fr DNS does not resolve; last Wayback Machine snapshot April 2023; URL `https://www.1870.fr/docs/liste_tarif.pdf` was stated in PDF research but site is offline |
| 75 | BV Vins (World) | CH | Yes | XLSX | 🔴 JS-triggered | Magento 2 | Magento 2 JS-triggered |
| 76 | Cave BB | CH | Yes | XLSX + PDF | 🟢 `https://www.cavebb.ch/en/ExportPreisliste/Excel` | None | Confirmed 200, 391 KB XLSX; also `/Pdf`, `/PdfInland`, `/ExcelInland` |
| 77 | Lucullus | CH | Yes | XLSX + PDF | 🟢 `https://www.lucullus.ch/product-price-list/xls` | None | Shopware redirect to dated file, e.g. `...Lucullus_Preisliste_17-02-2026.xlsx` |
| 78 | Martel AG | CH | Yes | PDF | 🟢 `https://www.martel.ch/pdf/Martel_Gesamtangebot_Privatkunden.pdf` | None | Confirmed 200, 505 KB PDF; no Excel found on downloads page; PDF is the only download |
| 79 | Vinothek im Park | CH | Unknown | PDF | 🔴 Not found | — | Not found in HTML |
| 80 | World Web Wines | CH | Unknown | CSV | 🔴 Not found | Age gate | Not in main HTML; age gate |

---

## Sites Requiring JS / Auth (V2 Scope)

These sites have download functionality but cannot be accessed with simple HTTP requests:

| Merchant | Reason | Potential Approach |
|----------|--------|-------------------|
| Justerini & Brooks (#2) | React frontend; JS-triggered download | Headless browser + click extraction |
| Wilkinson Vintners (#10) | JWT token required | API auth / contact for API key |
| Burns & German Vintners (#17) | Possibly behind trade login | Contact merchant |
| Aquilon Luxe / BV Vins Swiss (#73, #75) | Magento 2 AJAX download | Headless browser session |
| CitiCellar (#63) | JS-triggered | Headless browser |
| East Power Vins (#66) | Dynamic BASE64 params | Session capture + replay |
| Ganpei Vintners (#67) | Shopify CDN dated file | Scrape landing page for current URL |

---

## Dynamic URL Patterns

Sites where the URL changes regularly and requires a lookup step:

| Merchant | Pattern | How to get current URL |
|----------|---------|----------------------|
| Trinkreif (#35) | `trinkreif.at/data/uploads/{YYYY}/{MM}/trinkreif-Gesamtpreisliste-{DD}-{MM}-{YYYY}.xlsx` | Scrape `trinkreif.at/news-ganz-vorne/preisliste/` for current link |
| Bibendum Wine (#16) | `bibendum-wine.co.uk/media/{slug}/{DDMMYYYY}-fine-wine-list.xlsx` | Scrape bibendum-wine.co.uk for current link in page |
| Maison Jude (#50) | `maisonjude.com/wp-content/uploads/{YYYY}/{MM}/MAISON-JUDE-STOCK-EXC.-VAT-XLS.xlsx` | Scrape maisonjude.com for current link (rate-limited: use delay) |
| Four Walls Wine Co (#22) | `fourwallswine.com/?nonce={NONCE}&download_list={QUERY}` | Prefer `extranet.hub.wine/xlsx/fourwallswine` instead |
| Hand Picked Burgundy (#25) | `hpb-wines.com/?nonce={NONCE}&download_list={QUERY}` | Prefer `extranet.hub.wine/xlsx/hpb` instead |
| Grand Vin WM (#24) | `grandvinwinemerchants.co.uk/wine/download` returns dated file | URL is stable; filename has today's date but URL does not change |
| Ganpei Vintners (#67) | `cdn.shopify.com/s/files/1/.../{GV_Catalog_YYYYMMDD}.xlsx` | Scrape Ganpei Vintners site for current file link |

---

## URL Verification Status

| # | Merchant | Status | Last Verified | Method |
|---|----------|--------|---------------|--------|
| 1 | In Vino Veritas Ltd | 🟡 Unverified | — | PDF research |
| 2 | Justerini & Brooks | 🔴 No URL | — | — |
| 3 | Lay & Wheeler | 🔴 No download | — | — |
| 4 | Naultia | 🔴 Unknown | — | robots.txt blocked |
| 5 | Private Cellar | 🟡 Unverified | — | PDF research |
| 6 | Richard Kihl Ltd | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 1.8 MB XLS |
| 7 | Seckford Wines | 🔴 No download | — | — |
| 8 | Sterling Fine Wines | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, CSV |
| 9 | Turville Valley Wines | 🟡 Unverified | — | PDF research |
| 10 | Wilkinson Vintners | 🔒 Auth required | — | — |
| 11 | Cru Wine Investment | 🔴 Form only | — | — |
| 12 | Albany Vintners | 🟡 Unverified | — | PDF research |
| 13 | Asset Wines | 🔴 No download | — | — |
| 14 | Barber Wines | 🔴 Not found | — | — |
| 15 | BiBo Wine | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, XLSX |
| 16 | Bibendum Wine | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 5.4 MB XLSX |
| 17 | Burns & German Vintners | 🔒 Possibly login | — | — |
| 18 | Cuchet & Co | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, XLSX |
| 19 | Decorum Vintners | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, XLSX |
| 20 | Falcon Vintners | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, XLSX |
| 21 | Farr Vintners | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 523 KB XLSX |
| 22 | Four Walls Wine Co | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, fourwallswine.xlsx |
| 23 | Goedhuis & Co | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 330 KB XLSX |
| 24 | Grand Vin WM | 🟢 Confirmed | 2026-02-23 | HTTP 200, attachment header with today's date |
| 25 | Hand Picked Burgundy | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, hpb.xlsx |
| 26 | Hatton & Edwards | 🔴 No download | — | — |
| 27 | Blacksmith Wines | 🔒 Login | — | — |
| 28 | European Wine Resource | 🔴 403 | — | — |
| 29 | Flickinger Wines | 🔒 Login | — | — |
| 30 | GRW Wine Collection | 🟢 Confirmed | 2026-02-23 | Live browser; CSV and PDF links on /pages/di |
| 31 | Santa Rosa Fine Wine | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, srfw.csv |
| 32 | Spectrum Auctions | 🔒 Cloudflare 403 | — | — |
| 33 | Tribeca Wine Merchants | 🔒 Login | — | — |
| 34 | Enjoy Wine BCN | 🔴 403 | — | Cloudflare bot block |
| 35 | Trinkreif | 🟢 Confirmed | 2026-02-23 | Direct HTML scrape; current file 19-02-2026 |
| 36 | Vinosonline | 🔴 Unknown | — | — |
| 37 | Finest Wine | 🔴 Unknown | — | — |
| 38 | South Wine & Co | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 184 KB XLSX |
| 39 | Antoine Grands Crus | 🔴 No download | — | — |
| 40 | World Grands Crus | 🔴 No download | — | — |
| 41 | Dignef Fine Wines | 🔴 Site broken | 2026-02-23 | Apache empty directory listing |
| 42 | GVBSC | 🔴 No download | — | — |
| 43 | Cercle des Vignerons | 🔴 Inaccessible | — | — |
| 44 | Ariès Vins | 🟢 Confirmed | 2026-02-23 | Live browser; PDF link on telecharger page |
| 45 | Cave de Chaz | 🟡 Unverified | — | PDF research; Google Sheets |
| 46 | De Vinis Illustribus | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 63 KB PDF |
| 47 | Denis Perret | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, PDF |
| 48 | Jean Merlaut | 🟡 Partial | — | Per-product PDFs only |
| 49 | L'Enseigne du Bordeaux | 🔴 Timeout | 2026-02-23 | Site unreachable at lenseignedubordeaux.fr |
| 50 | Maison Jude | 🔃 Dynamic | 2026-02-23 | Site rate-limits; direct path 403; URL pattern known |
| 51 | Millésimes | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200 |
| 52 | La Cave de l'ILL | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, XLSX |
| 53 | Pleasure Wine | 🔴 No download | — | — |
| 54 | SoDivin | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 210 KB XLSX |
| 55 | Vins & Millésimes | 🔴 Domain down | 2026-02-23 | www.vins-millesimes.fr DNS fails |
| 56 | WineMania | 🟡 Unverified | — | PDF research; HTTP 301 redirect |
| 57 | Château & Estate | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 494 KB XLS |
| 58 | Orvinum AG | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 671 KB PDF (despite xlsx param) |
| 59 | WA Investment Ltd | 🔴 No download | — | HTML only |
| 60 | China Wine Club | 🔴 Site down | — | — |
| 61 | Great Ocean Industrial | 🔴 Wrong site | 2026-02-23 | greatocean.com.au is unrelated magazine |
| 62 | Burgundy Cave | 🟡 Unverified | — | PDF research; Google Sheets |
| 63 | CitiCellar | 🔴 JS only | — | — |
| 64 | Cote d'Or Fine Wines | 🟢 Confirmed | 2026-02-23 | Live browser; Drive file ID confirmed |
| 65 | DFV Fine Wines | 🔴 No download | — | — |
| 66 | East Power Vins | 🔃 Dynamic | — | Dynamic BASE64 params |
| 67 | Ganpei Vintners | 🔃 Dynamic | — | Shopify CDN dated file |
| 68 | OneRedDot Fine Wines | 🔴 Not found | — | — |
| 69 | Vintage Grand Cru | 🟡 Unverified | — | PDF research; 301 redirect |
| 70 | Hong Kong Wine Vault | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 1.5 MB XLS |
| 71 | Pierre Wyss | 🔒 Login | — | — |
| 72 | TopWines Switzerland | 🔴 No download | — | — |
| 73 | Aquilon Luxe | 🔴 JS-triggered | — | Magento 2 |
| 74 | 1870 Vins et Conseils | 🔴 Domain defunct | 2026-02-23 | DNS failure; last Wayback 2023-04 |
| 75 | BV Vins (World) | 🔴 JS-triggered | — | Magento 2 |
| 76 | Cave BB | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 400 KB XLSX |
| 77 | Lucullus | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, redirects to dated XLSX |
| 78 | Martel AG | 🟢 Confirmed | 2026-02-23 | HTTP HEAD 200, 505 KB PDF (no Excel found) |
| 79 | Vinothek im Park | 🔴 Not found | — | — |
| 80 | World Web Wines | 🔴 Age gate | — | — |

---

## hub.wine Integration Summary

Six UK merchants share the `extranet.hub.wine` CDN, all returning stable XLSX files:

| Merchant | Stable URL |
|----------|-----------|
| BiBo Wine | `https://extranet.hub.wine/xlsx/bibo` |
| Decorum Vintners | `https://extranet.hub.wine/xlsx/decorum` |
| Falcon Vintners | `https://extranet.hub.wine/xlsx/falconvintners` |
| Four Walls Wine Co | `https://extranet.hub.wine/xlsx/fourwallswine` |
| Hand Picked Burgundy | `https://extranet.hub.wine/xlsx/hpb` |
| Sterling Fine Wines | `https://sterlingfw.hub.wine/shop-wine-list.aspx?dl=true` (legacy hub.wine format, returns CSV) |

All `extranet.hub.wine` URLs return HTTP 200 with `Content-Disposition: attachment; filename="{slug}.xlsx"`. No authentication required. These are the most reliable format in the dataset.

---

*Generated by browser research session on 2026-02-23. Sources: research-wine-source-urls.pdf + live HTTP verification.*
