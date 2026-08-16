# Structured Data Pipeline Demo (Deterministic)

> **概要(日本語)**: PDF帳票・Excel一括データを受け取り、正規化・重複排除・JSON Schema検証を行い、正常データ(`output.json`/`output.csv`)とエラー・重複(`errors.csv`/`validation_report.json`)を機械的に分離するパイプラインです。AIによる曖昧な補完は一切行わず、スキーマに合わないデータは常にエラーとして検出されます。同じ入力からは常に同じ出力(bit単位で再現可能)。起動は `docker-compose up --build` のみ。

## 5分でわかるデータフロー

```text
PDF (3ファイル) / Excel (1ファイル)
        ↓
     抽出  (pdfplumber / openpyxl)
        ↓
    正規化 (空白除去・型変換)
        ↓
    重複排除 (employee_id単位)
        ↓
   JSON Schema検証 (input/schema.json)
        ↓
  ┌─────────────┐
  │             │
 正常         異常
  │             │
  ↓             ↓
JSON/CSV    errors.csv
              +
        validation_report.json
              (除外した重複も記録)
```

## 実行方法

1. `input/`に入力ファイルを配置
2. パイプラインを実行:
```bash
python src/run.py
```
3. `output/`で正常データとエラーログを確認

## 検収条件
[docs/acceptance_criteria.md](docs/acceptance_criteria.md)を参照(完了の機械的な定義)。

## 初回発注例

| 項目 | 内容 |
| :--- | :--- |
| **入力** | PDF/Excel 合計20ファイルまで + 出力JSON Schema |
| **納品** | JSON / CSV、変換スクリプト、`errors.csv`、`validation_report.json`、README |
| **納期** | 3営業日 |
| **検収** | 指定Schema PASS／不正データ全件隔離／同一入力→同一出力 |
| **本番DBアクセス** | 不要 |
