# Structured Data Pipeline Demo (Deterministic)

This repository demonstrates a highly fault-tolerant, **deterministic** data parsing and validation pipeline. 
It ingests messy, unstructured business data (PDF onboarding forms, Excel bulk imports), enforces strict schema typing via `JSON Schema`, removes duplicate records, and safely isolates invalid rows.

> **Note:** This pipeline is strictly deterministic. It does **NOT** use AI/LLMs to guess missing values, perform semantic inference, or read scanned images (OCR). If data violates the schema, it is rejected and logged — never silently filled in. Running the same input twice always produces the same output.

## 5-Minute Overview: Data Flow

```text
PDF (3 files) / Excel (1 file)
        ↓
     Extract  (pdfplumber / openpyxl)
        ↓
    Normalize (whitespace trimming, type coercion)
        ↓
    Deduplicate (by employee_id)
        ↓
   JSON Schema Validation (input/schema.json)
        ↓
  ┌─────────────┐
  │             │
Valid        Invalid
  │             │
  ↓             ↓
JSON/CSV    errors.csv
              +
        validation_report.json
              (also lists removed duplicates)
```

## How to Run

1. Place input files in `input/`
2. Run the pipeline:
```bash
python src/run.py
```
3. Check `output/` for the separated valid data and error logs.

## Acceptance Criteria
See [docs/acceptance_criteria.md](docs/acceptance_criteria.md) for the mechanical definition of done.
