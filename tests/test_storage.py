import json
from pathlib import Path

import pytest

from ahc_problem_digests.storage import load_digest, save_digest


def test_save_digest_creates_file(tmp_path):
    """save_digest writes a JSON file in the given directory."""
    path = save_digest("ahc001", "A - Test", "これは要約です。", digests_dir=tmp_path)

    assert path.exists()
    assert path.name == "ahc001.json"


def test_save_digest_file_contents(tmp_path):
    """save_digest stores contest_id and summary in the JSON file."""
    save_digest("ahc001", "Title A", "要約テキスト", digests_dir=tmp_path)

    data = json.loads((tmp_path / "ahc001.json").read_text(encoding="utf-8"))
    assert data["contest_id"] == "ahc001"
    assert data["title"] == "Title A"
    assert data["summary"] == "要約テキスト"


def test_save_digest_creates_directory_if_missing(tmp_path):
    """save_digest creates the digests directory when it does not exist."""
    nested = tmp_path / "nested" / "digests"
    save_digest("ahc002", "T", "要約", digests_dir=nested)

    assert nested.is_dir()
    assert (nested / "ahc002.json").exists()


def test_load_digest_returns_data(tmp_path):
    """load_digest returns the saved dictionary."""
    save_digest("ahc003", "Title 3", "要約", digests_dir=tmp_path)

    data = load_digest("ahc003", digests_dir=tmp_path)

    assert data is not None
    assert data["contest_id"] == "ahc003"
    assert data["title"] == "Title 3"
    assert data["summary"] == "要約"


def test_load_digest_returns_none_when_missing(tmp_path):
    """load_digest returns None when no file exists for the contest."""
    result = load_digest("ahc999", digests_dir=tmp_path)

    assert result is None


def test_save_and_load_roundtrip(tmp_path):
    """A summary saved by save_digest can be retrieved by load_digest."""
    summary = "日本語の要約テキスト。複数行。\n2行目。"
    save_digest("ahc010", "T10", summary, digests_dir=tmp_path)

    loaded = load_digest("ahc010", digests_dir=tmp_path)

    assert loaded is not None
    assert loaded["title"] == "T10"
    assert loaded["summary"] == "日本語の要約テキスト。複数行。\n2行目。"
