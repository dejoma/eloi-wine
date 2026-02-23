# Corkscrew V1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI tool that downloads wine inventory files from ~40 Tier-1 wine merchants and normalizes them into a standard CSV schema.

**Architecture:** Single Python package (`corkscrew/`) with async httpx downloader, pydantic config validation, pandas-based normalizers, and a click CLI. State is tracked in `data/state.json` using SHA-256 file hashes. Per-merchant normalizer classes handle column mapping; most merchants use a generic YAML-driven column map.

**Tech Stack:** Python 3.11+, httpx[http2], pydantic v2, pandas, openpyxl, xlrd, chardet, click, rich, pyyaml, pytest, pytest-asyncio

**Design Doc:** `docs/plans/2026-02-23-corkscrew-v1-design.md`

---

## Phase 1: Foundation

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `corkscrew/__init__.py`
- Create: `corkscrew/cli.py` (stub)
- Create: `corkscrew/config.py` (stub)
- Create: `corkscrew/downloader.py` (stub)
- Create: `corkscrew/normalizer.py` (stub)
- Create: `corkscrew/normalizers/__init__.py`
- Create: `corkscrew/storage.py` (stub)
- Create: `corkscrew/models.py` (stub)
- Create: `tests/__init__.py`
- Create: `tests/fixtures/` (empty dir for test data)
- Create: `data/raw/.gitkeep`
- Create: `data/normalized/.gitkeep`
- Create: `data/master/.gitkeep`
- Create: `.gitignore`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "corkscrew"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "httpx[http2]>=0.27",
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "pandas>=2.0",
    "openpyxl>=3.1",
    "xlrd>=2.0",
    "chardet>=5.0",
    "click>=8.1",
    "rich>=13.0",
]

[project.scripts]
corkscrew = "corkscrew.cli:cli"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Step 2: Create all stub files and directories**

```bash
mkdir -p corkscrew/normalizers tests/fixtures data/raw data/normalized data/master
touch corkscrew/__init__.py corkscrew/normalizers/__init__.py tests/__init__.py
touch data/raw/.gitkeep data/normalized/.gitkeep data/master/.gitkeep
```

Create `corkscrew/models.py` (empty stubs — will be filled in Task 2):
```python
# models.py — filled in Task 2
```

Create `corkscrew/config.py`:
```python
# config.py — filled in Task 3
```

Create `corkscrew/storage.py`:
```python
# storage.py — filled in Task 4
```

Create `corkscrew/downloader.py`:
```python
# downloader.py — filled in Tasks 5+6
```

Create `corkscrew/normalizer.py`:
```python
# normalizer.py — filled in Task 8
```

Create `corkscrew/cli.py`:
```python
import click

@click.group()
def cli():
    """Corkscrew — Wine Merchant Inventory Scraper"""
    pass
```

Create `.gitignore`:
```
__pycache__/
*.pyc
*.egg-info/
dist/
.venv/
data/raw/
data/normalized/
data/master/
data/state.json
!data/raw/.gitkeep
!data/normalized/.gitkeep
!data/master/.gitkeep
```

**Step 3: Install in dev mode**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**Step 4: Verify CLI entry point works**

```bash
corkscrew --help
```

Expected output:
```
Usage: corkscrew [OPTIONS] COMMAND [ARGS]...
  Corkscrew — Wine Merchant Inventory Scraper
```

**Step 5: Commit**

```bash
git init
git add .
git commit -m "feat: project scaffolding and dependencies"
```

---

### Task 2: Pydantic Models

**Files:**
- Create: `corkscrew/models.py`
- Create: `tests/test_models.py`

**Step 1: Write failing tests**

```python
# tests/test_models.py
import pytest
from pydantic import ValidationError
from corkscrew.models import DownloadConfig, MerchantConfig, WineRecord, DownloadResult, MerchantState

def test_download_config_requires_url_and_format():
    with pytest.raises(ValidationError):
        DownloadConfig(url="https://example.com/file.xlsx")  # missing format

def test_download_config_valid():
    dc = DownloadConfig(url="https://example.com/file.xlsx", format="xlsx", preferred=True)
    assert dc.url == "https://example.com/file.xlsx"
    assert dc.preferred is True

def test_merchant_config_valid():
    mc = MerchantConfig(
        id="farr-vintners",
        name="Farr Vintners",
        country="UK",
        tier=1,
        enabled=True,
        discovery_url="https://farrvintners.com/",
        downloads=[
            DownloadConfig(url="https://farrvintners.com/winelist_csv.php?output=csv", format="csv", preferred=True)
        ],
        url_pattern="static",
    )
    assert mc.id == "farr-vintners"
    assert len(mc.downloads) == 1

def test_merchant_config_preferred_download():
    mc = MerchantConfig(
        id="test", name="Test", country="UK", tier=1, enabled=True,
        discovery_url="https://example.com",
        downloads=[
            DownloadConfig(url="https://example.com/a.csv", format="csv", preferred=False),
            DownloadConfig(url="https://example.com/b.xlsx", format="xlsx", preferred=True),
        ],
        url_pattern="static",
    )
    preferred = mc.preferred_download
    assert preferred.format == "xlsx"

def test_wine_record_empty_fields_are_empty_string():
    wr = WineRecord(merchant_id="test", merchant_name="Test", wine_name="Pétrus", source_url="https://x.com", download_date="2026-02-23")
    assert wr.vintage == ""
    assert wr.region == ""

def test_download_result_creation():
    dr = DownloadResult(merchant_id="test", filepath="/tmp/x.csv", file_hash="abc123", changed=True, status_code=200, bytes_downloaded=1024)
    assert dr.success is True

def test_download_result_failure():
    dr = DownloadResult(merchant_id="test", filepath=None, file_hash=None, changed=False, status_code=503, bytes_downloaded=0, error="HTTP 503")
    assert dr.success is False
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_models.py -v
```

Expected: `ImportError: cannot import name 'DownloadConfig' from 'corkscrew.models'`

**Step 3: Implement models.py**

```python
# corkscrew/models.py
from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, model_validator


class DownloadConfig(BaseModel):
    url: str
    format: Literal["xlsx", "xls", "xlsm", "csv", "json", "txt", "pdf", "zip"]
    preferred: bool = False
    label: Optional[str] = None


class MerchantConfig(BaseModel):
    id: str
    name: str
    country: str
    tier: int
    enabled: bool
    discovery_url: str
    downloads: list[DownloadConfig]
    url_pattern: Literal["static", "dated", "google_sheets", "google_drive", "hub_wine", "rest_endpoint", "dynamic_php"]
    date_pattern: Optional[str] = None
    auth: Optional[str] = None
    google_sheet_id: Optional[str] = None
    google_drive_id: Optional[str] = None
    hub_wine_slug: Optional[str] = None
    column_map: Optional[dict[str, str]] = None
    notes: Optional[str] = None

    @property
    def preferred_download(self) -> DownloadConfig:
        for d in self.downloads:
            if d.preferred:
                return d
        return self.downloads[0]


class WineRecord(BaseModel):
    merchant_id: str
    merchant_name: str
    wine_name: str
    vintage: str = ""
    region: str = ""
    sub_region: str = ""
    appellation: str = ""
    color: str = ""
    format: str = ""
    price: str = ""
    currency: str = ""
    stock_quantity: str = ""
    case_size: str = ""
    score: str = ""
    scorer: str = ""
    condition_notes: str = ""
    source_url: str
    download_date: str

    def to_row(self) -> dict:
        return self.model_dump()


class DownloadResult(BaseModel):
    merchant_id: str
    filepath: Optional[str]
    file_hash: Optional[str]
    changed: bool
    status_code: int
    bytes_downloaded: int
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.status_code == 200 and self.filepath is not None


class MerchantState(BaseModel):
    last_run: Optional[str] = None
    last_success: Optional[str] = None
    last_hash: Optional[str] = None
    last_file: Optional[str] = None
    changed: bool = False
    consecutive_failures: int = 0
    history: list[dict] = []
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_models.py -v
```

Expected: All 7 tests pass.

**Step 5: Commit**

```bash
git add corkscrew/models.py tests/test_models.py
git commit -m "feat: pydantic models for merchant config and wine records"
```

---

### Task 3: Config Loader

**Files:**
- Create: `corkscrew/config.py`
- Create: `tests/test_config.py`
- Create: `tests/fixtures/merchants_test.yaml`

**Step 1: Create test fixture YAML**

