# PRD: Wine Inventory Scraper Pipeline — V1

## Product Overview

### Project Name
**Corkscrew** — Wine Merchant Inventory Scraper Pipeline

### Version
V1 — HTTP-Only Static Downloads

### Summary
Corkscrew V1 is a Python CLI tool that downloads wine inventory/price list files from ~40 wine merchants that expose direct, unauthenticated download URLs. It normalizes the downloaded data into a standard CSV schema and stores both raw files and normalized output for downstream consumption. V1 targets the highest-coverage, lowest-friction merchants — covering roughly half of the known 80-merchant universe with simple HTTP GET requests and zero browser automation.

### Goals
- Download inventory files from all merchants with publicly accessible, direct download URLs
- Normalize heterogeneous file formats (XLSX, XLS, CSV, JSON, PDF metadata) into a single standard schema
- Detect staleness (unchanged files) and track download history
- Provide a CLI interface for manual runs and cron-compatible exit codes for scheduling
- Establish the merchant configuration schema that V2 and V3 will extend

### Non-Goals (V1)
- Browser automation or JavaScript rendering
- Session-aware downloads (nonce extraction, cookie-based auth, JWT tokens)
- HTML page scraping / inventory extraction from rendered pages
- Age gate or login wall handling
- Agentic discovery of new download URLs
- Web UI or dashboard
- Real-time or streaming updates

---

## Target Merchants (V1 Scope)

V1 covers merchants classified as **Tier 1** — those with direct, unauthenticated, static or predictable download URLs accessible via HTTP GET. Based on the merchant audit report, these fall into five download mechanism archetypes.

### Archetype 1: hub.wine Extranet Endpoint
Single URL pattern covers multiple merchants: `extranet.hub.wine/xlsx/{slug}` (Excel) and `extranet.hub.wine/html/{slug}` (HTML fallback).

| # | Merchant | Slug | Format |
|---|---------|------|--------|
| 8 | Sterling Fine Wines | `sterlingfw` (variant: `sterlingfw.hub.wine/shop-wine-list.aspx?dl=true`) | CSV |
| 15 | BiBo Wine | `bibo` | XLSX |
| 19 | Decorum Vintners | `decorum` | XLSX |
| 20 | Falcon Vintners | `falconvintners` | XLSX |
| 24 | Grand Vin WM | `grandvinwinemerchants` (variant: `/wine/download`) | Excel |

### Archetype 2: Static File Paths on Merchant Domain
Direct URLs to files hosted on the merchant's own server. Predictable, stable paths.

| # | Merchant | URL(s) | Format(s) |
|---|---------|--------|-----------|
| 1 | In Vino Veritas Ltd | On dated `.htm` page (requires URL extraction) | ZIP (Excel) |
| 5 | Private Cellar | `privatecellar.co.uk/downloads/E-List Private Cellar.pdf` / `.xlsm` | PDF + XLSM |
| 6 | Richard Kihl Ltd | `richardkihl.ltd.uk/winelist/winelist.xls` | XLS |
| 16 | Bibendum Wine | `bibendum-wine.co.uk/media/yfkchr4d/01022026-fine-wine-list.xlsx` | XLSX |
| 18 | Cuchet & Co | `cuchet.co.uk/excel/Cuchet%20and%20co%20Wine%20List.xlsx` | XLSX |
| 21 | Farr Vintners | `farrvintners.com/winelist_csv.php?output=csv` (also XLSX, JSON, TXT) | CSV, XLSX, JSON, TXT |
| 35 | Trinkreif | `trinkreif.at/data/uploads/2026/02/trinkreif-Gesamtpreisliste-DD-MM-YYYY.xlsx` | XLSX |
| 38 | South Wine & Co | `southwineandco.com/media/files/tarif_global.xlsx` | XLSX |
| 46 | De Vinis Illustribus | `devinis.fr/documents/catalogue/devinis_wine_list.pdf` | PDF |
| 47 | Denis Perret | `denisperret.fr/en/index.php?controller=attachment&id_attachment=3760` | PDF |
| 50 | Maison Jude | `maisonjude.com/wp-content/uploads/2026/02/MAISON-JUDE-STOCK-EXC.-VAT-XLS.xlsx` (4 variants) | XLSX + PDF (×2 tax) |
| 51 | Millésimes | `millesimes.com/tarif/pdf-ht.php` | PDF |
| 52 | La Cave de l'ILL | `lacavedelill.fr/lacavedelill.xlsx` / `.pdf` | XLSX + PDF |
| 54 | SoDivin | `sodivin.com/download/SoDivin_Tarif EN_Vintage.xlsx` / `_Chateau.xlsx` | XLSX |
| 56 | WineMania | `winemania.com/tarifs/tarifs.pdf` / `tarifs.xls` | XLS + PDF |
| 57 | Château & Estate | `chateau-estate.de/prices/price.xls` | XLS |
| 69 | Vintage Grand Cru | `vintagegrandcru.com/pricelist.xlsx` / `.pdf` | XLSX + PDF |

