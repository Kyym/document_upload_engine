"""
ocr_validator/api/bundle_portal.py
Handles portal data and document upload + OCR validation.
"""
import base64
import secrets
import frappe
from frappe import _


ALLOWED_EXTS = {
    "jpg", "jpeg", "jfif", "pjpeg", "pjp",
    "png", "gif", "webp", "bmp", "tiff", "tif",
    "pdf", "doc", "docx"
}


def _get_app(token):
    if not token:
        frappe.throw(_("No token provided."), frappe.PermissionError)
    app_name = frappe.db.get_value(
        "Candidate Application", {"submission_token": token}, "name"
    )
    if not app_name:
        frappe.throw(_("Invalid or expired link."), frappe.PermissionError)
    return frappe.get_doc("Candidate Application", app_name)


def _build_portal_context(app):
    bundle = frappe.get_doc("Document Bundle", app.document_bundle)
    submitted_map = {
        (r.document_type, r.country): r for r in app.submitted_documents
    }
    outstanding, submitted = [], []
    for item in bundle.document_items:
        key = (item.document_type, item.country)
        sub = submitted_map.get(key)
        entry = {
            "document_type": item.document_type,
            "country": item.country,
            "description": item.description or "",
            "is_required": bool(item.is_required),
        }
        if sub:
            # All attempted uploads go to the submitted table (pass, fail, skipped)
            submitted.append({**entry,
                "ocr_status": sub.ocr_status,
                "file_url": sub.file_url or "",
                "uploaded_at": str(sub.uploaded_at) if sub.uploaded_at else "",
                "ocr_result": sub.ocr_result or "",
            })
            # Failed docs also stay outstanding so user can retry
            if sub.ocr_status not in ("Passed", "Skipped"):
                entry["ocr_status"] = sub.ocr_status
                entry["ocr_result"] = sub.ocr_result or ""
                outstanding.append(entry)
        else:
            outstanding.append(entry)
    return {
        "application_name": app.name,
        "full_name": app.full_name,
        "bundle_name": bundle.bundle_name,
        "app_status": app.status,
        "outstanding": outstanding,
        "completed": submitted,
    }


@frappe.whitelist(allow_guest=True)
def get_portal_data(token=None):
    token = token or frappe.form_dict.get("token", "").strip()
    app = _get_app(token)
    return _build_portal_context(app)


@frappe.whitelist(allow_guest=True)
def generate_portal_token(application_name):
    token = secrets.token_urlsafe(32)
    frappe.db.set_value("Candidate Application", application_name, "submission_token", token)
    frappe.db.commit()
    base = frappe.utils.get_url()
    return {
        "token": token,
        "portal_url": f"{base}/document-upload?token={token}",
    }


