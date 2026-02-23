# corkscrew/downloader.py
"""Async HTTP downloader: fetches wine inventory files with retry and URL pattern routing."""
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
        last_status = 0
        for url in candidates:
            for attempt, delay in enumerate(RETRY_DELAYS + [None], 1):
                try:
                    result = await self._fetch(merchant, url, dl.format)
                    if result.success:
                        return result
                    if result.status_code == 404 and len(candidates) > 1:
                        last_status = result.status_code
                        last_error = result.error
                        break  # try next dated candidate
                    last_status = result.status_code
                    last_error = result.error
                    if delay is not None:
                        await asyncio.sleep(delay)
                except Exception as e:
                    last_error = str(e)
                    if delay is not None:
                        await asyncio.sleep(delay)

        return DownloadResult(
            merchant_id=merchant.id,
            status_code=last_status,
            bytes_downloaded=0,
            changed=False,
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
                merchant_id=merchant.id,
                status_code=resp.status_code,
                bytes_downloaded=0,
                changed=False,
                error=f"HTTP {resp.status_code}",
            )

        content = resp.content
        if len(content) < MIN_FILE_SIZE:
            return DownloadResult(
                merchant_id=merchant.id,
                status_code=200,
                bytes_downloaded=len(content),
                changed=False,
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
            changed=True,  # caller compares with state.json for real change detection
            status_code=200,
            bytes_downloaded=len(content),
        )

    async def download_all(self, merchants: list[MerchantConfig], ref_date: Optional[date] = None) -> list[DownloadResult]:
        tasks = [self.download(m, ref_date) for m in merchants]
        return await asyncio.gather(*tasks)