### Archetype 3: Google Drive / Google Sheets
Hosted on Google infrastructure. Export via known URL transforms.

| # | Merchant | Google Resource | Format |
|---|---------|----------------|--------|
| 9 | Turville Valley Wines | `drive.google.com/uc?export=download&id=1Cj6l6Rs4dKCKxcQGxI2hPViWDUYP6N9y` | Excel/CSV |
| 45 | Cave de Chaz | `docs.google.com/spreadsheets/d/1kkDx3hJCjucG01FnvyzGXjRXbi60T6DlbEWJKSuML-E` | Google Sheets → CSV |
| 62 | Burgundy Cave | `docs.google.com/spreadsheets/d/13gBLhRdhHQTA1GQ5SZGQZnk_eqUizkqm` | Google Sheets → XLSX |

### Archetype 4: Cloud-Hosted Static Exports

| # | Merchant | URL Pattern | Format |
|---|---------|-------------|--------|
| 23 | Goedhuis & Co | `dailystockfunction.blob.core.windows.net/fine-wine-list/GWL_FINE_WINE_LIST.xlsx` | XLSX |
| 67 | Ganpei Vintners | `cdn.shopify.com/.../GV_Catalog_YYYYMMDD.xlsx` (date-stamped) | XLSX |

### Archetype 5: REST-Style Download Endpoints

| # | Merchant | URL Pattern | Format |
|---|---------|-------------|--------|
| 58 | Orvinum AG | `wine-rarities.auex.de/GetGerstlPDF.aspx?land=true` (4 variants) | PDF + XLSX |
| 70 | Hong Kong Wine Vault | `winevault.com.hk/site/WineVault_Wine_List.xls` | XLS |
| 76 | Cave BB | `cavebb.ch/en/ExportPreisliste/Excel` (4 endpoints) | XLSX + PDF |
| 77 | Lucullus | `lucullus.ch/product-price-list/xls` / `/pdf` | Excel + PDF |
| 31 | Santa Rosa Fine Wine | `santarosafinewine.com/prodfeed.php` | CSV/XML |

### Also Included (Simple HTTP, Minor Variations)

| # | Merchant | Notes |
|---|---------|-------|
| 12 | Albany Vintners | JS-rendered links but direct file URLs extractable |
| 30 | GRW Wine Collection | Shopify pages link `/pages/di` |
| 61 | Great Ocean Industrial | Shopify `/pages/our-full-wine-list` |
| 74 | 1870 Vins et Conseils | PDF links in header + footer nav |

**Total V1 merchant count: ~38–42** (depending on URL confirmation for edge cases).

---

## Merchant Configuration Schema

Each merchant is defined in a YAML configuration file. This schema is the contract between V1, V2, and V3.

