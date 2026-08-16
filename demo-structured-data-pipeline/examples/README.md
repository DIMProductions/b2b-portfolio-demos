# サンプル事例

本リポジトリに同梱の実データ(`input/` → `output/`)から抜き出した、具体的なbefore/afterです。

## 正常系: 有効なレコードはそのまま通る

`input/sample_01.pdf`はPDFネイティブの入社フォームです:

```
Employee ID: 2001
Name: Kenji Ito
Email: kenji@example.com
Department: Sales
```

そのままJSON Schema検証をPASSし、`output/output.json`に出力されます:

```json
{
  "employee_id": 2001,
  "name": "Kenji Ito",
  "email": "kenji@example.com",
  "department": "Sales",
  "source": "sample_01.pdf"
}
```

## エラー系: スキーマ違反は推測せず拒否する

`input/bulk_import.xlsx`の5行目は、スキーマの`minLength: 2`より短い名前です:

```
employee_id=3003, name="X", email="x@example.com", department="Legal"
```

パイプラインは"X"を勝手に修正・削除する**ことはしません** — レコード全体を拒否し、`output/errors.csv` / `output/validation_report.json`に理由を正確に記録します:

```json
{
  "raw_data": {"employee_id": 3003, "name": "X", "email": "x@example.com", "department": "Legal"},
  "source": "bulk_import.xlsx",
  "error_type": "SchemaValidationError",
  "error_msg": "name: 'X' is too short"
}
```

## 重複系: ソースをまたいだ重複排除

`input/sample_03.pdf`と`input/bulk_import.xlsx`の1行目は、どちらも`employee_id: 3001`を示しています。先に処理されるPDF側のレコード(PDFがExcelより先に読み込まれるため)が残り、Excel側の重複は除外されて`output/validation_report.json`の`duplicates`に記録されます(サイレントな上書きや二重カウントはしません)。