```yaml
# tests/fixtures/merchants_test.yaml
merchants:
  - id: "farr-vintners"
    name: "Farr Vintners"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.farrvintners.com/downloads/"
    downloads:
      - url: "https://www.farrvintners.com/winelist_csv.php?output=csv"
        format: "csv"
        preferred: true
        label: "CSV full list"
    url_pattern: "static"
    notes: "Gold standard"

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
    url_pattern: "hub_wine"
    hub_wine_slug: "bibo"

  - id: "disabled-merchant"
    name: "Disabled"
    country: "UK"
    tier: 1
    enabled: false
    discovery_url: "https://example.com/"
    downloads:
      - url: "https://example.com/file.csv"
        format: "csv"
        preferred: true
    url_pattern: "static"
```

**Step 2: Write failing tests**

```python
# tests/test_config.py
import pytest
from pathlib import Path
from corkscrew.config import load_config, ConfigError

FIXTURE = Path(__file__).parent / "fixtures" / "merchants_test.yaml"

def test_load_config_returns_merchant_list():
    merchants = load_config(FIXTURE)
    assert len(merchants) == 3

def test_load_config_parses_merchant_fields():
    merchants = load_config(FIXTURE)
    farr = next(m for m in merchants if m.id == "farr-vintners")
    assert farr.name == "Farr Vintners"
    assert farr.country == "UK"
    assert farr.tier == 1
    assert farr.enabled is True
    assert len(farr.downloads) == 1
    assert farr.downloads[0].preferred is True

def test_load_config_enabled_only_filter():
    merchants = load_config(FIXTURE, enabled_only=True)
    ids = [m.id for m in merchants]
    assert "disabled-merchant" not in ids
    assert "farr-vintners" in ids

def test_load_config_tier_filter():
    merchants = load_config(FIXTURE, tier=1)
    assert all(m.tier == 1 for m in merchants)

def test_load_config_missing_file_raises():
    with pytest.raises(ConfigError):
        load_config(Path("/nonexistent/merchants.yaml"))

def test_load_config_invalid_yaml_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("merchants: [invalid: yaml: content")
    with pytest.raises(ConfigError):
        load_config(bad)
```

**Step 3: Run to verify failures**

```bash
pytest tests/test_config.py -v
```

Expected: `ImportError` or `ModuleNotFoundError`

**Step 4: Implement config.py**

```python
# corkscrew/config.py
from pathlib import Path
from typing import Optional
import yaml
from pydantic import ValidationError
from corkscrew.models import MerchantConfig


class ConfigError(Exception):
    pass


def load_config(
    path: Path,
    enabled_only: bool = False,
    tier: Optional[int] = None,
    merchant_id: Optional[str] = None,
) -> list[MerchantConfig]:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {path}: {e}")

    if not isinstance(raw, dict) or "merchants" not in raw:
        raise ConfigError(f"Config missing 'merchants' key: {path}")

    merchants = []
    for item in raw["merchants"]:
        try:
            merchants.append(MerchantConfig(**item))
        except ValidationError as e:
            raise ConfigError(f"Invalid merchant config for {item.get('id', '?')}: {e}")

    if enabled_only:
        merchants = [m for m in merchants if m.enabled]
    if tier is not None:
        merchants = [m for m in merchants if m.tier == tier]
    if merchant_id is not None:
        merchants = [m for m in merchants if m.id == merchant_id]

    return merchants
```

**Step 5: Run tests to verify they pass**

```bash
pytest tests/test_config.py -v
```

Expected: All 6 tests pass.

**Step 6: Commit**

```bash
git add corkscrew/config.py tests/test_config.py tests/fixtures/merchants_test.yaml
git commit -m "feat: YAML config loader with pydantic validation"
```

---

### Task 4: Storage Module

**Files:**
- Create: `corkscrew/storage.py`
- Create: `tests/test_storage.py`

**Step 1: Write failing tests**

```python
# tests/test_storage.py
import json
import pytest
from pathlib import Path
from corkscrew.storage import compute_hash, StorageManager

def test_compute_hash_is_deterministic(tmp_path):
    f = tmp_path / "test.csv"
    f.write_bytes(b"wine,vintage\nPetrus,2019")
    h1 = compute_hash(f)
    h2 = compute_hash(f)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex

def test_compute_hash_differs_for_different_content(tmp_path):
    f1 = tmp_path / "a.csv"
    f2 = tmp_path / "b.csv"
    f1.write_bytes(b"content A")
    f2.write_bytes(b"content B")
    assert compute_hash(f1) != compute_hash(f2)

def test_storage_manager_initial_state(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    state = sm.get_merchant_state("farr-vintners")
    assert state.last_hash is None
    assert state.consecutive_failures == 0

def test_storage_manager_record_success(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    sm.record_success("farr-vintners", hash_val="abc123", filepath="data/raw/farr/x.csv", changed=True)
    state = sm.get_merchant_state("farr-vintners")
    assert state.last_hash == "abc123"
    assert state.consecutive_failures == 0
    assert state.changed is True

def test_storage_manager_record_failure_increments_counter(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    sm.record_failure("test-merchant", error="HTTP 503")
    sm.record_failure("test-merchant", error="HTTP 503")
    state = sm.get_merchant_state("test-merchant")
    assert state.consecutive_failures == 2

def test_storage_manager_success_resets_failure_counter(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    sm.record_failure("test-merchant", error="HTTP 503")
    sm.record_failure("test-merchant", error="HTTP 503")
    sm.record_success("test-merchant", hash_val="x", filepath="x", changed=True)
    state = sm.get_merchant_state("test-merchant")
    assert state.consecutive_failures == 0

def test_storage_manager_detects_unchanged(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    sm.record_success("test", hash_val="abc", filepath="x.csv", changed=True)
    is_changed = sm.is_changed("test", "abc")
    assert is_changed is False

def test_storage_manager_detects_changed(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    sm.record_success("test", hash_val="abc", filepath="x.csv", changed=True)
    is_changed = sm.is_changed("test", "xyz")
    assert is_changed is True

def test_storage_manager_history_capped_at_30(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    for i in range(35):
        sm.record_success("test", hash_val=f"hash{i}", filepath="x", changed=True)
    state = sm.get_merchant_state("test")
    assert len(state.history) <= 30

def test_storage_manager_persists_across_instances(tmp_path):
    state_file = tmp_path / "state.json"
    sm1 = StorageManager(state_file)
    sm1.record_success("test", hash_val="abc123", filepath="x.csv", changed=True)
    sm2 = StorageManager(state_file)
    state = sm2.get_merchant_state("test")
    assert state.last_hash == "abc123"
```

**Step 2: Run to verify failures**

```bash
pytest tests/test_storage.py -v
```

Expected: `ImportError`

**Step 3: Implement storage.py**

```python
# corkscrew/storage.py
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from corkscrew.models import MerchantState

HISTORY_LIMIT = 30


def compute_hash(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


class StorageManager:
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self._data: dict = self._load()

    def _load(self) -> dict:
        if self.state_path.exists():
            return json.loads(self.state_path.read_text())
        return {}

    def _save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self._data, indent=2))

    def get_merchant_state(self, merchant_id: str) -> MerchantState:
        return MerchantState(**self._data.get(merchant_id, {}))

    def is_changed(self, merchant_id: str, new_hash: str) -> bool:
        state = self.get_merchant_state(merchant_id)
        return state.last_hash != new_hash

    def record_success(self, merchant_id: str, hash_val: str, filepath: str, changed: bool):
        now = datetime.now(timezone.utc).isoformat()
        existing = self._data.get(merchant_id, {})
        history = existing.get("history", [])
        history.append({"date": now[:10], "hash": hash_val, "status": "success", "changed": changed})
        if len(history) > HISTORY_LIMIT:
            history = history[-HISTORY_LIMIT:]
        self._data[merchant_id] = {
            "last_run": now,
            "last_success": now,
            "last_hash": hash_val,
            "last_file": filepath,
            "changed": changed,
            "consecutive_failures": 0,
            "history": history,
        }
        self._save()

    def record_failure(self, merchant_id: str, error: str):
        now = datetime.now(timezone.utc).isoformat()
        existing = self._data.get(merchant_id, {})
        history = existing.get("history", [])
        history.append({"date": now[:10], "hash": None, "status": "failed", "changed": False, "error": error})
        if len(history) > HISTORY_LIMIT:
            history = history[-HISTORY_LIMIT:]
        failures = existing.get("consecutive_failures", 0) + 1
        self._data[merchant_id] = {
            **existing,
            "last_run": now,
            "consecutive_failures": failures,
            "history": history,
        }
        self._save()
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_storage.py -v
```