```yaml
# merchants.yaml
merchants:
  - id: "farr-vintners"
    name: "Farr Vintners"
    country: "UK"
    tier: 1                          # 1=HTTP, 2=session-aware, 3=browser-agent
    enabled: true
    discovery_url: "https://www.farrvintners.com/downloads/"
    downloads:
      - url: "https://www.farrvintners.com/winelist_csv.php?output=csv"
        format: "csv"
        preferred: true              # Use this one for normalization
        label: "CSV full list"
      - url: "https://www.farrvintners.com/winelist_xlsx.php"
        format: "xlsx"
        preferred: false
        label: "Excel full list"
      - url: "https://www.farrvintners.com/winelist_json.php"
        format: "json"
        preferred: false
        label: "JSON full list"
    url_pattern: "static"            # static | dated | google_sheets | google_drive | hub_wine | rest_endpoint | dynamic_php
    date_pattern: null               # For dated URLs: "trinkreif-Gesamtpreisliste-{DD}-{MM}-{YYYY}.xlsx"
    auth: null                       # null | nonce | jwt | login | age_gate
    notes: "Gold standard - 4 formats available"

  - id: "bibo-wine"
    name: "BiBo Wine"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.bibo-wine.co.uk/"
    downloads:
      - url: "https://extranet.hub.wine/xlsx/bibo"
        format: "xlsx"
        preferred: true
        label: "hub.wine Excel export"
    url_pattern: "hub_wine"
    auth: null
    notes: "hub.wine extranet pattern"

  - id: "trinkreif"
    name: "Trinkreif"
    country: "AT"
    tier: 1
    enabled: true
    discovery_url: "https://trinkreif.at/"
    downloads:
      - url: "https://trinkreif.at/data/uploads/{YYYY}/{MM}/trinkreif-Gesamtpreisliste-{DD}-{MM}-{YYYY}.xlsx"
        format: "xlsx"
        preferred: true
        label: "Date-stamped Excel list"
    url_pattern: "dated"
    date_pattern: "{YYYY}/{MM}/trinkreif-Gesamtpreisliste-{DD}-{MM}-{YYYY}.xlsx"
    auth: null
    notes: "URL contains current date; try today first, then walk back up to 7 days"

  - id: "cave-de-chaz"
    name: "Cave de Chaz"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://cavechaz.com/"
    downloads:
      - url: "https://docs.google.com/spreadsheets/d/1kkDx3hJCjucG01FnvyzGXjRXbi60T6DlbEWJKSuML-E/export?format=csv"
        format: "csv"
        preferred: true
        label: "Google Sheets CSV export"
    url_pattern: "google_sheets"
    google_sheet_id: "1kkDx3hJCjucG01FnvyzGXjRXbi60T6DlbEWJKSuML-E"
    auth: null
    notes: "Google Sheets; append /export?format=csv to get CSV"
```

### Configuration Fields Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique slug identifier (kebab-case) |
| `name` | string | Yes | Human-readable merchant name |
| `country` | string | Yes | ISO 2-letter country code |
| `tier` | int | Yes | 1=HTTP-only, 2=session/browser-click, 3=agentic |
| `enabled` | bool | Yes | Whether to include in runs |
| `discovery_url` | string | Yes | Page where download links are found |
| `downloads` | list | Yes | One or more download endpoints |
| `downloads[].url` | string | Yes | Direct download URL (may contain `{YYYY}`, `{MM}`, `{DD}` placeholders) |
| `downloads[].format` | string | Yes | Expected file format: `xlsx`, `xls`, `xlsm`, `csv`, `json`, `txt`, `pdf`, `zip` |
| `downloads[].preferred` | bool | Yes | Which download to use for normalization |
| `downloads[].label` | string | No | Human description |
| `url_pattern` | string | Yes | URL archetype for download logic routing |
| `date_pattern` | string | No | Template for date-stamped URLs |
| `auth` | string | No | Authentication type required (null for V1) |
| `google_sheet_id` | string | No | For Google Sheets merchants |
| `google_drive_id` | string | No | For Google Drive merchants |
| `notes` | string | No | Free-text implementation notes |

---

## Normalized Output Schema

All merchant data is normalized into a single flat CSV schema. This is the contract for downstream consumers.

