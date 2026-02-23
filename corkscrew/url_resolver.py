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
        if "/export?" in url:
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
    raise ValueError(f"Cannot extract Google Drive ID from URL: {url}")
