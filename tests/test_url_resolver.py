# tests/test_url_resolver.py
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
    # Day 6 back from Mar 2 = Feb 24 (index 6, 0-based)
    assert candidates[6] == "https://example.com/2026/02/file-24-02-2026.xlsx"

def test_generate_dated_candidates_returns_7():
    url = "https://x.com/{YYYY}-{MM}-{DD}.xlsx"
    candidates = generate_dated_candidates(url, reference_date=date(2026, 2, 23))
    assert len(candidates) == 7
    assert "https://x.com/2026-02-23.xlsx" in candidates
    assert "https://x.com/2026-02-17.xlsx" in candidates