Expected: All 9 tests pass.

**Step 5: Commit**

```bash
git add corkscrew/storage.py tests/test_storage.py
git commit -m "feat: storage manager with SHA-256 hashing and state tracking"
```

---

### Task 5: URL Pattern Resolver

**Files:**
- Create: `corkscrew/url_resolver.py`
- Create: `tests/test_url_resolver.py`

**Step 1: Write failing tests**

```python
# tests/test_url_resolver.py
import pytest
from datetime import date
from corkscrew.url_resolver import resolve_url, generate_dated_candidates

def test_static_url_unchanged():
    url = "https://example.com/file.xlsx"
    assert resolve_url("static", url) == [url]

def test_rest_endpoint_unchanged():
    url = "https://example.com/api/export"
    assert resolve_url("rest_endpoint", url) == [url]

def test_dynamic_php_unchanged():
    url = "https://example.com/export.php?type=csv"
    assert resolve_url("dynamic_php", url) == [url]

def test_hub_wine_uses_extranet_pattern():
    url = "https://extranet.hub.wine/xlsx/bibo"
    result = resolve_url("hub_wine", url)
    assert result == [url]

def test_google_sheets_appends_export():
    url = "https://docs.google.com/spreadsheets/d/SHEET_ID"
    result = resolve_url("google_sheets", url)
    assert result == [f"{url}/export?format=csv"]

def test_google_sheets_already_has_export():
    url = "https://docs.google.com/spreadsheets/d/SHEET_ID/export?format=csv"
    result = resolve_url("google_sheets", url)
    assert result == [url]

def test_google_drive_uses_uc_export():
    url = "https://drive.google.com/file/d/FILE_ID/view"
    result = resolve_url("google_drive", url, google_drive_id="FILE_ID")
    assert result == ["https://drive.google.com/uc?export=download&id=FILE_ID"]

def test_dated_url_generates_candidates():
    url = "https://example.com/{YYYY}/{MM}/file-{DD}-{MM}-{YYYY}.xlsx"
    candidates = resolve_url("dated", url, reference_date=date(2026, 2, 23))
    assert len(candidates) == 7
    assert candidates[0] == "https://example.com/2026/02/file-23-02-2026.xlsx"
    assert candidates[1] == "https://example.com/2026/02/file-22-02-2026.xlsx"

def test_dated_url_walkback_crosses_month():
    url = "https://example.com/{YYYY}/{MM}/file-{DD}-{MM}-{YYYY}.xlsx"
    candidates = resolve_url("dated", url, reference_date=date(2026, 3, 2))
    # Day 7 back = Feb 23
    assert candidates[6] == "https://example.com/2026/02/file-23-02-2026.xlsx"

def test_generate_dated_candidates_returns_7():
    url = "https://x.com/{YYYY}-{MM}-{DD}.xlsx"
    candidates = generate_dated_candidates(url, reference_date=date(2026, 2, 23))
    assert len(candidates) == 7
    dates = [c for c in candidates]
    assert "https://x.com/2026-02-23.xlsx" in dates
    assert "https://x.com/2026-02-17.xlsx" in dates
```

**Step 2: Run to verify failures**

```bash
pytest tests/test_url_resolver.py -v
```

**Step 3: Implement url_resolver.py**

```python
# corkscrew/url_resolver.py
from datetime import date, timedelta
from typing import Optional


def _substitute_date(url: str, d: date) -> str:
    return (
        url.replace("{YYYY}", str(d.year))
           .replace("{MM}", f"{d.month:02d}")
           .replace("{DD}", f"{d.day:02d}")
    )


def generate_dated_candidates(url: str, reference_date: Optional[date] = None, days: int = 7) -> list[str]:
    if reference_date is None:
        reference_date = date.today()
    return [_substitute_date(url, reference_date - timedelta(days=i)) for i in range(days)]


def resolve_url(
    pattern: str,
    url: str,
    reference_date: Optional[date] = None,
    google_drive_id: Optional[str] = None,
) -> list[str]:
    if pattern in ("static", "rest_endpoint", "dynamic_php", "hub_wine"):
        return [url]
    if pattern == "dated":
        return generate_dated_candidates(url, reference_date)
    if pattern == "google_sheets":
        if "export?" in url:
            return [url]
        return [f"{url.rstrip('/')}/export?format=csv"]
    if pattern == "google_drive":
        drive_id = google_drive_id or _extract_drive_id(url)
        return [f"https://drive.google.com/uc?export=download&id={drive_id}"]
    return [url]


def _extract_drive_id(url: str) -> str:
    # Handles: drive.google.com/file/d/{ID}/view or /uc?id={ID}
    if "uc?export=download&id=" in url:
        return url.split("id=")[-1]
    if "/file/d/" in url:
        return url.split("/file/d/")[1].split("/")[0]
    if "id=" in url:
        return url.split("id=")[-1].split("&")[0]
    return url
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_url_resolver.py -v
```

Expected: All 10 tests pass.

**Step 5: Commit**

```bash
git add corkscrew/url_resolver.py tests/test_url_resolver.py
git commit -m "feat: URL pattern resolver with dated walkback and Google transforms"
```

---

### Task 6: HTTP Downloader

**Files:**
- Create: `corkscrew/downloader.py`
- Create: `tests/test_downloader.py`

**Step 1: Write failing tests (using unittest.mock for HTTP)**

```python
# tests/test_downloader.py
import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from corkscrew.downloader import Downloader
from corkscrew.models import MerchantConfig, DownloadConfig


def make_merchant(url_pattern="static", url="https://example.com/file.xlsx", fmt="xlsx"):
    return MerchantConfig(
        id="test-merchant", name="Test", country="UK", tier=1, enabled=True,
        discovery_url="https://example.com",
        downloads=[DownloadConfig(url=url, format=fmt, preferred=True)],
        url_pattern=url_pattern,
    )


@pytest.mark.asyncio
async def test_download_saves_file(tmp_path):
    merchant = make_merchant()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/octet-stream"}
    mock_response.content = b"wine,vintage\nPetrus,2019"

    with patch("corkscrew.downloader.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        downloader = Downloader(output_root=tmp_path)
        result = await downloader.download(merchant)

    assert result.success
    assert result.merchant_id == "test-merchant"
    assert result.bytes_downloaded == len(b"wine,vintage\nPetrus,2019")


@pytest.mark.asyncio
async def test_download_returns_failure_on_404(tmp_path):
    merchant = make_merchant()
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.headers = {}

    with patch("corkscrew.downloader.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        downloader = Downloader(output_root=tmp_path)
        result = await downloader.download(merchant)

    assert not result.success
    assert result.status_code == 404


@pytest.mark.asyncio
async def test_download_rejects_tiny_file(tmp_path):
    merchant = make_merchant()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/octet-stream"}
    mock_response.content = b"too small"  # < 100 bytes

    with patch("corkscrew.downloader.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        downloader = Downloader(output_root=tmp_path)
        result = await downloader.download(merchant)

    assert not result.success
    assert result.error is not None
    assert "too small" in result.error.lower()
```

**Step 2: Run to verify failures**

```bash
pytest tests/test_downloader.py -v
```

**Step 3: Implement downloader.py**

