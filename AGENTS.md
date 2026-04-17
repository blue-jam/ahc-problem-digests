# AGENTS.md

このドキュメントは、AIエージェントがこのリポジトリを扱う際の手順とルールをまとめたものです。

## リポジトリの概要

AtCoder Heuristic Contest (AHC) の問題文を Gemini API で日本語に要約し、JSON ファイルとして保存するツールです。

## ディレクトリ構成

```
.
├── src/
│   └── ahc_problem_digests/
│       ├── __init__.py
│       ├── cli.py        # コマンドラインエントリーポイント
│       ├── fetcher.py    # AtCoder から問題文を取得
│       ├── storage.py    # 要約の保存・読み込み
│       └── summarizer.py # Gemini API で要約生成
├── tests/
│   ├── test_cli.py
│   ├── test_fetcher.py
│   ├── test_storage.py
│   └── test_summarizer.py
├── digests/              # 生成された要約 JSON（git 管理対象外）
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
- `.env` は絶対にコミットしない。クレデンシャルは `.env.example` に記載する。
- `digests/` ディレクトリの JSON ファイルはコミットしてよい（要約の蓄積が目的）。
- パッケージの追加・削除には `uv add` / `uv remove` を使う。
