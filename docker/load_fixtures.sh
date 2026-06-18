#!/bin/bash
cd /home/frappe/frappe-bench
source env/bin/activate

echo "=== Loading OCR Compare seed rules ==="
# Frappe v15 uses 'bench --site <site> execute' to load fixtures
# Try the new way first, fall back to direct Python
bench --site frontend execute frappe.utils.fixtures.sync_fixtures --kwargs '{"app": "ocr_validator"}' 2>/dev/null || \
python -c "
import frappe
frappe.init(site='frontend')
frappe.connect()
from frappe.utils.fixtures import sync_fixtures
sync_fixtures(app='ocr_validator')
frappe.db.commit()
print('Fixtures loaded OK')
frappe.destroy()
"

echo "=== Restarting workers to pick up new app ==="
# Signal gunicorn to reload gracefully
kill -HUP $(pgrep -f gunicorn) 2>/dev/null || echo "Gunicorn reload skipped (handled by supervisor)"

echo "=== Done ==="
