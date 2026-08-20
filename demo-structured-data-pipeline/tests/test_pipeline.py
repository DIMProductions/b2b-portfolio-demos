import json
from pathlib import Path

import jsonschema
import pytest

from src.run import coerce_employee_id, dedupe, process_pipeline

SCHEMA = json.loads(Path("input/schema.json").read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft7Validator(SCHEMA)


def test_coerce_employee_id_casts_numeric_string():
    record = coerce_employee_id({"employee_id": "1001"})
    assert record["employee_id"] == 1001


def test_coerce_employee_id_leaves_non_numeric_string():
    record = coerce_employee_id({"employee_id": "abc"})
    assert record["employee_id"] == "abc"


def test_dedupe_removes_repeated_employee_id():
    records = [
        {"employee_id": 1, "_source": "a.pdf"},
        {"employee_id": 1, "_source": "b.xlsx"},
        {"employee_id": 2, "_source": "b.xlsx"},
    ]
    deduped, duplicates = dedupe(records)
    assert [r["employee_id"] for r in deduped] == [1, 2]
    assert len(duplicates) == 1
    assert duplicates[0]["duplicate_of_source"] == "a.pdf"


def test_schema_accepts_valid_record():
    record = {"employee_id": 1, "name": "Taro", "email": "test@example.com", "department": "IT"}
    assert list(VALIDATOR.iter_errors(record)) == []


def test_schema_rejects_short_name():
    record = {"employee_id": 1, "name": "T", "email": "test@example.com", "department": "IT"}
    assert list(VALIDATOR.iter_errors(record))


def test_schema_rejects_malformed_email():
    record = {"employee_id": 1, "name": "Taro", "email": "not-an-email", "department": "IT"}
    assert list(VALIDATOR.iter_errors(record))


def test_schema_rejects_non_integer_employee_id():
    record = {"employee_id": "N/A", "name": "Taro", "email": "test@example.com", "department": "IT"}
    assert list(VALIDATOR.iter_errors(record))


def test_end_to_end_pipeline_on_bundled_fixtures():
    """Runs the real pipeline against input/ (3 PDFs + 1 Excel) and checks the
    exact counts the fixture data was designed to produce."""
    process_pipeline()

    report = json.loads(Path("output/validation_report.json").read_text(encoding="utf-8"))
    assert report["total_ingested"] == 9
    assert report["duplicates_removed"] == 2
    assert report["processed"] == 7
    assert report["valid_count"] == 3
    assert report["error_count"] == 4

    valid = json.loads(Path("output/output.json").read_text(encoding="utf-8"))
    assert {r["employee_id"] for r in valid} == {2001, 3001, 3002}


def test_corrupt_file_is_isolated_not_crashed():
    """A future bug or a genuinely malformed input file must not crash the
    whole batch — it gets isolated the same way a bad record does."""
    bad_pdf = Path("input/_corrupt_test.pdf")
    bad_pdf.write_bytes(b"not a real pdf \x00\x01\x02")
    try:
        process_pipeline()  # must not raise
        report = json.loads(Path("output/validation_report.json").read_text(encoding="utf-8"))
        assert any(fe["source"] == "_corrupt_test.pdf" for fe in report["file_errors"])
    finally:
        bad_pdf.unlink()
        process_pipeline()  # restore output/ to match the real fixtures only
