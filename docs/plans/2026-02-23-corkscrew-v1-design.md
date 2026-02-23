# Corkscrew V1 — Design Document
**Date:** 2026-02-23
**Status:** Approved

---

## Summary

Corkscrew V1 is a Python CLI tool that downloads wine inventory files from ~40 Tier-1 wine merchants (direct, unauthenticated HTTP GET) and normalizes them into a standard CSV schema.

---

## Decisions from Brainstorming

| Decision | Choice | Rationale |
|---|---|---|
| Merchants requiring JS rendering / HTML scraping | Hardcode direct file URLs manually | One-time manual research fits V1 HTTP-only constraint |
| PDF normalization | Download + hash only; emit warning on normalization attempt | PDFs are messy; XLSX/CSV alternatives exist for most PDF merchants |
| Testing | Unit tests for core logic only (no live HTTP) | Validates URL resolution, config parsing, hashing, column mapping |
| Implementation approach | Faithful PRD (Approach A) | PRD is detailed enough for direct translation |

---

## Architecture

```
corkscrew/
├── corkscrew/
│   ├── cli.py          # click CLI: run, status, list, merge
│   ├── config.py       # YAML loader + pydantic validation
│   ├── downloader.py   # async httpx, semaphore(10), 5 URL archetypes
│   ├── normalizer.py   # BaseNormalizer + format dispatchers
│   ├── normalizers/    # Per-merchant overrides
│   │   ├── __init__.py
│   │   ├── farr_vintners.py
│   │   ├── hub_wine.py
│   │   ├── google_sheets.py
│   │   └── cave_bb.py
│   ├── storage.py      # SHA-256 hashing, state.json, history
│   └── models.py       # Pydantic: MerchantConfig, WineRecord, DownloadResult
├── merchants.yaml      # ~40 merchant configurations
├── data/
│   ├── raw/            # {merchant_id}/{YYYY-MM-DD}/{filename}
│   ├── normalized/     # {merchant_id}/{YYYY-MM-DD}.csv
│   ├── master/         # master.csv (merged)
│   └── state.json      # run history, hashes, failure counts
├── tests/
│   ├── test_config.py
│   ├── test_downloader.py
│   ├── test_normalizer.py
│   └── test_storage.py
├── pyproject.toml
└── README.md
```

---

## Core Components

### Downloader (`downloader.py`)
- `httpx.AsyncClient` with `asyncio.Semaphore(10)`
- URL pattern handlers:
  - `static`: URL used as-is
  - `dated`: Substitute `{YYYY}`, `{MM}`, `{DD}` with today; walk back up to 7 days on 404
  - `google_sheets`: Append `/export?format=csv` (or xlsx)
  - `google_drive`: `drive.google.com/uc?export=download&id={id}`
  - `hub_wine`: `extranet.hub.wine/xlsx/{slug}`
  - `rest_endpoint`: URL used as-is
  - `dynamic_php`: URL used as-is
- Retry: 3 attempts, exponential backoff (1s → 4s → 16s)
- Timeout: 60s per download
- User-Agent: realistic browser string
- Validates: HTTP 200, Content-Type, file size > 100 bytes
- Saves to: `data/raw/{merchant_id}/{YYYY-MM-DD}/{filename}`
- Returns: `DownloadResult(merchant_id, filepath, hash, changed, status_code, bytes_downloaded)`

### Normalizer (`normalizer.py` + `normalizers/`)
- `BaseNormalizer.normalize(filepath, config) → list[WineRecord]`
- Format dispatchers: `XLSXNormalizer` (openpyxl/pandas), `CSVNormalizer` (pandas + chardet), `JSONNormalizer`, `PDFNormalizer` (stub — emits warning, returns [])
- Per-merchant lookup by `merchant_id`; falls back to format-based dispatcher
- Column maps defined in merchant YAML config where possible; Python class overrides for complex transformations only
- Output: `data/normalized/{merchant_id}/{YYYY-MM-DD}.csv`

