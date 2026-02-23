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
    mock_response.content = b"wine,vintage\nPetrus,2019\n" + b"x" * 200  # > 100 bytes

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
    assert result.bytes_downloaded == len(mock_response.content)


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
    # One GET only: size-check failure on a 200 must not trigger the retry loop.
    assert mock_client.get.call_count == 1


@pytest.mark.asyncio
async def test_download_all_runs_multiple(tmp_path):
    merchants = [make_merchant(url=f"https://example.com/file{i}.xlsx") for i in range(3)]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/octet-stream"}
    mock_response.content = b"wine data " * 20  # > 100 bytes

    with patch("corkscrew.downloader.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        downloader = Downloader(output_root=tmp_path)
        results = await downloader.download_all(merchants)

    assert len(results) == 3
    assert all(r.success for r in results)
