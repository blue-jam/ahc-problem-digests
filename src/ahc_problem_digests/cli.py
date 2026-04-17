"""Command-line interface for ahc-problem-digests."""

import argparse
import sys

from dotenv import load_dotenv

from ahc_problem_digests.fetcher import fetch_problem_statement
from ahc_problem_digests.storage import DIGESTS_DIR, load_digest, save_digest
from ahc_problem_digests.summarizer import create_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ahc-digest",
        description="AHC の問題文を Gemini API で要約して保存する",
    )
    parser.add_argument(
        "contest_id",
        nargs="?",
        help="コンテスト ID（例: ahc001）。--list 指定時は省略可",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="既存の要約があっても再生成する",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="保存されている要約の一覧を表示する",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    load_dotenv()

    if args.list:
        if not DIGESTS_DIR.exists():
            print("保存されている要約はありません。")
            return 0
        for path in sorted(DIGESTS_DIR.glob("*.json")):
            contest_id = path.stem
            digest = load_digest(contest_id)
            if digest:
                title = digest.get("title", "")
                summary = digest.get("summary", "").replace("\n", " ")
                print(f"{contest_id.upper()} - {title} - {summary}")
        return 0

    if not args.contest_id:
        print("エラー: コンテストIDを指定するか、--list オプションを使用してください。", file=sys.stderr)
        return 1

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
