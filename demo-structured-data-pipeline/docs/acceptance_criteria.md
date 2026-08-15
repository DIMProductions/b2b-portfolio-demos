# Acceptance Criteria (検収条件)

This project is built for B2B subcontracting. The "Definition of Done" is strictly mechanical and verifiable without human subjectivity.

## PASS Conditions
1. **Schema Compliance**: The data in `output/output.json` MUST pass 100% validation against `input/schema.json`.
2. **Error Isolation**: Any record that fails validation MUST be written to `output/errors.csv` and `output/validation_report.json`. The main process MUST NOT crash.
3. **Duplicate Isolation**: Records sharing the same `employee_id` as an earlier record MUST be removed before validation and logged under `duplicates` in `output/validation_report.json`, not silently merged.
4. **Data Integrity**: `duplicates_removed + valid_count + error_count` MUST exactly equal `total_ingested` (the raw record count extracted from all PDF/Excel inputs).
5. **Idempotency**: Running `python src/run.py` multiple times on the same input MUST produce the exact same output bytes.
6. **Test Coverage**: Running `pytest tests/` MUST result in a 100% PASS rate.

## Out of Scope (除外事項)
* **OCR / Scanned Documents**: Only native text PDF/Excel files are supported (no scanned images).
* **AI Imputation**: Missing values are not guessed. They trigger a validation error.
* **Direct DB Insertion**: This module acts as a pure converter. Deployment to or direct mutation of production databases is not included.
