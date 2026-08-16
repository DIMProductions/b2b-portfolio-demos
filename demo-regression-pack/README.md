# Regression Pack Demo (YAML-driven Fixed Runner)

> **概要(日本語)**: `test_spec.yaml`にテスト仕様(ログイン・検索・フォーム送信・API疎通)を書くだけで、Playwrightによる自動E2Eテストが実行されます。結果は`junit.xml`・自己完結型HTMLレポート・失敗時のスクリーンショット/トレースとして出力され、GitHub Actions上でも同じ手順で再現されます。単体試験・結合試験工程の外注先として、そのまま検収可能な形で成果物が返ってくる想定です。起動は `docker-compose up --build` のみ。

## 5分でわかるデータフロー

```text
YAMLテスト仕様 (Excel/スプレッドシート相当)
        ↓
    バリデーション (Pydanticスキーマ)
        ↓
   Fixed Runner (Playwright + Pytest)
        ↓
  ┌─────────────┐
  │             │
 PASS        FAIL (スクリーンショット付き)
  │             │
  └──────┬──────┘
         ↓
  エンタープライズ出力
  - junit.xml
  - report.html (自己完結型)
  - 失敗時スクリーンショット / トレース
  - CI/CDパイプライン連携
```

## 自己完結型デモ
外部のインターネット接続や不安定な第三者サイトに依存せず動作するよう、小さなWebアプリ(`src/dummy_app.py`)を同梱しています。

## 実行方法

1. 対象アプリを起動し、テストを実行:
```bash
docker-compose up --build
```
2. `output/`で`junit.xml`・`report.html`・失敗時スクリーンショットを確認

## 検収条件
[docs/acceptance_criteria.md](docs/acceptance_criteria.md)を参照(完了の機械的な定義)。

## 初回発注例

| 項目 | 内容 |
| :--- | :--- |
| **入力** | `test_spec.yaml`（テストケース10件程度まで）+ 対象URL（ステージング環境等） |
| **納品** | テストコード一式、`junit.xml`、`report.html`、失敗時スクリーンショット/トレース、README |
| **納期** | 3営業日 |
| **検収** | 記載した全テストケースが実行される／PASS・FAILが`junit.xml`に正しく反映される／失敗時に証跡（スクリーンショット・トレース）が残る |
| **本番DBアクセス** | 不要（対象URLへのHTTPアクセスのみ） |
