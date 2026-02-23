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

def test_merchant_state_defaults():
    state = MerchantState()
    assert state.last_run is None
    assert state.last_success is None
    assert state.last_hash is None
    assert state.last_file is None
    assert state.changed is False
    assert state.consecutive_failures == 0
    assert state.history == []

def test_merchant_config_requires_at_least_one_download():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        MerchantConfig(
            id="test", name="Test", country="UK", tier=1, enabled=True,
            discovery_url="https://example.com",
            downloads=[],  # empty list should fail
            url_pattern="static",
        )
