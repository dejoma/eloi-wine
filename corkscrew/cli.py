# corkscrew/cli.py
from __future__ import annotations
import asyncio
import sys
from datetime import date, datetime, timezone
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from corkscrew.config import load_config, ConfigError
from corkscrew.downloader import Downloader
from corkscrew.normalizer import NormalizerRegistry, NormalizationError
from corkscrew.storage import StorageManager
import pandas as pd

console = Console()
DATA_ROOT = Path("data")
STATE_FILE = DATA_ROOT / "state.json"
DEFAULT_CONFIG = Path("merchants.yaml")


def get_config_path() -> Path:
    return DEFAULT_CONFIG


@click.group()
def cli():
    """Corkscrew — Wine Merchant Inventory Scraper"""
    pass


@cli.command()
@click.option("--merchant", default=None, help="Run a single merchant by ID")
@click.option("--tier", default=None, type=int, help="Run merchants of this tier (default: all tiers)")
@click.option("--dry-run", is_flag=True, help="Show what would be downloaded without downloading")
@click.option("--config", default=None, help="Path to merchants.yaml")
def run(merchant, tier, dry_run, config):
    """Download and normalize wine inventory from merchants."""
    config_path = Path(config) if config else get_config_path()
    try:
        merchants = load_config(config_path, enabled_only=True, tier=tier, merchant_id=merchant)
    except ConfigError as e:
        console.print(f"[red]Config error:[/red] {e}")
        sys.exit(2)

    if not merchants:
        console.print("[yellow]No merchants matched the filter criteria.[/yellow]")
        sys.exit(0)

    if dry_run:
        console.print(f"[bold]Dry run:[/bold] would download {len(merchants)} merchants")
        for m in merchants:
            dl = m.preferred_download
            console.print(f"  {m.id:40} {dl.format:6} {dl.url}")
        sys.exit(0)

    storage = StorageManager(STATE_FILE)
    downloader = Downloader(output_root=DATA_ROOT / "raw")
    registry = NormalizerRegistry()

    console.print(f"[bold]Starting run for {len(merchants)} merchants (10 concurrent)[/bold]")

    results = asyncio.run(downloader.download_all(merchants))

    failed = []
    normalized_count = 0
    total_wines = 0

    for result, merchant_cfg in zip(results, merchants):
        if not result.success:
            console.print(f"  [red]✗[/red] {merchant_cfg.id:40} {result.error}")
            storage.record_failure(merchant_cfg.id, result.error or "Unknown error")
            failed.append(merchant_cfg.id)
            continue

        changed = storage.is_changed(merchant_cfg.id, result.file_hash)
        storage.record_success(
            merchant_cfg.id,
            hash_val=result.file_hash,
            filepath=result.filepath,
            changed=changed,
        )

        change_label = "changed" if changed else "unchanged"
        size_kb = result.bytes_downloaded // 1024
        console.print(f"  [green]✓[/green] {merchant_cfg.id:40} {size_kb:6} KB  {change_label}")

        if changed:
            filepath = Path(result.filepath)
            today = date.today().isoformat()
            out_dir = DATA_ROOT / "normalized" / merchant_cfg.id
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{today}.csv"
            try:
                records = registry.normalize(filepath, merchant_cfg, download_date=today)
                if records:
                    pd.DataFrame([r.to_row() for r in records]).to_csv(out_path, index=False)
                    console.print(f"    [dim]→ {len(records)} wines normalized[/dim]")
                    total_wines += len(records)
                normalized_count += 1
            except NormalizationError as e:
                console.print(f"    [yellow]⚠ Normalization failed:[/yellow] {e}")

    console.print(f"\n[bold]Run complete:[/bold] {len(merchants)-len(failed)}/{len(merchants)} succeeded, "
                  f"{len(failed)} failed, {total_wines} wines normalized")

    sys.exit(1 if failed else 0)


