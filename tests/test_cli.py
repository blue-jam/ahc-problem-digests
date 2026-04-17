import argparse
from unittest.mock import MagicMock

import pytest

from ahc_problem_digests.cli import build_parser, run


def _make_args(contest_id: str, force: bool = False) -> argparse.Namespace:
    return argparse.Namespace(contest_id=contest_id, force=force)


def test_run_uses_existing_digest(mocker, tmp_path, capsys):
    """run prints the existing digest and returns 0 when --force is not set."""
    mocker.patch(
        "ahc_problem_digests.cli.load_digest",
        return_value={"contest_id": "ahc001", "summary": "既存の要約"},
    )
    mocker.patch("ahc_problem_digests.cli.load_dotenv")

    exit_code = run(_make_args("ahc001"))

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "既存の要約" in captured.out


def test_run_fetches_and_saves_when_no_existing_digest(mocker, capsys):
    """run fetches the problem, creates a summary, and saves it when no digest exists."""
    mocker.patch("ahc_problem_digests.cli.load_dotenv")
    mocker.patch("ahc_problem_digests.cli.load_digest", return_value=None)
    mocker.patch(
        "ahc_problem_digests.cli.fetch_problem_statement",
        return_value="問題文テキスト",
    )
    mocker.patch(
        "ahc_problem_digests.cli.create_summary",
        return_value="新しい要約",
    )
    mock_save = mocker.patch("ahc_problem_digests.cli.save_digest")

    exit_code = run(_make_args("ahc002"))

    assert exit_code == 0
    mock_save.assert_called_once_with("ahc002", "新しい要約")
    captured = capsys.readouterr()
    assert "新しい要約" in captured.out


def test_run_force_regenerates_summary(mocker, capsys):
    """run with --force skips the existing digest check and regenerates."""
    mocker.patch("ahc_problem_digests.cli.load_dotenv")
    mocker.patch(
        "ahc_problem_digests.cli.fetch_problem_statement",
        return_value="問題文",
    )
    mocker.patch(
        "ahc_problem_digests.cli.create_summary",
        return_value="再生成された要約",
    )
    mock_save = mocker.patch("ahc_problem_digests.cli.save_digest")
    mock_load = mocker.patch("ahc_problem_digests.cli.load_digest")

    exit_code = run(_make_args("ahc003", force=True))

    assert exit_code == 0
    mock_load.assert_not_called()
    mock_save.assert_called_once_with("ahc003", "再生成された要約")


def test_build_parser_defaults():
    """build_parser creates a parser with the expected defaults."""
    parser = build_parser()
    args = parser.parse_args(["ahc001"])

    assert args.contest_id == "ahc001"
    assert args.force is False


def test_build_parser_force_flag():
    """build_parser supports the --force flag."""
    parser = build_parser()
    args = parser.parse_args(["ahc001", "--force"])

    assert args.force is True