```python
# corkscrew/downloader.py
import asyncio
from datetime import date
from pathlib import Path
from typing import Optional
import httpx
from corkscrew.models import MerchantConfig, DownloadResult
from corkscrew.url_resolver import resolve_url
from corkscrew.storage import compute_hash

BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
MIN_FILE_SIZE = 100  # bytes
RETRY_DELAYS = [1, 4, 16]


class Downloader:
    def __init__(self, output_root: Path, concurrency: int = 10):
        self.output_root = output_root
        self.semaphore = asyncio.Semaphore(concurrency)

    async def download(self, merchant: MerchantConfig, ref_date: Optional[date] = None) -> DownloadResult:
        async with self.semaphore:
            return await self._download_with_retry(merchant, ref_date)

    async def _download_with_retry(self, merchant: MerchantConfig, ref_date: Optional[date]) -> DownloadResult:
        dl = merchant.preferred_download
        candidates = resolve_url(
            merchant.url_pattern,
            dl.url,
            reference_date=ref_date,
            google_drive_id=merchant.google_drive_id,
        )

        last_error = None
        for url in candidates:
            for attempt, delay in enumerate(RETRY_DELAYS + [None], 1):
                try:
                    result = await self._fetch(merchant, url, dl.format)
                    if result.success:
                        return result
                    if result.status_code == 404 and len(candidates) > 1:
                        break  # try next dated candidate
                    last_error = result.error
                    if attempt < len(RETRY_DELAYS) + 1 and delay:
                        await asyncio.sleep(delay)
                except Exception as e:
                    last_error = str(e)
                    if attempt < len(RETRY_DELAYS) + 1 and delay:
                        await asyncio.sleep(delay)

        return DownloadResult(
            merchant_id=merchant.id,
            filepath=None,
            file_hash=None,
            changed=False,
            status_code=0,
            bytes_downloaded=0,
            error=last_error or "All attempts failed",
        )

    async def _fetch(self, merchant: MerchantConfig, url: str, fmt: str) -> DownloadResult:
        async with httpx.AsyncClient(
            headers={"User-Agent": BROWSER_UA},
            follow_redirects=True,
            timeout=60.0,
        ) as client:
            resp = await client.get(url)

        if resp.status_code != 200:
            return DownloadResult(
                merchant_id=merchant.id, filepath=None, file_hash=None,
                changed=False, status_code=resp.status_code, bytes_downloaded=0,
                error=f"HTTP {resp.status_code}",
            )

        content = resp.content
        if len(content) < MIN_FILE_SIZE:
            return DownloadResult(
                merchant_id=merchant.id, filepath=None, file_hash=None,
                changed=False, status_code=200, bytes_downloaded=len(content),
                error=f"File too small ({len(content)} bytes)",
            )

        # Determine filename
        content_disp = resp.headers.get("content-disposition", "")
        if "filename=" in content_disp:
            fname = content_disp.split("filename=")[-1].strip('" ')
        else:
            fname = url.split("/")[-1].split("?")[0] or f"download.{fmt}"
        if "." not in fname:
            fname = f"{fname}.{fmt}"

        today = date.today().isoformat()
        out_dir = self.output_root / merchant.id / today
        out_dir.mkdir(parents=True, exist_ok=True)
        filepath = out_dir / fname
        filepath.write_bytes(content)

        file_hash = compute_hash(filepath)
        return DownloadResult(
            merchant_id=merchant.id,
            filepath=str(filepath),
            file_hash=file_hash,
            changed=True,  # caller checks state for real change detection
            status_code=200,
            bytes_downloaded=len(content),
        )

    async def download_all(self, merchants: list[MerchantConfig], ref_date: Optional[date] = None) -> list[DownloadResult]:
        tasks = [self.download(m, ref_date) for m in merchants]
        return await asyncio.gather(*tasks)
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_downloader.py -v
```

Expected: All 3 tests pass.

**Step 5: Commit**

```bash
git add corkscrew/downloader.py corkscrew/url_resolver.py tests/test_downloader.py
git commit -m "feat: async HTTP downloader with retry, URL pattern resolution"
```

---

## Phase 2: Normalizers

### Task 7: Base Normalizer + Format Dispatch

**Files:**
- Create: `corkscrew/normalizer.py`
- Create: `tests/test_normalizer.py`
- Create: `tests/fixtures/sample_wines.csv`
- Create: `tests/fixtures/sample_wines.xlsx` (created in test setup)

**Step 1: Create CSV test fixture**

```
# tests/fixtures/sample_wines.csv
Wine,Vintage,Region,Price,Currency,Stock
Pétrus,2019,Pomerol,4500.00,GBP,6
Mouton Rothschild,2018,Pauillac,650.00,GBP,12
Romanée-Conti,2017,Burgundy,25000.00,GBP,1
```

**Step 2: Write failing tests**

```python
# tests/test_normalizer.py
import pytest
import pandas as pd
from pathlib import Path
from datetime import date
from corkscrew.normalizer import NormalizerRegistry, CSVNormalizer, XLSXNormalizer, PDFNormalizer
from corkscrew.models import MerchantConfig, DownloadConfig, WineRecord

FIXTURES = Path(__file__).parent / "fixtures"

def make_merchant(merchant_id="test", column_map=None):
    return MerchantConfig(
        id=merchant_id, name="Test Merchant", country="UK", tier=1, enabled=True,
        discovery_url="https://example.com",
        downloads=[DownloadConfig(url="https://example.com/f.csv", format="csv", preferred=True)],
        url_pattern="static",
        column_map=column_map,
    )

def test_csv_normalizer_with_column_map():
    merchant = make_merchant(column_map={
        "Wine": "wine_name",
        "Vintage": "vintage",
        "Region": "region",
        "Price": "price",
        "Currency": "currency",
        "Stock": "stock_quantity",
    })
    normalizer = CSVNormalizer()
    records = normalizer.normalize(FIXTURES / "sample_wines.csv", merchant, download_date="2026-02-23")
    assert len(records) == 3
    assert records[0].wine_name == "Pétrus"
    assert records[0].vintage == "2019"
    assert records[0].price == "4500.0"
    assert records[0].merchant_id == "test"
    assert records[0].download_date == "2026-02-23"

def test_csv_normalizer_missing_column_skips_gracefully():
    # column_map references a column that doesn't exist in the CSV
    merchant = make_merchant(column_map={
        "Wine": "wine_name",
        "NonExistent": "region",
    })
    normalizer = CSVNormalizer()
    records = normalizer.normalize(FIXTURES / "sample_wines.csv", merchant, download_date="2026-02-23")
    assert len(records) == 3
    assert records[0].region == ""  # missing col defaults to empty

def test_xlsx_normalizer(tmp_path):
    # Create a simple xlsx fixture
    df = pd.DataFrame({
        "Wine": ["Latour", "Margaux"],
        "Vintage": ["2015", "2016"],
        "Price": [800.0, 600.0],
        "Currency": ["GBP", "GBP"],
    })
    xlsx_path = tmp_path / "wines.xlsx"
    df.to_excel(xlsx_path, index=False)

    merchant = make_merchant(column_map={
        "Wine": "wine_name",
        "Vintage": "vintage",
        "Price": "price",
        "Currency": "currency",
    })
    normalizer = XLSXNormalizer()
    records = normalizer.normalize(xlsx_path, merchant, download_date="2026-02-23")
    assert len(records) == 2
    assert records[0].wine_name == "Latour"

def test_pdf_normalizer_returns_empty_with_warning(tmp_path, caplog):
    import logging
    pdf_path = tmp_path / "price.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")
    merchant = make_merchant()
    normalizer = PDFNormalizer()
    with caplog.at_level(logging.WARNING):
        records = normalizer.normalize(pdf_path, merchant, download_date="2026-02-23")
    assert records == []
    assert "PDF normalization" in caplog.text

def test_registry_dispatches_by_format(tmp_path):
    df = pd.DataFrame({"Wine": ["Pétrus"], "Vintage": ["2019"]})
    csv_path = tmp_path / "test.csv"
    df.to_csv(csv_path, index=False)
    merchant = make_merchant(column_map={"Wine": "wine_name", "Vintage": "vintage"})
    registry = NormalizerRegistry()
    records = registry.normalize(csv_path, merchant, download_date="2026-02-23")
    assert len(records) == 1

def test_registry_unknown_extension_raises(tmp_path):
    from corkscrew.normalizer import NormalizationError
    unknown = tmp_path / "file.xyz"
    unknown.write_bytes(b"data")
    merchant = make_merchant()
    registry = NormalizerRegistry()
    with pytest.raises(NormalizationError):
        registry.normalize(unknown, merchant, download_date="2026-02-23")
```

**Step 3: Run to verify failures**

```bash
pytest tests/test_normalizer.py -v
```

**Step 4: Implement normalizer.py**

