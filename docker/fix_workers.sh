#!/bin/bash
# fix_workers.sh
# Installs ocr_validator into the bench virtualenv so all workers can import it

BENCH=/home/frappe/frappe-bench

echo "=== Installing ocr_validator into bench virtualenv ==="
$BENCH/env/bin/pip install -e $BENCH/apps/ocr_validator --quiet

echo "=== Verifying all workers can import it ==="
$BENCH/env/bin/python -c "import ocr_validator; print('OK:', ocr_validator.__file__)"

echo "=== Also installing pytesseract/Pillow into venv ==="
$BENCH/env/bin/pip install pytesseract Pillow pdf2image --quiet

echo "=== Done ==="
