"""
ocr_validator/api/ocr_validate.py  (patched)

Fixes:
  - Returns a proper JSON-serialisable dict instead of raising on bad input,
    so the frontend always gets { matched, ... } and never hits "Cannot read
    properties of undefined (reading 'matched')".
  - Handles __HAS_DATE__ and __REGEX__:<pattern> special rule tokens.
  - Logs OCR text for debugging.
"""

import frappe
import base64
import re
import os
import tempfile
from frappe import _


# ─────────────────────────────────────────────────────────────────────────────
# OCR helpers
# ─────────────────────────────────────────────────────────────────────────────

def run_ocr(file_path: str) -> str:
    """Run Tesseract OCR on *file_path* and return extracted text (lower-cased)."""
    import pytesseract
    from PIL import Image

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        # Convert PDF pages to images first
        from pdf2image import convert_from_path
        pages = convert_from_path(file_path, dpi=200)
        texts = []
        for page in pages:
            texts.append(pytesseract.image_to_string(page))
        return "\n".join(texts).lower()
    else:
        return pytesseract.image_to_string(Image.open(file_path)).lower()


def _save_b64_to_temp(file_b64: str, file_ext: str) -> str:
    """Decode base64 content and write to a temp file. Returns the temp path."""
    # Strip data-URI prefix if present  (e.g. "data:image/png;base64,...")
    if "," in file_b64:
        file_b64 = file_b64.split(",", 1)[1]

    # Fix URL-safe base64 padding
    file_b64 = file_b64.replace("-", "+").replace("_", "/")
    padding = 4 - len(file_b64) % 4
    if padding != 4:
        file_b64 += "=" * padding

    file_bytes = base64.b64decode(file_b64)
    suffix = f".{file_ext.lstrip('.')}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        return tmp.name


# ─────────────────────────────────────────────────────────────────────────────
# Rule evaluation
# ─────────────────────────────────────────────────────────────────────────────

DATE_PATTERNS = [
    # DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
    r"\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b",
    # YYYY-MM-DD
    r"\b\d{4}-\d{2}-\d{2}\b",
    # Month DD YYYY  /  DD Month YYYY
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
    r"\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b",
]

def _rule_matches(rule: str, ocr_text: str) -> bool:
    """
    Evaluate a single must-have rule against *ocr_text* (already lower-cased).

    Special tokens:
      __HAS_DATE__          → true if any date pattern found
      __RECENT_DATE__       → true if a date within the last 3 months is found
      __REGEX__:<pattern>   → true if regex matches
    """
    rule = rule.strip()

    if rule.upper() == "__HAS_DATE__":
        return any(re.search(p, ocr_text) for p in DATE_PATTERNS)

    if rule.upper() == "__RECENT_DATE__":
        # Extract all dates from the text and check if any is within last 90 days
        import datetime
        today = datetime.date.today()
        cutoff = today - datetime.timedelta(days=90)

        for pattern in DATE_PATTERNS:
            for match in re.finditer(pattern, ocr_text):
                raw = match.group()
                parsed = _try_parse_date(raw)
                if parsed and cutoff <= parsed <= today:
                    return True
        return False

    if rule.upper().startswith("__REGEX__:"):
        pattern = rule[len("__REGEX__:"):]
        try:
            return bool(re.search(pattern, ocr_text, re.IGNORECASE))
        except re.error:
            frappe.log_error(f"Invalid regex in OCR rule: {pattern}", "OCR Validator")
            return False

    return rule.lower() in ocr_text


def _try_parse_date(raw: str):
    """Try to parse a raw date string into a datetime.date. Returns None if unparseable."""
    import datetime
    raw = raw.strip()
    fmts = [
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
        "%Y-%m-%d", "%Y/%m/%d",
        "%d %B %Y", "%d %b %Y",
        "%B %d %Y", "%b %d %Y",
        "%B %d, %Y", "%b %d, %Y",
    ]
    for fmt in fmts:
        try:
            return datetime.datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Main public API
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def validate_ocr_document(document_type, country, file_b64, file_ext):
    """
    Validate an uploaded document via OCR.

    Always returns a JSON-safe dict:
    {
        "matched": bool,
        "document_type": str,
        "country": str,
        "missing_required": [...],
        "matched_rules": [...],
        "failed_or_groups": [...],
        "error": str | null        ← populated only on unexpected errors
    }
    """
    result = {
        "matched": False,
        "document_type": document_type,
        "country": country,
        "missing_required": [],
        "matched_rules": [],
        "failed_or_groups": [],
        "error": None,
    }

    tmp_path = None
    try:
        # ── 1. Find OCR Compare configuration ────────────────────────
        ocr_compare_name = frappe.db.get_value(
            "OCR Compare",
            {"document_type": document_type, "country": country, "enabled": 1},
            "name",
        )

        if not ocr_compare_name:
            result["error"] = (
                f"No enabled OCR Compare rule found for "
                f"document_type='{document_type}', country='{country}'."
            )
            return result

        ocr_compare = frappe.get_doc("OCR Compare", ocr_compare_name)

        # ── 2. Save base64 to temp file & run OCR ────────────────────
        tmp_path = _save_b64_to_temp(file_b64, file_ext)
        ocr_text = run_ocr(tmp_path)
        frappe.logger().debug(f"OCR text for {document_type}/{country}:\n{ocr_text[:500]}")

        # ── 3. Check Must-Have rules ──────────────────────────────────
        missing_required = []
        matched_rules = []

        for row in ocr_compare.must_have_table:
            rule = row.rule_value          # actual field name in DocType
            if _rule_matches(rule, ocr_text):
                matched_rules.append(rule)
            else:
                missing_required.append({"rule": rule, "description": row.description or rule})

        result["missing_required"] = missing_required
        result["matched_rules"] = matched_rules

        # ── 4. Check OR rules ─────────────────────────────────────────
        failed_or_groups = []

        if ocr_compare.or_table:
            # Group rows by group_name
            groups = {}
            for row in ocr_compare.or_table:
                groups.setdefault(row.group_name, []).append(row.rule_value)  # actual field name

            for group_name, values in groups.items():
                if not any(_rule_matches(v, ocr_text) for v in values):
                    failed_or_groups.append(group_name)

        result["failed_or_groups"] = failed_or_groups

        # ── 5. Determine overall match ────────────────────────────────
        result["matched"] = (len(missing_required) == 0 and len(failed_or_groups) == 0)

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "OCR Validator Error")
        result["error"] = str(e)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    return result
