# Examples

Concrete before/after cases pulled from this repo's own bundled fixtures (`input/` → `output/`).

## Normal case: valid record survives untouched

`input/sample_01.pdf` contains a PDF-native onboarding form:

```
Employee ID: 2001
Name: Kenji Ito
Email: kenji@example.com
Department: Sales
```

It passes JSON Schema validation as-is and appears in `output/output.json`:

```json
{
  "employee_id": 2001,
  "name": "Kenji Ito",
  "email": "kenji@example.com",
  "department": "Sales",
  "source": "sample_01.pdf"
}
```

## Error case: schema violation is rejected, not guessed

`input/bulk_import.xlsx` row 5 has a name shorter than the schema's `minLength: 2`:

```
employee_id=3003, name="X", email="x@example.com", department="Legal"
```

The pipeline does **not** attempt to fix or drop the "X" — it rejects the whole record and records exactly why in `output/errors.csv` / `output/validation_report.json`:

```json
{
  "raw_data": {"employee_id": 3003, "name": "X", "email": "x@example.com", "department": "Legal"},
  "source": "bulk_import.xlsx",
  "error_type": "SchemaValidationError",
  "error_msg": "name: 'X' is too short"
}
```

## Duplicate case: cross-source dedup

`input/sample_03.pdf` and row 1 of `input/bulk_import.xlsx` both describe `employee_id: 3001`. The PDF record (processed first, since PDFs are read before the Excel file) is kept; the Excel duplicate is removed and logged under `duplicates` in `output/validation_report.json` instead of silently overwriting or double-counting.