```python
# corkscrew/normalizer.py
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional
import chardet
import pandas as pd
from corkscrew.models import MerchantConfig, WineRecord

logger = logging.getLogger(__name__)


class NormalizationError(Exception):
    pass


class BaseNormalizer:
    def normalize(self, filepath: Path, merchant: MerchantConfig, download_date: str) -> list[WineRecord]:
        raise NotImplementedError

    def _map_row(self, row: dict, column_map: dict[str, str], merchant: MerchantConfig, download_date: str) -> WineRecord:
        kwargs: dict = {
            "merchant_id": merchant.id,
            "merchant_name": merchant.name,
            "wine_name": "",
            "source_url": merchant.preferred_download.url,
            "download_date": download_date,
        }
        for src_col, dest_field in column_map.items():
            val = row.get(src_col, "")
            if val is None or (isinstance(val, float) and pd.isna(val)):
                val = ""
            kwargs[dest_field] = str(val).strip()
        return WineRecord(**kwargs)


class CSVNormalizer(BaseNormalizer):
    def normalize(self, filepath: Path, merchant: MerchantConfig, download_date: str) -> list[WineRecord]:
        raw = filepath.read_bytes()
        detected = chardet.detect(raw)
        encoding = detected.get("encoding") or "utf-8"
        try:
            df = pd.read_csv(filepath, encoding=encoding, dtype=str)
        except Exception as e:
            raise NormalizationError(f"CSV read failed for {filepath}: {e}")
        df = df.fillna("")
        column_map = merchant.column_map or {}
        return [self._map_row(row, column_map, merchant, download_date) for _, row in df.iterrows()]


class XLSXNormalizer(BaseNormalizer):
    def normalize(self, filepath: Path, merchant: MerchantConfig, download_date: str) -> list[WineRecord]:
        try:
            engine = "xlrd" if filepath.suffix.lower() == ".xls" else "openpyxl"
            df = pd.read_excel(filepath, dtype=str, engine=engine)
        except Exception as e:
            raise NormalizationError(f"Excel read failed for {filepath}: {e}")
        df = df.fillna("")
        column_map = merchant.column_map or {}
        return [self._map_row(row, column_map, merchant, download_date) for _, row in df.iterrows()]


class JSONNormalizer(BaseNormalizer):
    def normalize(self, filepath: Path, merchant: MerchantConfig, download_date: str) -> list[WineRecord]:
        import json
        try:
            data = json.loads(filepath.read_text())
        except Exception as e:
            raise NormalizationError(f"JSON read failed: {e}")
        if isinstance(data, dict):
            # Try to find a list value
            for v in data.values():
                if isinstance(v, list):
                    data = v
                    break
        if not isinstance(data, list):
            raise NormalizationError("JSON does not contain a list of records")
        column_map = merchant.column_map or {}
        return [self._map_row(item, column_map, merchant, download_date) for item in data if isinstance(item, dict)]


class PDFNormalizer(BaseNormalizer):
    def normalize(self, filepath: Path, merchant: MerchantConfig, download_date: str) -> list[WineRecord]:
        logger.warning(
            "PDF normalization not implemented for %s (%s). "
            "File downloaded and hashed but not normalized.",
            merchant.id, filepath.name
        )
        return []


class NormalizerRegistry:
    FORMAT_MAP = {
        ".csv": CSVNormalizer,
        ".xlsx": XLSXNormalizer,
        ".xlsm": XLSXNormalizer,
        ".xls": XLSXNormalizer,
        ".json": JSONNormalizer,
        ".pdf": PDFNormalizer,
    }
    # merchant_id → normalizer class overrides
    MERCHANT_MAP: dict[str, type[BaseNormalizer]] = {}

    def normalize(self, filepath: Path, merchant: MerchantConfig, download_date: str) -> list[WineRecord]:
        if merchant.id in self.MERCHANT_MAP:
            return self.MERCHANT_MAP[merchant.id]().normalize(filepath, merchant, download_date)
        ext = filepath.suffix.lower()
        cls = self.FORMAT_MAP.get(ext)
        if cls is None:
            raise NormalizationError(f"No normalizer for extension '{ext}'")
        return cls().normalize(filepath, merchant, download_date)
```

**Step 5: Run tests to verify they pass**

```bash
pytest tests/test_normalizer.py -v
```

Expected: All 6 tests pass.

**Step 6: Commit**

```bash
git add corkscrew/normalizer.py tests/test_normalizer.py tests/fixtures/sample_wines.csv
git commit -m "feat: normalizer registry with CSV/XLSX/JSON/PDF dispatch"
```

---

### Task 8: Per-Merchant Normalizer Overrides

**Files:**
- Create: `corkscrew/normalizers/farr_vintners.py`
- Create: `corkscrew/normalizers/hub_wine.py`
- Create: `corkscrew/normalizers/google_sheets.py`
- Modify: `corkscrew/normalizers/__init__.py`
- Modify: `corkscrew/normalizer.py` (register overrides)

**Step 1: Implement Farr Vintners normalizer**

Farr Vintners CSV has these known columns (from PRD "gold standard"):

```python
# corkscrew/normalizers/farr_vintners.py
from corkscrew.normalizer import CSVNormalizer

class FarrVintnersNormalizer(CSVNormalizer):
    DEFAULT_COLUMN_MAP = {
        "Wine": "wine_name",
        "Vintage": "vintage",
        "Region": "region",
        "Appellation": "appellation",
        "Colour": "color",
        "Format": "format",
        "Price (ex VAT)": "price",
        "Currency": "currency",
        "Stock": "stock_quantity",
        "Case Size": "case_size",
        "Score": "score",
        "Scorer": "scorer",
        "Condition": "condition_notes",
    }

    def normalize(self, filepath, merchant, download_date):
        # Use config column_map if provided, otherwise fall back to default
        if not merchant.column_map:
            import copy
            patched = copy.copy(merchant)
            object.__setattr__(patched, "column_map", self.DEFAULT_COLUMN_MAP)
            return super().normalize(filepath, patched, download_date)
        return super().normalize(filepath, merchant, download_date)
```

**Step 2: Implement hub.wine shared normalizer**

```python
# corkscrew/normalizers/hub_wine.py
from corkscrew.normalizer import XLSXNormalizer

class HubWineNormalizer(XLSXNormalizer):
    DEFAULT_COLUMN_MAP = {
        "Wine Name": "wine_name",
        "Vintage": "vintage",
        "Region": "region",
        "Appellation": "appellation",
        "Colour": "color",
        "Format": "format",
        "Price": "price",
        "Currency": "currency",
        "Stock": "stock_quantity",
        "Case Size": "case_size",
    }

    def normalize(self, filepath, merchant, download_date):
        if not merchant.column_map:
            import copy
            patched = copy.copy(merchant)
            object.__setattr__(patched, "column_map", self.DEFAULT_COLUMN_MAP)
            return super().normalize(filepath, patched, download_date)
        return super().normalize(filepath, merchant, download_date)
```

**Step 3: Implement Google Sheets shared normalizer**

```python
# corkscrew/normalizers/google_sheets.py
from corkscrew.normalizer import CSVNormalizer

class GoogleSheetsNormalizer(CSVNormalizer):
    """Generic normalizer for Google Sheets exports.
    Column map must be provided in merchants.yaml for each sheet merchant.
    """
    pass  # Inherits all CSV behavior; column_map from config
```

**Step 4: Update normalizers/__init__.py and register overrides**

```python
# corkscrew/normalizers/__init__.py
from corkscrew.normalizers.farr_vintners import FarrVintnersNormalizer
from corkscrew.normalizers.hub_wine import HubWineNormalizer
from corkscrew.normalizers.google_sheets import GoogleSheetsNormalizer

# Map merchant_id → normalizer class
MERCHANT_NORMALIZER_MAP = {
    "farr-vintners": FarrVintnersNormalizer,
    # hub.wine merchants
    "sterling-fine-wines": HubWineNormalizer,
    "bibo-wine": HubWineNormalizer,
    "decorum-vintners": HubWineNormalizer,
    "falcon-vintners": HubWineNormalizer,
    "grand-vin-wm": HubWineNormalizer,
    # Google Sheets merchants
    "turville-valley-wines": GoogleSheetsNormalizer,
    "cave-de-chaz": GoogleSheetsNormalizer,
    "burgundy-cave": GoogleSheetsNormalizer,
}
```

**Step 5: Wire registry to use MERCHANT_NORMALIZER_MAP**

In `corkscrew/normalizer.py`, update `NormalizerRegistry`:
```python
# At bottom of normalizer.py, after imports:
def _load_merchant_map():
    try:
        from corkscrew.normalizers import MERCHANT_NORMALIZER_MAP
        return MERCHANT_NORMALIZER_MAP
    except ImportError:
        return {}

class NormalizerRegistry:
    FORMAT_MAP = { ... }  # unchanged

    @property
    def MERCHANT_MAP(self):
        return _load_merchant_map()

    def normalize(self, filepath, merchant, download_date):
        merchant_map = self.MERCHANT_MAP
        if merchant.id in merchant_map:
            return merchant_map[merchant.id]().normalize(filepath, merchant, download_date)
        # ... rest unchanged
```

**Step 6: Run all tests to ensure nothing broke**

```bash
pytest tests/ -v
```

Expected: All tests pass.

**Step 7: Commit**

```bash
git add corkscrew/normalizers/
git commit -m "feat: per-merchant normalizer overrides for farr, hub.wine, google sheets"
```

