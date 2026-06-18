#!/bin/bash
set -e
cd /home/frappe/frappe-bench
echo "=== Installing ocr_validator into Frappe virtualenv ==="
source env/bin/activate
pip install -e apps/ocr_validator --quiet
echo "=== Verifying import ==="
python -c "import ocr_validator; print('IMPORT_OK:', ocr_validator.__file__)"
echo "=== Registering app in apps.txt ==="
grep -qxF "ocr_validator" sites/apps.txt || echo "ocr_validator" >> sites/apps.txt
echo "apps.txt now contains:"
cat sites/apps.txt

echo "=== Running bench install-app ==="
bench --site frontend install-app ocr_validator
echo "=== Running migrate ==="
bench --site frontend migrate
echo "=== Loading fixtures ==="
bench --site frontend import-fixtures --app ocr_validator || echo "Fixtures skipped"
echo "=== Building assets ==="
bench build --app ocr_validator 2>&1 | tail -4
echo "=== Setting default site ==="
bench --site frontend set-config serve_default_site true
echo ""
echo "=========================================="
echo " ALL DONE!"
echo " URL:   http://localhost:8080"
echo " Login: Administrator / admin"
echo " OCR:   http://localhost:8080/ocr-validator"
echo "=========================================="
