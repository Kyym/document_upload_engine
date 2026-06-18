#!/bin/bash
set -e
BENCH=/home/frappe/frappe-bench

echo "=== Step 1: Verify ocr_validator app is in apps/ ==="
ls $BENCH/apps/ | grep ocr || echo "NOT FOUND - needs copy"

echo "=== Step 2: Install into bench venv ==="
$BENCH/env/bin/pip install -e $BENCH/apps/ocr_validator --quiet
$BENCH/env/bin/python -c "import ocr_validator; print('IMPORT OK')"

echo "=== Step 3: Ensure in apps.txt ==="
grep -qxF "ocr_validator" $BENCH/sites/apps.txt || echo "ocr_validator" >> $BENCH/sites/apps.txt
echo "apps.txt:"
cat $BENCH/sites/apps.txt

echo "=== Step 4: Verify site config ==="
cat $BENCH/sites/frontend/site_config.json

echo "=== All done ==="