```
merchant_id, merchant_name, wine_name, vintage, region, sub_region, appellation, color, format, price, currency, stock_quantity, case_size, score, scorer, condition_notes, source_url, download_date
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `merchant_id` | string | Yes | Matches config `id` |
| `merchant_name` | string | Yes | Human-readable merchant name |
| `wine_name` | string | Yes | Full wine name including château/domaine |
| `vintage` | string | No | Year as string (allows "NV" for non-vintage) |
| `region` | string | No | Top-level region (Bordeaux, Burgundy, Rhône, etc.) |
| `sub_region` | string | No | Sub-region (Pauillac, St. Julien, Côte de Nuits, etc.) |
| `appellation` | string | No | AOC/AOP/DOC if available |
| `color` | string | No | red, white, rosé, sparkling, dessert, fortified |
| `format` | string | No | bottle, magnum, half-bottle, jeroboam, imperial, etc. |
| `price` | decimal | No | Numeric price (excluding VAT unless noted) |
| `currency` | string | No | ISO 4217 (GBP, EUR, USD, CHF, HKD) |
| `stock_quantity` | integer | No | Number of units available |
| `case_size` | integer | No | Units per case if pricing is per-case |
| `score` | string | No | Critic score if provided (e.g., "98", "95-97") |
| `scorer` | string | No | Scoring body (Parker, Jancis Robinson, Wine Spectator) |
| `condition_notes` | string | No | OWC, damaged label, fill level, etc. |
| `source_url` | string | Yes | URL the file was downloaded from |
| `download_date` | string | Yes | ISO 8601 date of download |

### Normalization Rules
- Prices are stored as-is from the merchant (no currency conversion)
- Currency is inferred from merchant country if not explicit in the data
- Vintage "NV" or empty string for non-vintage wines
- Format defaults to "bottle" (75cl) if not specified
- Fields not available from a merchant are left empty (not null, not "N/A")
- Each merchant gets its own normalizer function since column mappings vary

---

## System Architecture

### Directory Structure

```
corkscrew/
├── corkscrew/
│   ├── __init__.py
│   ├── cli.py                    # CLI entry point (click or argparse)
│   ├── config.py                 # YAML config loader + validation
│   ├── downloader.py             # HTTP download engine
│   ├── normalizer.py             # Base normalizer + registry
│   ├── normalizers/              # Per-merchant normalizer overrides
│   │   ├── __init__.py
│   │   ├── farr_vintners.py
│   │   ├── hub_wine.py           # Shared normalizer for all hub.wine merchants
│   │   ├── google_sheets.py      # Shared normalizer for Google Sheets merchants
│   │   └── ...
│   ├── storage.py                # File storage + hashing + history
│   └── models.py                 # Pydantic models for config + normalized wine
├── merchants.yaml                # Merchant configurations
├── data/
│   ├── raw/                      # Raw downloaded files: {merchant_id}/{date}/{filename}
│   ├── normalized/               # Normalized CSVs: {merchant_id}/{date}.csv
│   ├── master/                   # Merged master CSV (all merchants)
│   └── state.json                # Run history, file hashes, last success per merchant
├── tests/
├── pyproject.toml
└── README.md
```

### Core Components

#### 1. CLI (`cli.py`)
```
corkscrew run                     # Run all enabled merchants
corkscrew run --merchant farr-vintners   # Run single merchant
corkscrew run --tier 1            # Run all Tier 1 merchants
corkscrew run --dry-run           # Show what would be downloaded
corkscrew status                  # Show last run status per merchant
corkscrew list                    # List all configured merchants
corkscrew merge                   # Generate master CSV from latest normalized files
```

Exit codes: 0 = all succeeded, 1 = some failed, 2 = config error.

#### 2. Downloader (`downloader.py`)
- Uses `httpx` with async support for parallel downloads
- Handles URL pattern resolution:
  - `static`: Use URL as-is
  - `dated`: Substitute `{YYYY}`, `{MM}`, `{DD}` with current date; if 404, walk back up to 7 days
  - `google_sheets`: Append `/export?format=csv` or `/export?format=xlsx`
  - `google_drive`: Use `drive.google.com/uc?export=download&id={id}`
  - `hub_wine`: Use `extranet.hub.wine/xlsx/{slug}` pattern
  - `rest_endpoint`: Use URL as-is
  - `dynamic_php`: Use URL as-is (server generates on demand)
- Retry logic: 3 attempts with exponential backoff (1s, 4s, 16s)
- Timeout: 60 seconds per download
- User-Agent: Realistic browser UA string (not `python-httpx`)
- Follows redirects (up to 5 hops)
- Validates response: checks Content-Type, minimum file size (>100 bytes), HTTP status
- Saves to `data/raw/{merchant_id}/{YYYY-MM-DD}/{original_filename}`

#### 3. Normalizer (`normalizer.py` + `normalizers/`)
- Base class with `normalize(filepath, merchant_config) -> list[WineRecord]`
- Registry: maps `merchant_id` to normalizer class (falls back to generic format-based normalizer)
- Format-specific base normalizers:
  - `XLSXNormalizer`: Uses `openpyxl` / `pandas` to read XLSX/XLS/XLSM
  - `CSVNormalizer`: Uses `pandas` with encoding detection (`chardet`)
  - `JSONNormalizer`: Loads JSON, flattens to records
  - `PDFNormalizer`: Uses `pdfplumber` for table extraction (best-effort; PDFs are messy)
- Per-merchant overrides define column mappings, e.g.:
  ```python
  class FarrVintnersNormalizer(CSVNormalizer):
      column_map = {
          "Wine": "wine_name",
          "Vintage": "vintage",
          "Region": "region",
          "Price": "price",
          # ...
      }
  ```
- Outputs `data/normalized/{merchant_id}/{YYYY-MM-DD}.csv`

#### 4. Storage & State (`storage.py`)
- Computes SHA-256 hash of each downloaded file
- Maintains `data/state.json`:
  ```json
  {
    "farr-vintners": {
      "last_run": "2026-02-23T14:00:00Z",
      "last_success": "2026-02-23T14:00:00Z",
      "last_hash": "a1b2c3d4...",
      "last_file": "data/raw/farr-vintners/2026-02-23/winelist.csv",
      "changed": true,
      "consecutive_failures": 0,
      "history": [
        {"date": "2026-02-23", "hash": "a1b2c3d4...", "status": "success", "changed": true},
        {"date": "2026-02-22", "hash": "a1b2c3d4...", "status": "success", "changed": false}
      ]
    }
  }
  ```
- Staleness detection: if hash unchanged for N consecutive runs, flag in status output
- History is kept for last 30 runs per merchant (configurable)

---

## Technical Requirements

### Runtime
- Python 3.11+
- No web framework (CLI only)
- Async HTTP via `httpx[http2]`

### Dependencies
```
httpx[http2]        # HTTP client with HTTP/2 support
pyyaml              # Config file parsing
pydantic            # Config + data model validation
pandas              # Data normalization + CSV/Excel reading
openpyxl            # XLSX reading
xlrd                # Legacy XLS reading
chardet             # Encoding detection for CSV files
pdfplumber          # PDF table extraction (best-effort)
click               # CLI framework
rich                # Pretty terminal output (status tables, progress bars)
```

### Performance
- Parallel downloads: up to 10 concurrent HTTP requests (configurable)
- Sequential normalization (I/O bound on disk, not worth parallelizing in V1)
- Full run for ~40 merchants should complete in under 5 minutes

### Error Handling
- Per-merchant error isolation: one merchant failing does not stop others
- Errors logged with full context (merchant, URL, HTTP status, response headers)
- Failed merchants are retried on next run
- Consecutive failure counter triggers warning after 3 failures, alert after 7

---

## Output Examples

### CLI Status Output
```
$ corkscrew status

