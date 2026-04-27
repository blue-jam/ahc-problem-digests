# AGENTS.md

このドキュメントは、AIエージェントがこのリポジトリを扱う際の手順とルールをまとめたものです。

## リポジトリの概要

AtCoder Heuristic Contest (AHC) の問題文を Gemini API で日本語に要約し、JSON ファイルとして保存するツールです。
また、CSV形式の投票結果データを読み込み、GitHub Pages (Jekyll) 向けにMarkdownとして集計・出力する機能（`aggregate-votes`）も備えています。

## ディレクトリ構成

```
.
├── src/
│   └── ahc_problem_digests/
│       ├── __init__.py
│       ├── cli.py               # コマンドラインエントリーポイント
│       ├── fetcher.py           # AtCoder から問題文を取得
│       ├── storage.py           # 要約の保存・読み込み
│       ├── summarizer.py        # Gemini API で要約生成
│       └── vote_aggregator.py   # 投票結果の集計とMarkdown生成
├── tests/
│   ├── test_cli.py
│   ├── test_fetcher.py
│   ├── test_storage.py
│   ├── test_summarizer.py
│   └── test_vote_aggregator.py
├── digests/              # 生成された要約 JSON（git 管理対象外）
├── docs/                 # GitHub Pages 用の出力先ディレクトリ（Markdown 等）
├── votes/                # 投票結果の入力 CSV ファイル置き場
├── .env                  # クレデンシャル（git 管理対象外 — .env.example を参照）
├── .env.example          # .env のテンプレート
├── main.py               # `python main.py <contest_id>` で実行するエントリーポイント
├── pyproject.toml
└── uv.lock
```

## セットアップ

```bash
# 依存関係のインストール
uv sync

# .env の作成
cp .env.example .env
# .env を編集して GEMINI_API_KEY を設定する
```

## 使い方

```bash
# コンテスト ahc001 の問題文を取得して要約する
uv run ahc-digest ahc001

# 既存の要約を強制的に再生成する
uv run ahc-digest ahc001 --force

# 投票結果を集計し、Markdown を生成する（votes/ahc001-063.csv を入力とする）
uv run ahc-digest aggregate-votes ahc001-063

# または main.py 経由で実行する
uv run python main.py ahc001
```

## テスト

```bash
uv run pytest
```

## コード変更時のルール

- `fetcher.py` を変更する場合は `tests/test_fetcher.py` も更新する。
- `summarizer.py` を変更する場合は `tests/test_summarizer.py` も更新する。
- `storage.py` を変更する場合は `tests/test_storage.py` も更新する。
- `cli.py` を変更する場合は `tests/test_cli.py` も更新する。
- `vote_aggregator.py` を変更する場合は `tests/test_vote_aggregator.py` も更新する。
- `.env` は絶対にコミットしない。クレデンシャルは `.env.example` に記載する。
- `digests/` ディレクトリの JSON ファイルはコミットしてよい（要約の蓄積が目的）。
- `docs/` ディレクトリに生成された Markdown は GitHub Pages で公開するためにコミットする。
- パッケージの追加・削除には `uv add` / `uv remove` を使う。
