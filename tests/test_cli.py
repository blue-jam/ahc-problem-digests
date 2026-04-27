import argparse
from unittest.mock import MagicMock

import pytest

from ahc_problem_digests.cli import build_parser, run


def _make_args(command_or_id: str | None = None, target: str | None = None, force: bool = False, list_flag: bool = False) -> argparse.Namespace:
    return argparse.Namespace(command_or_id=command_or_id, target=target, force=force, list=list_flag)


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
        return_value=("Title 2", "問題文テキスト"),
    )
    mocker.patch(
        "ahc_problem_digests.cli.create_summary",
        return_value="新しい要約",
    )
    mock_save = mocker.patch("ahc_problem_digests.cli.save_digest")

    exit_code = run(_make_args("ahc002"))

    assert exit_code == 0
    mock_save.assert_called_once_with("ahc002", "Title 2", "新しい要約")
    captured = capsys.readouterr()
    assert "新しい要約" in captured.out


def test_run_force_regenerates_summary(mocker, capsys):
    """run with --force skips the existing digest check and regenerates."""
    mocker.patch("ahc_problem_digests.cli.load_dotenv")
    mocker.patch(
        "ahc_problem_digests.cli.fetch_problem_statement",
        return_value=("Title 3", "問題文"),
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
    mock_save.assert_called_once_with("ahc003", "Title 3", "再生成された要約")


def test_build_parser_defaults():
    """build_parser creates a parser with the expected defaults."""
    parser = build_parser()
    args = parser.parse_args(["ahc001"])

    assert args.command_or_id == "ahc001"
    assert args.force is False


def test_build_parser_force_flag():
    """build_parser supports the --force flag."""
    parser = build_parser()
    args = parser.parse_args(["ahc001", "--force"])

    assert args.force is True


def test_run_list(mocker, capsys):
    """run with --list prints all digests."""
    mocker.patch("ahc_problem_digests.cli.load_dotenv")
    
    mock_dir = mocker.MagicMock()
    mock_dir.exists.return_value = True
    
    from pathlib import Path
    mock_dir.glob.return_value = [Path("digests/ahc001.json"), Path("digests/ahc002.json")]
    
    mocker.patch("ahc_problem_digests.cli.DIGESTS_DIR", mock_dir)
    
    def mock_load_digest(cid, *args, **kwargs):
        if cid == "ahc001":
            return {"contest_id": "ahc001", "title": "Title 1", "summary": "Summary 1\nLine 2"}
        if cid == "ahc002":
            return {"contest_id": "ahc002", "title": "Title 2", "summary": "Summary 2"}
        return None
        
    mocker.patch("ahc_problem_digests.cli.load_digest", side_effect=mock_load_digest)
    
    exit_code = run(_make_args(list_flag=True))
    
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "AHC001 - Title 1 - Summary 1 Line 2" in captured.out
    assert "AHC002 - Title 2 - Summary 2" in captured.out

def test_run_no_args(mocker, capsys):
    """run without args and --list prints error."""
    mocker.patch("ahc_problem_digests.cli.load_dotenv")
    
    exit_code = run(_make_args())
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "エラー: コンテストIDを指定するか、--list" in captured.err
