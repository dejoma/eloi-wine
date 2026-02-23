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
