"""
pipeline/validate.py — Step 2: Validation
---------------------------------------------
Checks each extracted row against the required fields for its document
type before it's allowed into the report-generation step.
"""
from datetime import datetime

from .schemas import get_type


def validate_row(record: dict, doc_type: str) -> dict:
    schema = get_type(doc_type)
    errors = []

    for field in schema["required"]:
        if not str(record.get(field, "")).strip():
            errors.append(f"Missing required field: {schema['labels'].get(field, field)}")

    record["validation_status"] = "PASSED" if not errors else "FAILED"
    record["validation_errors"] = errors
    record["processed_at"] = datetime.now().isoformat() + "Z"
    return record


def validate_rows(rows: list, doc_type: str) -> list:
    return [validate_row(dict(row), doc_type) for row in rows]