Merchant                    Last Run     Status    Changed  Hash (first 8)
─────────────────────────────────────────────────────────────────────────
Farr Vintners               2h ago       ✅ OK      Yes     a1b2c3d4
BiBo Wine                   2h ago       ✅ OK      No      e5f6g7h8
Trinkreif                   2h ago       ✅ OK      Yes     i9j0k1l2
Maison Jude                 2h ago       ⚠️ Stale   No      m3n4o5p6  (7 days)
Vintage Grand Cru           2h ago       ✅ OK      Yes     q7r8s9t0
Private Cellar              2h ago       ❌ Failed  -       -          (HTTP 503)

40 merchants | 37 OK | 1 stale | 2 failed
```

### CLI Run Output
```
$ corkscrew run

[14:00:01] Starting run for 40 merchants (10 concurrent)
[14:00:02] ✅ farr-vintners          winelist.csv (245 KB, changed)
[14:00:02] ✅ bibo-wine              bibo.xlsx (89 KB, unchanged)
[14:00:03] ✅ cave-bb                ExportPreisliste.xlsx (312 KB, changed)
[14:00:03] ✅ trinkreif              Gesamtpreisliste-23-02-2026.xlsx (156 KB, changed)
[14:00:04] ❌ private-cellar         HTTP 503 Service Unavailable (attempt 3/3)
...
[14:00:38] Run complete: 38/40 succeeded, 2 failed, 22 changed

