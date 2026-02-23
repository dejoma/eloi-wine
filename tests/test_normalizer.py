# tests/test_normalizer.py
import pytest
import pandas as pd
from pathlib import Path
from datetime import date
from corkscrew.normalizer import NormalizerRegistry, CSVNormalizer, XLSXNormalizer, PDFNormalizer, NormalizationError
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
    unknown = tmp_path / "file.xyz"
    unknown.write_bytes(b"data")
    merchant = make_merchant()
    registry = NormalizerRegistry()
    with pytest.raises(NormalizationError):
        registry.normalize(unknown, merchant, download_date="2026-02-23")
