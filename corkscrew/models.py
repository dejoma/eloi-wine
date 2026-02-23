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
