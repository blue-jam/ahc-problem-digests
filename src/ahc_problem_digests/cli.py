"""Command-line interface for ahc-problem-digests."""

import argparse
import sys

from dotenv import load_dotenv

from ahc_problem_digests.fetcher import fetch_problem_statement
from ahc_problem_digests.storage import load_digest, save_digest
from ahc_problem_digests.summarizer import create_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ahc-digest",
        description="AHC の問題文を Gemini API で要約して保存する",
    )
    parser.add_argument(
        "contest_id",
        help="コンテスト ID（例: ahc001）",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="既存の要約があっても再生成する",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    load_dotenv()

    contest_id: str = args.contest_id

    if not args.force:
        existing = load_digest(contest_id)
        if existing is not None:
            print(f"既存の要約が見つかりました（{contest_id}）:")
            print(existing["summary"])
            return 0

    print(f"問題文を取得しています ({contest_id})...")
    title, problem_text = fetch_problem_statement(contest_id)

    print("要約を生成しています...")
    summary = create_summary(problem_text)

    save_digest(contest_id, title, summary)
    print(f"要約を保存しました（digests/{contest_id}.json）:")
    print(summary)
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
