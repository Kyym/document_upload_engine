import frappe
frappe.init(site='frontend')
frappe.connect()

from frappe.utils.fixtures import sync_fixtures
sync_fixtures(app='ocr_validator')
frappe.db.commit()

# Verify rules were loaded
count = frappe.db.count('OCR Compare')
print(f"OCR Compare rules loaded: {count} records")

if count > 0:
    rules = frappe.get_all('OCR Compare', fields=['document_type', 'country', 'enabled'])
    for r in rules:
        print(f"  - {r.document_type} / {r.country} (enabled={r.enabled})")

frappe.destroy()
