# corkscrew/config.py
from pathlib import Path
from typing import Optional
import yaml
from pydantic import ValidationError
from corkscrew.models import MerchantConfig


class ConfigError(Exception):
    pass


def load_config(
    path: Path,
    enabled_only: bool = False,
    tier: Optional[int] = None,
    merchant_id: Optional[str] = None,
) -> list[MerchantConfig]:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {path}: {e}")

    if not isinstance(raw, dict) or "merchants" not in raw:
        raise ConfigError(f"Config missing 'merchants' key: {path}")

    merchants = []
    for item in raw["merchants"]:
        try:
            merchants.append(MerchantConfig(**item))
        except ValidationError as e:
            raise ConfigError(f"Invalid merchant config for {item.get('id', '?')}: {e}")

    if enabled_only:
        merchants = [m for m in merchants if m.enabled]
    if tier is not None:
        merchants = [m for m in merchants if m.tier == tier]
    if merchant_id is not None:
        merchants = [m for m in merchants if m.id == merchant_id]

    return merchants
