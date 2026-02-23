# tests/test_storage.py
import json
import pytest
from pathlib import Path
from corkscrew.storage import compute_hash, StorageManager

def test_compute_hash_is_deterministic(tmp_path):
    f = tmp_path / "test.csv"
    f.write_bytes(b"wine,vintage\nPetrus,2019")
    h1 = compute_hash(f)
    h2 = compute_hash(f)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex

def test_compute_hash_differs_for_different_content(tmp_path):
    f1 = tmp_path / "a.csv"
    f2 = tmp_path / "b.csv"
    f1.write_bytes(b"content A")
    f2.write_bytes(b"content B")
    assert compute_hash(f1) != compute_hash(f2)

def test_storage_manager_initial_state(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    state = sm.get_merchant_state("farr-vintners")
    assert state.last_hash is None
    assert state.consecutive_failures == 0

def test_storage_manager_record_success(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    sm.record_success("farr-vintners", hash_val="abc123", filepath="data/raw/farr/x.csv", changed=True)
    state = sm.get_merchant_state("farr-vintners")
    assert state.last_hash == "abc123"
    assert state.consecutive_failures == 0
    assert state.changed is True

def test_storage_manager_record_failure_increments_counter(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    sm.record_failure("test-merchant", error="HTTP 503")
    sm.record_failure("test-merchant", error="HTTP 503")
    state = sm.get_merchant_state("test-merchant")
    assert state.consecutive_failures == 2

def test_storage_manager_success_resets_failure_counter(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    sm.record_failure("test-merchant", error="HTTP 503")
    sm.record_failure("test-merchant", error="HTTP 503")
    sm.record_success("test-merchant", hash_val="x", filepath="x", changed=True)
    state = sm.get_merchant_state("test-merchant")
    assert state.consecutive_failures == 0

def test_storage_manager_detects_unchanged(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    sm.record_success("test", hash_val="abc", filepath="x.csv", changed=True)
    is_changed = sm.is_changed("test", "abc")
    assert is_changed is False

def test_storage_manager_detects_changed(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    sm.record_success("test", hash_val="abc", filepath="x.csv", changed=True)
    is_changed = sm.is_changed("test", "xyz")
    assert is_changed is True

def test_storage_manager_history_capped_at_30(tmp_path):
    sm = StorageManager(tmp_path / "state.json")
    for i in range(35):
        sm.record_success("test", hash_val=f"hash{i}", filepath="x", changed=True)
    state = sm.get_merchant_state("test")
    assert len(state.history) <= 30

def test_storage_manager_persists_across_instances(tmp_path):
    state_file = tmp_path / "state.json"
    sm1 = StorageManager(state_file)
    sm1.record_success("test", hash_val="abc123", filepath="x.csv", changed=True)
    sm2 = StorageManager(state_file)
    state = sm2.get_merchant_state("test")
    assert state.last_hash == "abc123"