---

### Task 9: Full merchants.yaml

**Files:**
- Create: `merchants.yaml`

**Step 1: Create merchants.yaml with all ~40 V1 merchants**

This is a data entry task. Create `merchants.yaml` with all merchants from the PRD. The full file should contain:

- **Archetype 1 (hub.wine):** sterling-fine-wines, bibo-wine, decorum-vintners, falcon-vintners, grand-vin-wm
- **Archetype 2 (static):** private-cellar, richard-kihl, bibendum-wine, cuchet-co, farr-vintners, trinkreif, south-wine-co, de-vinis-illustribus, denis-perret, maison-jude, millesimes, la-cave-de-lill, sodivin, winemania, chateau-estate, vintage-grand-cru
- **Archetype 3 (google_sheets/google_drive):** turville-valley-wines, cave-de-chaz, burgundy-cave
- **Archetype 4 (static cloud):** goedhuis-co, ganpei-vintners
- **Archetype 5 (rest_endpoint):** orvinum-ag, hong-kong-wine-vault, cave-bb, lucullus, santa-rosa-fine-wine
- **Hardcoded edge cases:** albany-vintners, grw-wine-collection, great-ocean-industrial, 1870-vins-et-conseils, in-vino-veritas

Full YAML content (abbreviated example; populate all ~40 merchants following the schema in `docs/plans/2026-02-23-corkscrew-v1-design.md`):

```yaml
merchants:
  # ─── ARCHETYPE 1: hub.wine Extranet ─────────────────────────────────────
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
    hub_wine_slug: "bibo"
    auth: null
    notes: "hub.wine extranet pattern"

  - id: "sterling-fine-wines"
    name: "Sterling Fine Wines"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://sterlingfw.hub.wine/"
    downloads:
      - url: "https://extranet.hub.wine/xlsx/sterlingfw"
        format: "xlsx"
        preferred: true
        label: "hub.wine Excel export"
    url_pattern: "hub_wine"
    hub_wine_slug: "sterlingfw"
    auth: null

  - id: "decorum-vintners"
    name: "Decorum Vintners"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.decorumvintners.co.uk/"
    downloads:
      - url: "https://extranet.hub.wine/xlsx/decorum"
        format: "xlsx"
        preferred: true
    url_pattern: "hub_wine"
    hub_wine_slug: "decorum"

  - id: "falcon-vintners"
    name: "Falcon Vintners"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.falconvintners.com/"
    downloads:
      - url: "https://extranet.hub.wine/xlsx/falconvintners"
        format: "xlsx"
        preferred: true
    url_pattern: "hub_wine"
    hub_wine_slug: "falconvintners"

  - id: "grand-vin-wm"
    name: "Grand Vin WM"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.grandvinwinemerchants.com/"
    downloads:
      - url: "https://extranet.hub.wine/xlsx/grandvinwinemerchants"
        format: "xlsx"
        preferred: true
    url_pattern: "hub_wine"
    hub_wine_slug: "grandvinwinemerchants"

  # ─── ARCHETYPE 2: Static File Paths ──────────────────────────────────────
  - id: "farr-vintners"
    name: "Farr Vintners"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.farrvintners.com/downloads/"
    downloads:
      - url: "https://www.farrvintners.com/winelist_csv.php?output=csv"
        format: "csv"
        preferred: true
        label: "CSV full list"
      - url: "https://www.farrvintners.com/winelist_xlsx.php"
        format: "xlsx"
        preferred: false
        label: "Excel full list"
    url_pattern: "dynamic_php"
    auth: null
    notes: "Gold standard - multiple formats"

  - id: "richard-kihl"
    name: "Richard Kihl Ltd"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.richardkihl.ltd.uk/"
    downloads:
      - url: "https://www.richardkihl.ltd.uk/winelist/winelist.xls"
        format: "xls"
        preferred: true
    url_pattern: "static"

  - id: "bibendum-wine"
    name: "Bibendum Wine"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.bibendum-wine.co.uk/"
    downloads:
      - url: "https://bibendum-wine.co.uk/media/yfkchr4d/01022026-fine-wine-list.xlsx"
        format: "xlsx"
        preferred: true
    url_pattern: "static"
    notes: "URL may change on each upload — check periodically"

  - id: "cuchet-co"
    name: "Cuchet & Co"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://www.cuchet.co.uk/"
    downloads:
      - url: "https://cuchet.co.uk/excel/Cuchet%20and%20co%20Wine%20List.xlsx"
        format: "xlsx"
        preferred: true
    url_pattern: "static"

  - id: "private-cellar"
    name: "Private Cellar"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.privatecellar.co.uk/"
    downloads:
      - url: "https://www.privatecellar.co.uk/downloads/E-List%20Private%20Cellar.xlsm"
        format: "xlsm"
        preferred: true
        label: "Excel Macro list"
      - url: "https://www.privatecellar.co.uk/downloads/E-List%20Private%20Cellar.pdf"
        format: "pdf"
        preferred: false
    url_pattern: "static"

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
    notes: "URL contains current date; tries today then walks back up to 7 days"

  - id: "south-wine-co"
    name: "South Wine & Co"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://southwineandco.com/"
    downloads:
      - url: "https://southwineandco.com/media/files/tarif_global.xlsx"
        format: "xlsx"
        preferred: true
    url_pattern: "static"

  - id: "de-vinis-illustribus"
    name: "De Vinis Illustribus"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://www.devinis.fr/"
    downloads:
      - url: "https://devinis.fr/documents/catalogue/devinis_wine_list.pdf"
        format: "pdf"
        preferred: true
    url_pattern: "static"
    notes: "PDF only merchant"

  - id: "denis-perret"
    name: "Denis Perret"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://www.denisperret.fr/"
    downloads:
      - url: "https://www.denisperret.fr/en/index.php?controller=attachment&id_attachment=3760"
        format: "pdf"
        preferred: true
    url_pattern: "dynamic_php"
    notes: "PDF only"

  - id: "maison-jude"
    name: "Maison Jude"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://maisonjude.com/"
    downloads:
      - url: "https://maisonjude.com/wp-content/uploads/{YYYY}/{MM}/MAISON-JUDE-STOCK-EXC.-VAT-XLS.xlsx"
        format: "xlsx"
        preferred: true
        label: "Ex-VAT stock list"
    url_pattern: "dated"

  - id: "millesimes"
    name: "Millésimes"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://www.millesimes.com/"
    downloads:
      - url: "https://millesimes.com/tarif/pdf-ht.php"
        format: "pdf"
        preferred: true
    url_pattern: "dynamic_php"
    notes: "PDF only"

  - id: "la-cave-de-lill"
    name: "La Cave de l'ILL"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://www.lacavedelill.fr/"
    downloads:
      - url: "https://lacavedelill.fr/lacavedelill.xlsx"
        format: "xlsx"
        preferred: true
      - url: "https://lacavedelill.fr/lacavedelill.pdf"
        format: "pdf"
        preferred: false
    url_pattern: "static"

  - id: "sodivin"
    name: "SoDivin"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://www.sodivin.com/"
    downloads:
      - url: "https://sodivin.com/download/SoDivin_Tarif%20EN_Vintage.xlsx"
        format: "xlsx"
        preferred: true
        label: "By vintage"
      - url: "https://sodivin.com/download/SoDivin_Tarif%20EN_Chateau.xlsx"
        format: "xlsx"
        preferred: false
        label: "By chateau"
    url_pattern: "static"

  - id: "winemania"
    name: "WineMania"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://www.winemania.com/"
    downloads:
      - url: "https://winemania.com/tarifs/tarifs.xls"
        format: "xls"
        preferred: true
      - url: "https://winemania.com/tarifs/tarifs.pdf"
        format: "pdf"
        preferred: false
    url_pattern: "static"

  - id: "chateau-estate"
    name: "Château & Estate"
    country: "DE"
    tier: 1
    enabled: true
    discovery_url: "https://www.chateau-estate.de/"
    downloads:
      - url: "https://chateau-estate.de/prices/price.xls"
        format: "xls"
        preferred: true
    url_pattern: "static"

  - id: "vintage-grand-cru"
    name: "Vintage Grand Cru"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.vintagegrandcru.com/"
    downloads:
      - url: "https://vintagegrandcru.com/pricelist.xlsx"
        format: "xlsx"
        preferred: true
      - url: "https://vintagegrandcru.com/pricelist.pdf"
        format: "pdf"
        preferred: false
    url_pattern: "static"

  # ─── ARCHETYPE 3: Google Drive / Google Sheets ───────────────────────────
  - id: "turville-valley-wines"
    name: "Turville Valley Wines"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.turvillevalleywines.com/"
    downloads:
      - url: "https://drive.google.com/uc?export=download&id=1Cj6l6Rs4dKCKxcQGxI2hPViWDUYP6N9y"
        format: "xlsx"
        preferred: true
    url_pattern: "google_drive"
    google_drive_id: "1Cj6l6Rs4dKCKxcQGxI2hPViWDUYP6N9y"

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
    url_pattern: "google_sheets"
    google_sheet_id: "1kkDx3hJCjucG01FnvyzGXjRXbi60T6DlbEWJKSuML-E"

  - id: "burgundy-cave"
    name: "Burgundy Cave"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://burgundycave.com/"
    downloads:
      - url: "https://docs.google.com/spreadsheets/d/13gBLhRdhHQTA1GQ5SZGQZnk_eqUizkqm/export?format=xlsx"
        format: "xlsx"
        preferred: true
    url_pattern: "google_sheets"
    google_sheet_id: "13gBLhRdhHQTA1GQ5SZGQZnk_eqUizkqm"

  # ─── ARCHETYPE 4: Cloud-Hosted Static Exports ────────────────────────────
  - id: "goedhuis-co"
    name: "Goedhuis & Co"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.goedhuis.com/"
    downloads:
      - url: "https://dailystockfunction.blob.core.windows.net/fine-wine-list/GWL_FINE_WINE_LIST.xlsx"
        format: "xlsx"
        preferred: true
    url_pattern: "static"

  - id: "ganpei-vintners"
    name: "Ganpei Vintners"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.ganpeivintners.com/"
    downloads:
      - url: "https://cdn.shopify.com/s/files/1/0000/0000/files/GV_Catalog_{YYYYMMDD}.xlsx"
        format: "xlsx"
        preferred: true
    url_pattern: "dated"
    notes: "Date-stamped filename in YYYYMMDD format — see url_resolver special handling needed"

  # ─── ARCHETYPE 5: REST-Style Download Endpoints ──────────────────────────
  - id: "orvinum-ag"
    name: "Orvinum AG"
    country: "DE"
    tier: 1
    enabled: true
    discovery_url: "https://www.orvinum.com/"
    downloads:
      - url: "https://wine-rarities.auex.de/GetGerstlPDF.aspx?land=true&format=xlsx"
        format: "xlsx"
        preferred: true
    url_pattern: "rest_endpoint"

  - id: "hong-kong-wine-vault"
    name: "Hong Kong Wine Vault"
    country: "HK"
    tier: 1
    enabled: true
    discovery_url: "https://www.winevault.com.hk/"
    downloads:
      - url: "https://winevault.com.hk/site/WineVault_Wine_List.xls"
        format: "xls"
        preferred: true
    url_pattern: "static"

  - id: "cave-bb"
    name: "Cave BB"
    country: "CH"
    tier: 1
    enabled: true
    discovery_url: "https://www.cavebb.ch/"
    downloads:
      - url: "https://cavebb.ch/en/ExportPreisliste/Excel"
        format: "xlsx"
        preferred: true
        label: "Excel price list"
    url_pattern: "rest_endpoint"

  - id: "lucullus"
    name: "Lucullus"
    country: "CH"
    tier: 1
    enabled: true
    discovery_url: "https://www.lucullus.ch/"
    downloads:
      - url: "https://lucullus.ch/product-price-list/xls"
        format: "xls"
        preferred: true
    url_pattern: "rest_endpoint"

  - id: "santa-rosa-fine-wine"
    name: "Santa Rosa Fine Wine"
    country: "US"
    tier: 1
    enabled: true
    discovery_url: "https://www.santarosafinewine.com/"
    downloads:
      - url: "https://santarosafinewine.com/prodfeed.php"
        format: "csv"
        preferred: true
    url_pattern: "dynamic_php"

  # ─── EDGE CASES: Hardcoded Direct URLs ───────────────────────────────────
  - id: "in-vino-veritas"
    name: "In Vino Veritas Ltd"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.invinoveritas.co.uk/"
    downloads:
      - url: "https://www.invinoveritas.co.uk/download/wine_list.xlsx"
        format: "xlsx"
        preferred: true
        label: "HARDCODED - verify URL on next URL audit"
    url_pattern: "static"
    notes: "URL originally behind dated .htm page - manually researched direct URL"

  - id: "albany-vintners"
    name: "Albany Vintners"
    country: "UK"
    tier: 1
    enabled: true
    discovery_url: "https://www.albanyvintners.co.uk/"
    downloads:
      - url: "https://www.albanyvintners.co.uk/downloads/price_list.xlsx"
        format: "xlsx"
        preferred: true
        label: "HARDCODED - verify URL on next URL audit"
    url_pattern: "static"
    notes: "JS-rendered links - direct URL manually researched"

  - id: "grw-wine-collection"
    name: "GRW Wine Collection"
    country: "UK"
    tier: 1
    enabled: false
    discovery_url: "https://www.grwwine.com/pages/di"
    downloads:
      - url: "https://www.grwwine.com/pages/di"
        format: "xlsx"
        preferred: true
        label: "PLACEHOLDER - needs URL research"
    url_pattern: "static"
    notes: "Shopify page - direct download URL not yet confirmed; disabled pending verification"

  - id: "great-ocean-industrial"
    name: "Great Ocean Industrial"
    country: "AU"
    tier: 1
    enabled: false
    discovery_url: "https://www.greatocean.com.au/pages/our-full-wine-list"
    downloads:
      - url: "https://www.greatocean.com.au/pages/our-full-wine-list"
        format: "xlsx"
        preferred: true
        label: "PLACEHOLDER - needs URL research"
    url_pattern: "static"
    notes: "Shopify page - direct download URL not yet confirmed; disabled pending verification"

  - id: "1870-vins-et-conseils"
    name: "1870 Vins et Conseils"
    country: "FR"
    tier: 1
    enabled: true
    discovery_url: "https://www.1870.fr/"
    downloads:
      - url: "https://www.1870.fr/docs/liste_tarif.pdf"
        format: "pdf"
        preferred: true
        label: "HARDCODED - verify URL on next audit"
    url_pattern: "static"
    notes: "PDF links in header/footer nav - manually researched"
```

