# OCR Validator — CCI Global

A production-ready OCR document validation module built on the Frappe framework.

---

## Architecture

```
ocr_validator/
├── api/
│   └── ocr_validate.py          ← All backend logic (OCR engine + rule evaluator + API endpoints)
├── fixtures/
│   └── ocr_compare.json         ← Seed data: 8 document configs across 4 types × 2 countries
├── ocr_validator/               ← Frappe module (canonical DocType definitions)
│   └── doctype/
│       ├── ocr_compare/         ← Master config DocType (rules live here)
│       ├── ocr_compare_must_have/ ← Child table: mandatory rules
│       ├── ocr_compare_or_rule/   ← Child table: OR-group rules
│       └── ocr_validation_log/  ← Audit log DocType
├── www/
│   └── ocr-validator.html       ← Full SaaS-style UI (standalone web page)
├── hooks.py
└── ocr_utils.py                 ← Re-export shim
```

---

## Setup

### 1. Install Python dependencies

```bash
# Inside your bench environment
pip install pytesseract Pillow pdf2image
# Install Tesseract binary (Ubuntu/Debian)
sudo apt-get install -y tesseract-ocr
# macOS
brew install tesseract
```

### 2. Install the app on your site

```bash
bench --site <your-site> install-app ocr_validator
```

### 3. Run migrations (creates the DocTypes)

```bash
bench --site <your-site> migrate
```

### 4. Load seed rule configs

```bash
bench --site <your-site> import-fixtures --app ocr_validator
```

### 5. Build assets and restart

```bash
bench build
bench restart
```

### 6. Open the validator

Navigate to: `https://<your-site>/ocr-validator`

Or from Frappe Desk: **Tools → Open Validator** on any OCR Compare record.

---

## Rule Engine

Rules live in **OCR Compare** DocType. Each record maps to one `document_type + country` combination.

### Must Have Rules (AND logic)
All rules must pass. Supports:

| Syntax | Behaviour |
|--------|-----------|
| `plain text` | Case-insensitive substring match in OCR text |
| `__REGEX__:<pattern>` | Python `re.search` with the given pattern |
| `__HAS_DATE__` | True if any date is found in the text |
| `__FUTURE_DATE__` | True if a future date exists (good for expiry checks) |
| `__RECENT_DATE__` | True if a date within the last 3 months exists (proof of address) |

### OR Rules (group logic)
Rows share a `Group Name`. At least one value in each group must match.  
Multiple groups are evaluated independently — all groups must have at least one match.

---

## Adding a New Document Type

1. Go to **OCR Compare** in Frappe Desk
2. Click **New**
3. Set `Document Type` (e.g. `Birth Certificate`) and `Country`
4. Add Must Have rules and OR groups
5. Enable the record
6. The new type appears automatically in the validator UI

No code changes required.

---

## Swapping the OCR Engine

The `run_ocr()` function in `api/ocr_validate.py` is the only place that calls Tesseract.  
Replace it with any provider (AWS Textract, Azure Document Intelligence, Google Vision):

```python
def run_ocr(file_path: str) -> str:
    # Drop in your engine here — just return a plain string
    import boto3
    client = boto3.client('textract')
    ...
    return extracted_text
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `ocr_validator.api.ocr_validate.validate_ocr_document` | POST | Main validation — returns full result |
| `ocr_validator.api.ocr_validate.get_ocr_configs` | POST | Returns all active configs grouped by doc type |
| `ocr_validator.api.ocr_validate.get_countries_for_doc_type` | POST | Returns countries for a given doc type |

All endpoints require a valid Frappe session (CSRF token).

---

## Validation Response Shape

```json
{
  "matched": true,
  "document_type": "Passport",
  "country": "Kenya",
  "matched_rules": ["passport", "kenya", "surname"],
  "missing_required": [],
  "failed_or_groups": [],
  "passed_or_groups": ["Name Label"],
  "ocr_text": "..full extracted text..",
  "ocr_preview": "..first 800 chars..",
  "rule_details": [
    {
      "rule": "passport",
      "description": "Document must identify as a passport",
      "type": "must_have",
      "passed": true
    },
    ...
  ],
  "config_used": "Passport-Kenya"
}
```
