# tests/test_merchant_normalizers.py
import pandas as pd
import pytest
from pathlib import Path
from corkscrew.normalizer import NormalizerRegistry
from corkscrew.models import MerchantConfig, DownloadConfig


def make_merchant(merchant_id, url_pattern="static", column_map=None):
    return MerchantConfig(
        id=merchant_id, name=merchant_id, country="UK", tier=1, enabled=True,
        discovery_url="https://example.com",
        downloads=[DownloadConfig(url="https://example.com/f.csv", format="csv", preferred=True)],
        url_pattern=url_pattern,
        column_map=column_map,
    )


def test_farr_vintners_uses_default_column_map(tmp_path):
    # CSV with Farr Vintners column names
    df = pd.DataFrame({
        "Wine": ["Petrus"],
        "Vintage": ["2019"],
        "Price (ex VAT)": ["4500"],
        "Currency": ["GBP"],
        "Stock": ["6"],
    })
    csv_path = tmp_path / "farr.csv"
    df.to_csv(csv_path, index=False)

    merchant = make_merchant("farr-vintners")
    registry = NormalizerRegistry()
    records = registry.normalize(csv_path, merchant, download_date="2026-02-23")
    assert len(records) == 1
    assert records[0].wine_name == "Petrus"
    assert records[0].price == "4500"
    assert records[0].currency == "GBP"


def test_hub_wine_normalizer_dispatched(tmp_path):
    # XLSX with hub.wine column names
    df = pd.DataFrame({
        "Wine Name": ["Latour"],
        "Vintage": ["2015"],
        "Price": ["800"],
        "Currency": ["GBP"],
    })
    xlsx_path = tmp_path / "hub.xlsx"
    df.to_excel(xlsx_path, index=False)

    merchant = make_merchant("bibo-wine")
    registry = NormalizerRegistry()
    records = registry.normalize(xlsx_path, merchant, download_date="2026-02-23")
    assert len(records) == 1
    assert records[0].wine_name == "Latour"


def test_google_sheets_normalizer_dispatched(tmp_path):
    # CSV with merchant-provided column_map
    df = pd.DataFrame({"Vin": ["Petrus"], "Millesime": ["2019"]})
    csv_path = tmp_path / "sheets.csv"
    df.to_csv(csv_path, index=False)

    merchant = make_merchant("turville-valley-wines", column_map={"Vin": "wine_name", "Millesime": "vintage"})
    registry = NormalizerRegistry()
    records = registry.normalize(csv_path, merchant, download_date="2026-02-23")
    assert len(records) == 1
    assert records[0].wine_name == "Petrus"


def test_unknown_merchant_falls_back_to_format_dispatch(tmp_path):
    # A merchant not in MERCHANT_NORMALIZER_MAP gets format-based dispatch
    df = pd.DataFrame({"Wine": ["Margaux"]})
    csv_path = tmp_path / "unknown.csv"
    df.to_csv(csv_path, index=False)

    merchant = make_merchant("new-unknown-merchant", column_map={"Wine": "wine_name"})
    registry = NormalizerRegistry()
    records = registry.normalize(csv_path, merchant, download_date="2026-02-23")
    assert len(records) == 1
    assert records[0].wine_name == "Margaux"
