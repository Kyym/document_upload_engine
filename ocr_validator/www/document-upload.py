"""
ocr_validator/www/document-upload.py

Frappe web page controller for the Candidate Document Upload Portal.
URL: /document-upload?token=<submission_token>

Sets context variables consumed by document-upload.html.
"""

import frappe
from frappe import _

no_cache = 1


def get_context(context):
    token = frappe.form_dict.get("token", "").strip()

    if not token:
        frappe.throw(_("No token provided. Please use the link sent to you."), frappe.PermissionError)

    app_name = frappe.db.get_value(
        "Candidate Application", {"submission_token": token}, "name"
    )
    if not app_name:
        frappe.throw(_("Invalid or expired link."), frappe.PermissionError)

    app = frappe.get_doc("Candidate Application", app_name)
    bundle = frappe.get_doc("Document Bundle", app.document_bundle)

    # Build submitted lookup  { (document_type, country): row }
    submitted_map = {}
    for row in app.submitted_documents:
        submitted_map[(row.document_type, row.country)] = row

    outstanding = []
    completed = []

    for item in bundle.document_items:
        key = (item.document_type, item.country)
        sub = submitted_map.get(key)

        entry = {
            "document_type": item.document_type,
            "country": item.country,
            "description": item.description or "",
            "is_required": bool(item.is_required),
        }

        if sub and sub.ocr_status in ("Passed", "Skipped"):
            entry["ocr_status"] = sub.ocr_status
            entry["file_url"] = sub.file_url or ""
            entry["uploaded_at"] = str(sub.uploaded_at) if sub.uploaded_at else ""
            completed.append(entry)
        else:
            if sub:
                entry["ocr_status"] = sub.ocr_status  # "Failed" — allow retry
                entry["ocr_result"] = sub.ocr_result or ""
            outstanding.append(entry)

    context.update({
        "token": token,
        "application_name": app_name,
        "full_name": app.full_name,
        "bundle_name": bundle.bundle_name,
        "app_status": app.status,
        "outstanding": outstanding,
        "completed": completed,
        "title": f"Document Upload — {bundle.bundle_name}",
    })