@frappe.whitelist(allow_guest=True)
def upload_and_validate(token=None, document_type=None, country=None,
                        file_b64=None, file_ext=None, file_name=None):
    """
    Receive a base64-encoded file via POST JSON body, save it, run OCR, return result.
    Using POST avoids 414 URI Too Large errors from large base64 payloads in GET params.
    """
    # Frappe parses JSON body into frappe.local.form_dict automatically when
    # Content-Type is application/json. Fall back to direct kwargs if already set.
    fd = frappe.local.form_dict
    token         = token         or fd.get("token", "")
    document_type = document_type or fd.get("document_type", "")
    country       = country       or fd.get("country", "")
    file_b64      = file_b64      or fd.get("file_b64", "")
    file_ext      = file_ext      or fd.get("file_ext", "jpg")
    file_name     = file_name     or fd.get("file_name", "")

    # Strip data-URL prefix if present (e.g. "data:image/png;base64,...")
    if "," in file_b64:
        file_b64 = file_b64.split(",", 1)[1]

    # Normalise: strip whitespace, fix URL-safe base64, fix padding
    file_b64 = file_b64.strip().replace("-", "+").replace("_", "/")
    pad = len(file_b64) % 4
    if pad:
        file_b64 += "=" * (4 - pad)

    try:
        file_bytes = base64.b64decode(file_b64)
    except Exception as e:
        frappe.throw(_(f"File encoding error — {e}"))

    ext = (file_ext or "jpg").lower().lstrip(".")
    if ext == "jfif":
        ext = "jpg"
    if ext not in ALLOWED_EXTS:
        frappe.throw(_(f"File type '.{ext}' is not supported."))

    app = _get_app(token)

    # Save to Frappe file store
    safe_name = (file_name or f"{document_type}_{country}").replace(" ", "_")
    fname = f"{app.name}_{safe_name}_{secrets.token_hex(4)}.{ext}"

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": fname,
        "content": file_bytes,
        "is_private": 1,
        "attached_to_doctype": "Candidate Application",
        "attached_to_name": app.name,
    })
    file_doc.insert(ignore_permissions=True)
    file_url = file_doc.file_url

    # Run OCR — pass base64 + ext directly to validate_ocr_document
    try:
        from ocr_validator.api.ocr_validate import validate_ocr_document
        ocr_result = validate_ocr_document(
            document_type=document_type,
            country=country,
            file_b64=file_b64,
            file_ext=ext,
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "OCR bundle_portal error")
        ocr_result = {"matched": False, "error": str(e)}

    ocr_passed = bool(ocr_result.get("matched"))
    ocr_status = "Passed" if ocr_passed else "Failed"
    missing    = ocr_result.get("missing_required", [])

    def _fmt(m):
        if isinstance(m, dict):
            return m.get("description") or m.get("rule") or str(m)
        return str(m)

    ocr_summary = ocr_result.get("error") or (
        "All rules matched." if ocr_passed
        else "Missing: " + ", ".join(_fmt(m) for m in missing)
    )

    # Upsert child row on the application
    app.reload()
    existing = next(
        (r for r in app.submitted_documents
         if r.document_type == document_type and r.country == country),
        None
    )
    now = frappe.utils.now_datetime()
    if existing:
        existing.file_url    = file_url
        existing.ocr_status  = ocr_status
        existing.ocr_result  = ocr_summary
        existing.uploaded_at = now
    else:
        app.append("submitted_documents", {
            "document_type": document_type,
            "country":       country,
            "file_url":      file_url,
            "ocr_status":    ocr_status,
            "ocr_result":    ocr_summary,
            "uploaded_at":   now,
        })

    # Update application status
    bundle    = frappe.get_doc("Document Bundle", app.document_bundle)
    req_keys  = {
        (i.document_type, i.country)
        for i in bundle.document_items if i.is_required
    }
    passed_keys = {
        (r.document_type, r.country)
        for r in app.submitted_documents
        if r.ocr_status in ("Passed", "Skipped")
    }
    if ocr_passed:
        passed_keys.add((document_type, country))

    app.status = "Documents Complete" if req_keys and req_keys.issubset(passed_keys) else "Pending Documents"
    app.save(ignore_permissions=True)
    frappe.db.commit()

    result_dict = {
        "ocr_passed":       bool(ocr_passed),
        "ocr_status":       str(ocr_status),
        "ocr_result":       str(ocr_summary),
        "file_url":         str(file_url),
        "app_status":       str(app.status),
        "missing_required": [_fmt(m) for m in missing],
        "failed_or_groups": ocr_result.get("failed_or_groups", []),
    }
    frappe.response["message"] = result_dict
    return result_dict


@frappe.whitelist(allow_guest=True)
def remove_document(token=None, document_type=None, country=None):
    fd = frappe.local.form_dict
    token = token or fd.get("token", "")
    document_type = document_type or fd.get("document_type", "")
    country = country or fd.get("country", "")
    app = _get_app(token)
    app.reload()
    app.submitted_documents = [r for r in app.submitted_documents
                                if not (r.document_type == document_type and r.country == country)]
    app.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist(allow_guest=True)
def get_available_doc_types(token=None, country=None):
    """Return all enabled OCR Compare document types for the candidate's country."""
    fd = frappe.local.form_dict
    token   = token   or fd.get("token", "")
    country = country or fd.get("country", "")

    # If no country provided, get it from the application
    if not country and token:
        try:
            app = _get_app(token)
            bundle = frappe.get_doc("Document Bundle", app.document_bundle)
            countries = list({item.country for item in bundle.document_items if item.country})
            country = countries[0] if countries else ""
        except Exception:
            country = ""

    filters = {"enabled": 1}
    if country:
        filters["country"] = country

    records = frappe.get_all(
        "OCR Compare",
        filters=filters,
        fields=["document_type", "country"],
        order_by="document_type asc",
    )
    # Deduplicate
    seen = set()
    result = []
    for r in records:
        key = r.document_type + "||" + r.country
        if key not in seen:
            seen.add(key)
            result.append({"document_type": r.document_type, "country": r.country})
    return result
