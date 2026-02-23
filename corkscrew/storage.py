# corkscrew/storage.py
import hashlib
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from corkscrew.models import MerchantState

logger = logging.getLogger(__name__)

HISTORY_LIMIT = 30


def compute_hash(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


class StorageManager:
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self._data: dict = self._load()

    def _load(self) -> dict:
        if not self.state_path.exists():
            return {}
        try:
            return json.loads(self.state_path.read_text())
        except json.JSONDecodeError as e:
            backup = self.state_path.with_suffix(".json.bak")
            shutil.copy2(self.state_path, backup)
            logger.warning(
                "state.json is corrupted (%s). Starting with empty state. "
                "Corrupted file backed up to %s",
                e, backup,
            )
            return {}

    def _save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self._data, indent=2))

    def get_merchant_state(self, merchant_id: str) -> MerchantState:
        return MerchantState(**self._data.get(merchant_id, {}))

    def is_changed(self, merchant_id: str, new_hash: str) -> bool:
        state = self.get_merchant_state(merchant_id)
        return state.last_hash != new_hash

    def record_success(self, merchant_id: str, hash_val: str, filepath: str, changed: bool):
        now = datetime.now(timezone.utc).isoformat()
        existing = self._data.get(merchant_id, {})
        history = list(existing.get("history", []))
        history.append({"date": now[:10], "hash": hash_val, "status": "success", "changed": changed})
        if len(history) > HISTORY_LIMIT:
            history = history[-HISTORY_LIMIT:]
        self._data[merchant_id] = {
            "last_run": now,
            "last_success": now,
            "last_hash": hash_val,
            "last_file": filepath,
            "changed": changed,
            "consecutive_failures": 0,
            "history": history,
        }
        self._save()

    def record_failure(self, merchant_id: str, error: str):
        now = datetime.now(timezone.utc).isoformat()
        existing = self._data.get(merchant_id, {})
        history = list(existing.get("history", []))
        history.append({"date": now[:10], "hash": None, "status": "failed", "changed": False, "error": error})
        if len(history) > HISTORY_LIMIT:
            history = history[-HISTORY_LIMIT:]
        failures = existing.get("consecutive_failures", 0) + 1
        self._data[merchant_id] = {
            **existing,
            "last_run": now,
            "consecutive_failures": failures,
            "history": history,
        }
        self._save()