Normalizing 22 changed files...
[14:00:39] ✅ farr-vintners          4,231 wines normalized
[14:00:40] ✅ cave-bb                1,847 wines normalized
...
[14:01:02] Normalization complete: 22 files, 28,445 total wine records
```

---

## Rollout Plan

### Phase 1: Foundation (Days 1–2)
- Project scaffolding, config schema, YAML loader with validation
- HTTP downloader with all URL pattern resolvers
- State management (hashing, history tracking)
- CLI skeleton with `run`, `status`, `list` commands

### Phase 2: Normalizers (Days 3–4)
- Generic XLSX/CSV/JSON normalizers
- Per-merchant normalizer overrides for top-priority merchants:
  - Farr Vintners (CSV — gold standard, use to validate schema)
  - hub.wine shared normalizer (covers 5 merchants)
  - Cave BB, Lucullus, Vintage Grand Cru (REST endpoints)
  - Google Sheets shared normalizer (covers 3 merchants)
- Remaining merchants get generic normalizer + column map configs

### Phase 3: Polish (Day 5)
- Master CSV merge command
- Staleness detection + alerting thresholds
- PDF normalizer (best-effort with pdfplumber)
- Error reporting improvements
- README + usage documentation
- Populate full `merchants.yaml` with all ~40 merchant configs

### Phase 4: Validation (Day 6)
- Full run against all merchants, verify downloads + normalization
- Fix edge cases (encoding issues, unexpected column layouts, date format variations)
- Add any missing merchant-specific normalizer overrides

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Merchants covered | ≥35 out of ~40 Tier 1 merchants |
| Download success rate | ≥90% per run |
| Normalization coverage | ≥80% of downloaded files produce valid normalized CSV |
| Full run time | <5 minutes |
| Zero manual intervention for routine runs | Cron-compatible with meaningful exit codes |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Merchants change URLs without notice | High | Medium | Staleness detection + consecutive failure alerts; V3 adds self-healing |
| Excel column layouts vary between merchant updates | Medium | Medium | Per-merchant normalizers with explicit column maps; validation warnings on unexpected columns |
| Google Sheet IDs change on re-upload | Medium | Low | V2/V3 re-scrapes landing page to discover new IDs |
| Rate limiting / IP blocking | Low | Medium | Polite defaults (1 req/s per domain), realistic UA, randomized delays |
| PDF tables too messy for automated extraction | High | Low | PDF normalizer is best-effort; prefer XLSX/CSV when both available |
| Dated URL patterns break on holidays/weekends | Low | Low | Walk-back logic tries last 7 days |

---

## Future (V2/V3 Hooks)

The following extension points are designed into V1 for forward compatibility:

- `tier` field in config: V1 only processes `tier: 1`; V2 adds 2, V3 adds 3
- `auth` field in config: V1 ignores non-null; V2 implements `nonce`, `age_gate`
- `url_pattern` field: V1 handles static patterns; V2 adds `browser_click`, `session_aware`
- Normalizer registry: V2 adds `HTMLNormalizer` for scraping rendered pages
- State schema: extensible for V3's self-healing metadata (last_discovery_run, discovered_urls, etc.)