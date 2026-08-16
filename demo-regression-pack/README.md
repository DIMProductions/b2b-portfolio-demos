# Regression Pack Demo (YAML-driven Fixed Runner)

> **概要(日本語)**: `test_spec.yaml`にテスト仕様(ログイン・検索・フォーム送信・API疎通)を書くだけで、Playwrightによる自動E2Eテストが実行されます。結果は`junit.xml`・自己完結型HTMLレポート・失敗時のスクリーンショット/トレースとして出力され、GitHub Actions上でも同じ手順で再現されます。単体試験・結合試験工程の外注先として、そのまま検収可能な形で成果物が返ってくる想定です。起動は `docker-compose up --build` のみ。

This repository demonstrates a highly maintainable automated E2E test suite. 
Instead of writing fragile UI test code, human QA testers write strict YAML test specifications. 
Our fixed Python Runner consumes this YAML and reliably executes a fixed set of safe Playwright actions (goto/fill/click/expect_*), producing rich enterprise-grade reports.

## 5-Minute Overview: Data Flow

```text
YAML Test Spec (Excel/Spreadsheet Equivalent)
        ↓
    Validation (Pydantic Schema)
        ↓
   Fixed Runner (Playwright + Pytest)
        ↓
  ┌─────────────┐
  │             │
 PASS        FAIL (with Screenshot)
  │             │
  └──────┬──────┘
         ↓
  Enterprise Output
  - junit.xml
  - report.html (self-contained)
  - failure screenshots / traces
  - CI/CD pipeline integration
```

## Self-Contained Demo
This repository includes a tiny bundled Web App (`src/dummy_app.py`) so tests run locally without relying on external internet connectivity or volatile third-party websites.

## How to Run

1. Start the target app and run tests:
```bash
docker-compose up --build
```
2. Check `output/` for `junit.xml`, `report.html`, and failure screenshots.

## Acceptance Criteria
See [docs/acceptance_criteria.md](docs/acceptance_criteria.md) for the mechanical definition of done.

## Sample Work Order（初回発注例）

| 項目 | 内容 |
| :--- | :--- |
| **入力** | `test_spec.yaml`（テストケース10件程度まで）+ 対象URL（ステージング環境等） |
| **納品** | テストコード一式、`junit.xml`、`report.html`、失敗時スクリーンショット/トレース、README |
| **納期** | 3営業日 |
| **検収** | 記載した全テストケースが実行される／PASS・FAILが`junit.xml`に正しく反映される／失敗時に証跡（スクリーンショット・トレース）が残る |
| **本番DBアクセス** | 不要（対象URLへのHTTPアクセスのみ） |