@cli.command()
@click.option("--config", default=None, help="Path to merchants.yaml")
def status(config):
    """Show last run status for all merchants."""
    config_path = Path(config) if config else get_config_path()
    try:
        merchants = load_config(config_path)
    except ConfigError as e:
        console.print(f"[red]Config error:[/red] {e}")
        sys.exit(2)

    storage = StorageManager(STATE_FILE)

    table = Table(title="Corkscrew Status")
    table.add_column("Merchant", style="bold")
    table.add_column("Last Run")
    table.add_column("Status")
    table.add_column("Changed")
    table.add_column("Hash")
    table.add_column("Failures")

    ok = stale = failed_count = 0
    for m in merchants:
        state = storage.get_merchant_state(m.id)
        if state.last_run is None:
            last_run = "never"
            status_str = "[dim]PENDING[/dim]"
            changed_str = "-"
            hash_str = "-"
        else:
            last_run = _relative_time(state.last_run)
            failures = state.consecutive_failures
            if failures >= 7:
                status_str = "[red]CRITICAL[/red]"
                failed_count += 1
            elif failures >= 3:
                status_str = "[yellow]⚠ WARN[/yellow]"
                failed_count += 1
            elif failures > 0:
                status_str = "[red]FAILED[/red]"
                failed_count += 1
            elif not state.changed and len(state.history) > 5:
                status_str = "[yellow]STALE[/yellow]"
                stale += 1
            else:
                status_str = "[green]OK[/green]"
                ok += 1
            changed_str = "Yes" if state.changed else "No"
            hash_str = (state.last_hash or "")[:8]

        table.add_row(m.name, last_run, status_str, changed_str, hash_str, str(state.consecutive_failures))

    console.print(table)
    console.print(f"\n{len(merchants)} merchants | {ok} OK | {stale} stale | {failed_count} failed")


@cli.command(name="list")
@click.option("--config", default=None)
def list_merchants(config):
    """List all configured merchants."""
    config_path = Path(config) if config else get_config_path()
    try:
        merchants = load_config(config_path)
    except ConfigError as e:
        console.print(f"[red]Config error:[/red] {e}")
        sys.exit(2)

    table = Table(title="Configured Merchants")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Country")
    table.add_column("Tier")
    table.add_column("Enabled")
    table.add_column("Pattern")
    for m in merchants:
        table.add_row(m.id, m.name, m.country, str(m.tier), "✓" if m.enabled else "✗", m.url_pattern)
    console.print(table)


@cli.command()
@click.option("--output", default=None, help="Output path for master CSV")
def merge(output):
    """Merge all latest normalized CSVs into a master file."""
    out_path = Path(output) if output else DATA_ROOT / "master" / "master.csv"
    normalized_root = DATA_ROOT / "normalized"

    if not normalized_root.exists():
        console.print("[yellow]No normalized directory found. Run 'corkscrew run' first.[/yellow]")
        sys.exit(0)

    all_dfs = []
    for merchant_dir in sorted(normalized_root.iterdir()):
        if not merchant_dir.is_dir():
            continue
        csvs = sorted(merchant_dir.glob("*.csv"))
        if csvs:
            latest = csvs[-1]
            try:
                df = pd.read_csv(latest, dtype=str)
                all_dfs.append(df)
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not read {latest}: {e}")
    if not all_dfs:
        console.print("[yellow]No normalized files found.[/yellow]")
        sys.exit(0)
    master = pd.concat(all_dfs, ignore_index=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    master.to_csv(out_path, index=False)
    console.print(f"[green]✓[/green] Merged {len(all_dfs)} merchants → {out_path} ({len(master)} total records)")


def _relative_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        if delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() // 60)}m ago"
        if delta.total_seconds() < 86400:
            return f"{int(delta.total_seconds() // 3600)}h ago"
        return f"{delta.days}d ago"
    except Exception:
        return iso_str[:10]
