# ahc-problem-digests

AtCoder Heuristic Contest (AHC) の問題文を Gemini API で日本語に要約して保存するツール。

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

# 保存されている要約の一覧を表示する
uv run ahc-digest --list
```

要約は `digests/<contest_id>.json` に保存されます。

## テスト

```bash
uv run pytest
```
