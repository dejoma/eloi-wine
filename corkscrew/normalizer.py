# corkscrew/normalizer.py
"""Normalizer registry and per-format base normalizers for wine inventory data."""
from __future__ import annotations
import logging
from pathlib import Path
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
            str_val = str(val).strip()
            # Normalise decimal numeric strings: "4500.00" -> "4500.0", leave "2019" as "2019"
            if "." in str_val:
                try:
                    str_val = str(float(str_val))
                except (ValueError, TypeError):
                    pass
            kwargs[dest_field] = str_val
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

    @property
    def _merchant_map(self) -> dict[str, type[BaseNormalizer]]:
        try:
            from corkscrew.normalizers import MERCHANT_NORMALIZER_MAP
            return MERCHANT_NORMALIZER_MAP
        except ImportError:
            return {}

    def normalize(self, filepath: Path, merchant: MerchantConfig, download_date: str) -> list[WineRecord]:
        merchant_map = self._merchant_map
        if merchant.id in merchant_map:
            return merchant_map[merchant.id]().normalize(filepath, merchant, download_date)
        ext = filepath.suffix.lower()
        cls = self.FORMAT_MAP.get(ext)
        if cls is None:
            raise NormalizationError(f"No normalizer for extension '{ext}'")
        return cls().normalize(filepath, merchant, download_date)