### Storage (`storage.py`)
- `compute_hash(filepath) → str` (SHA-256, hex)
- `load_state() / save_state()` for `data/state.json`
- Staleness: consecutive `changed=False` runs tracked; warning threshold configurable
- History: last 30 runs per merchant

### CLI (`cli.py`)
- `corkscrew run [--merchant ID] [--tier N] [--dry-run]`
- `corkscrew status` — rich table (merchant, last run, status, changed, hash[:8], consecutive failures)
- `corkscrew list` — tabular list of all configured merchants
- `corkscrew merge` — concatenate latest normalized CSVs → `data/master/master.csv`
- Exit codes: `0`=all OK, `1`=partial failure, `2`=config error

---

## Data Flow

```
1. Load + validate merchants.yaml
2. Filter: enabled=true, tier=1 (or --tier / --merchant flags)
3. Async download all filtered merchants (semaphore=10)
   ├─ dated URLs: try today, walk back up to 7 days on 404
   ├─ non-200 after 3 retries → FAILED (continue other merchants)
   └─ save file to data/raw/
4. For each successful download:
   ├─ compute SHA-256 hash
   ├─ compare to state.json last_hash
   ├─ unchanged → skip normalization, log "unchanged"
   └─ changed → run normalizer → write normalized CSV
5. Update state.json (last_run, last_success, last_hash, changed, consecutive_failures, history)
6. Print rich summary
7. Exit with appropriate code
```

---

## Error Handling

- **Per-merchant isolation**: one failure never blocks other merchants
- **Error context captured**: merchant ID, URL, HTTP status, response headers
- **Consecutive failure alerting**: ⚠️ warning at 3, 🔴 critical at 7 (shown in `corkscrew status`)
- **Config errors**: fatal, exit code 2 before any downloads begin

---

## Testing Strategy

Unit tests only (no live HTTP):

| Test File | Coverage |
|---|---|
| `test_config.py` | YAML loading, pydantic validation, edge cases |
| `test_downloader.py` | URL pattern resolution, dated walkback, google_sheets/drive transforms |
| `test_normalizer.py` | Column mapping with synthetic CSV/XLSX fixtures |
| `test_storage.py` | Hash computation, staleness detection, state.json read/write |

---

## Merchant Edge Cases

| Merchant | Issue | Resolution |
|---|---|---|
| Albany Vintners (#12) | JS-rendered download links | Manually research + hardcode direct URL |
| GRW Wine Collection (#30) | Shopify page links | Manually research + hardcode direct URL |
| Great Ocean Industrial (#61) | Shopify page links | Manually research + hardcode direct URL |
| 1870 Vins et Conseils (#74) | PDF links in nav | Manually research + hardcode direct URL |
| In Vino Veritas (#1) | URL extraction from .htm page | Manually research + hardcode direct URL |
| PDF-only merchants | No XLSX/CSV alternative | Download + hash; normalization emits warning |
| Trinkreif / Ganpei | Date-stamped URLs | Dated URL pattern with 7-day walkback |

---

## Dependencies

```toml
httpx[http2]    # HTTP client
pyyaml          # Config parsing
pydantic        # Data validation
pandas          # CSV/Excel normalization
openpyxl        # XLSX reading
xlrd            # Legacy XLS reading
chardet         # CSV encoding detection
click           # CLI framework
rich            # Terminal output
pytest          # Unit testing
pytest-asyncio  # Async test support
```

---

## Rollout Phases

| Phase | Days | Deliverables |
|---|---|---|
| 1: Foundation | 1–2 | Scaffolding, config schema, downloader, storage, CLI skeleton |
| 2: Normalizers | 3–4 | XLSX/CSV/JSON normalizers, priority merchant overrides, full merchants.yaml |
| 3: Polish | 5 | merge command, staleness alerting, error reporting, README |
| 4: Validation | 6 | Full run against all merchants, fix edge cases |