**Step 2: Validate the YAML loads correctly**

```bash
python -c "
from pathlib import Path
from corkscrew.config import load_config
merchants = load_config(Path('merchants.yaml'), enabled_only=True, tier=1)
print(f'Loaded {len(merchants)} enabled Tier-1 merchants')
for m in merchants:
    print(f'  {m.id}: {len(m.downloads)} download(s), pattern={m.url_pattern}')
"
```

Expected: prints 30+ merchants without errors.

**Step 3: Commit**

```bash
git add merchants.yaml
git commit -m "feat: full merchants.yaml with ~40 Tier-1 merchant configurations"
```

---

## Phase 3: CLI Integration

### Task 10: CLI — run command

**Files:**
- Modify: `corkscrew/cli.py`

**Step 1: Implement full CLI**

```python
# corkscrew/cli.py
from __future__ import annotations
import asyncio
import sys
from datetime import date, datetime, timezone
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from corkscrew.config import load_config, ConfigError
from corkscrew.downloader import Downloader
from corkscrew.normalizer import NormalizerRegistry, NormalizationError
from corkscrew.storage import StorageManager
import pandas as pd

console = Console()
DATA_ROOT = Path("data")
STATE_FILE = DATA_ROOT / "state.json"
DEFAULT_CONFIG = Path("merchants.yaml")


def get_config_path() -> Path:
    return DEFAULT_CONFIG


@click.group()
def cli():
    """Corkscrew — Wine Merchant Inventory Scraper"""
    pass


@cli.command()
@click.option("--merchant", default=None, help="Run a single merchant by ID")
@click.option("--tier", default=1, type=int, show_default=True, help="Run merchants of this tier")
@click.option("--dry-run", is_flag=True, help="Show what would be downloaded without downloading")
@click.option("--config", default=None, help="Path to merchants.yaml")
def run(merchant, tier, dry_run, config):
    """Download and normalize wine inventory from merchants."""
    config_path = Path(config) if config else get_config_path()
    try:
        merchants = load_config(config_path, enabled_only=True, tier=tier, merchant_id=merchant)
    except ConfigError as e:
        console.print(f"[red]Config error:[/red] {e}")
        sys.exit(2)

    if not merchants:
        console.print("[yellow]No merchants matched the filter criteria.[/yellow]")
        sys.exit(0)

    if dry_run:
        console.print(f"[bold]Dry run:[/bold] would download {len(merchants)} merchants")
        for m in merchants:
            dl = m.preferred_download
            console.print(f"  {m.id:40} {dl.format:6} {dl.url}")
        sys.exit(0)

    storage = StorageManager(STATE_FILE)
    downloader = Downloader(output_root=DATA_ROOT / "raw")
    registry = NormalizerRegistry()

    console.print(f"[bold]Starting run for {len(merchants)} merchants (10 concurrent)[/bold]")

    results = asyncio.run(downloader.download_all(merchants))

    failed = []
    normalized_count = 0
    total_wines = 0

    for result, merchant_cfg in zip(results, merchants):
        if not result.success:
            console.print(f"  [red]✗[/red] {merchant_cfg.id:40} {result.error}")
            storage.record_failure(merchant_cfg.id, result.error or "Unknown error")
            failed.append(merchant_cfg.id)
            continue

        changed = storage.is_changed(merchant_cfg.id, result.file_hash)
        storage.record_success(
            merchant_cfg.id,
            hash_val=result.file_hash,
            filepath=result.filepath,
            changed=changed,
        )

        change_label = "changed" if changed else "unchanged"
        size_kb = result.bytes_downloaded // 1024
        console.print(f"  [green]✓[/green] {merchant_cfg.id:40} {size_kb:6} KB  {change_label}")

        if changed:
            filepath = Path(result.filepath)
            today = date.today().isoformat()
            out_dir = DATA_ROOT / "normalized" / merchant_cfg.id
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{today}.csv"
            try:
                records = registry.normalize(filepath, merchant_cfg, download_date=today)
                if records:
                    pd.DataFrame([r.to_row() for r in records]).to_csv(out_path, index=False)
                    console.print(f"    [dim]→ {len(records)} wines normalized[/dim]")
                    total_wines += len(records)
                normalized_count += 1
            except NormalizationError as e:
                console.print(f"    [yellow]⚠ Normalization failed:[/yellow] {e}")

    console.print(f"\n[bold]Run complete:[/bold] {len(merchants)-len(failed)}/{len(merchants)} succeeded, "
                  f"{len(failed)} failed, {total_wines} wines normalized")

    sys.exit(1 if failed else 0)


@cli.command()
@click.option("--config", default=None, help="Path to merchants.yaml")
def status(config):
    """Show last run status for all merchants."""
    config_path = Path(config) if config else get_config_path()
    try:
        merchants = load_config(config_path)
    except ConfigError as e:
        console.print(f"[red]Config error:[/red] {e}")
        sys.exit(2)

    storage = StorageManager(STATE_FILE)

    table = Table(title="Corkscrew Status")
    table.add_column("Merchant", style="bold")
    table.add_column("Last Run")
    table.add_column("Status")
    table.add_column("Changed")
    table.add_column("Hash")
    table.add_column("Failures")

    ok = stale = failed_count = 0
    for m in merchants:
        state = storage.get_merchant_state(m.id)
        if state.last_run is None:
            last_run = "never"
            status_str = "[dim]PENDING[/dim]"
            changed_str = "-"
            hash_str = "-"
        else:
            last_run = _relative_time(state.last_run)
            failures = state.consecutive_failures
            if failures >= 7:
                status_str = "[red]CRITICAL[/red]"
                failed_count += 1
            elif failures >= 3:
                status_str = "[yellow]⚠ WARN[/yellow]"
                failed_count += 1
            elif failures > 0:
                status_str = f"[red]FAILED ({failures})[/red]"
                failed_count += 1
            elif not state.changed and len(state.history) > 5:
                status_str = "[yellow]STALE[/yellow]"
                stale += 1
            else:
                status_str = "[green]OK[/green]"
                ok += 1
            changed_str = "Yes" if state.changed else "No"
            hash_str = (state.last_hash or "")[:8]

        table.add_row(m.name, last_run, status_str, changed_str, hash_str, str(state.consecutive_failures))

    console.print(table)
    console.print(f"\n{len(merchants)} merchants | {ok} OK | {stale} stale | {failed_count} failed")


@cli.command(name="list")
@click.option("--config", default=None)
def list_merchants(config):
    """List all configured merchants."""
    config_path = Path(config) if config else get_config_path()
    try:
        merchants = load_config(config_path)
    except ConfigError as e:
        console.print(f"[red]Config error:[/red] {e}")
        sys.exit(2)

    table = Table(title="Configured Merchants")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Country")
    table.add_column("Tier")
    table.add_column("Enabled")
    table.add_column("Pattern")
    for m in merchants:
        table.add_row(m.id, m.name, m.country, str(m.tier), "✓" if m.enabled else "✗", m.url_pattern)
    console.print(table)


@cli.command()
@click.option("--output", default=None, help="Output path for master CSV")
def merge(output):
    """Merge all latest normalized CSVs into a master file."""
    out_path = Path(output) if output else DATA_ROOT / "master" / "master.csv"
    normalized_root = DATA_ROOT / "normalized"
    all_dfs = []
    for merchant_dir in sorted(normalized_root.iterdir()):
        if not merchant_dir.is_dir():
            continue
        csvs = sorted(merchant_dir.glob("*.csv"))
        if csvs:
            latest = csvs[-1]
            try:
                df = pd.read_csv(latest, dtype=str)
                all_dfs.append(df)
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not read {latest}: {e}")
    if not all_dfs:
        console.print("[yellow]No normalized files found.[/yellow]")
        sys.exit(0)
    master = pd.concat(all_dfs, ignore_index=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    master.to_csv(out_path, index=False)
    console.print(f"[green]✓[/green] Merged {len(all_dfs)} merchants → {out_path} ({len(master)} total records)")


def _relative_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        delta = datetime.now(timezone.utc) - dt
        if delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() // 60)}m ago"
        if delta.total_seconds() < 86400:
            return f"{int(delta.total_seconds() // 3600)}h ago"
        return f"{delta.days}d ago"
    except Exception:
        return iso_str[:10]
```

