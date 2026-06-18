"""
ocr_utils.py — re-export shim for ocr_validator.api.ocr_validate
Only exports functions that actually exist in ocr_validate.py.
"""
from ocr_validator.api.ocr_validate import (  # noqa: F401
    run_ocr,
    validate_ocr_document,
)