**Step 2: Test CLI commands**

```bash
corkscrew --help
corkscrew list
corkscrew status
corkscrew run --dry-run
```

Expected: All commands work without errors.

**Step 3: Commit**

```bash
git add corkscrew/cli.py
git commit -m "feat: full CLI with run, status, list, merge commands"
```

---

## Phase 4: Polish & Validation

### Task 11: README

**Files:**
- Create: `README.md`

Content:
```markdown
# Corkscrew

Wine Merchant Inventory Scraper Pipeline — V1

## Install

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

## Usage

corkscrew run                          # All enabled Tier-1 merchants
corkscrew run --merchant farr-vintners # Single merchant
corkscrew run --dry-run                # Preview without downloading
corkscrew status                       # Last run summary table
corkscrew list                         # All configured merchants
corkscrew merge                        # Build master CSV

## Exit Codes
0 = all merchants succeeded
1 = partial failures
2 = config error

## Adding a Merchant
Edit merchants.yaml following the schema in docs/plans/2026-02-23-corkscrew-v1-design.md.
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README with install and usage instructions"
```

---

### Task 12: Final Test Run and Validation

**Step 1: Run full test suite**

```bash
pytest tests/ -v --tb=short
```

Expected: All tests pass.

**Step 2: Dry run against all merchants**

```bash
corkscrew run --dry-run
```

Expected: Shows all ~30+ enabled merchants with their URLs.

**Step 3: Live test run against 3 well-known merchants**

```bash
corkscrew run --merchant farr-vintners
corkscrew run --merchant goedhuis-co
corkscrew run --merchant bibo-wine
```

Expected: Downloads succeed, normalized CSVs written to `data/normalized/`.

**Step 4: Check status output**

```bash
corkscrew status
```

**Step 5: Commit**

```bash
git add .
git commit -m "feat: corkscrew v1 complete — all tests passing"
```

---

## Summary

| Phase | Tasks | Status |
|---|---|---|
| 1: Foundation | 1–6 | Project, models, config, storage, URL resolver, downloader |
| 2: Normalizers | 7–9 | Normalizer dispatch, per-merchant overrides, full merchants.yaml |
| 3: CLI | 10 | Full CLI with run/status/list/merge |
| 4: Polish | 11–12 | README, validation |

**Parallel execution opportunity:** Tasks 5 (URL resolver), 4 (storage), and 3 (config) can be built in parallel after Task 2 (models). Tasks 7-9 (normalizers) can be built in parallel after Task 6 (downloader).
