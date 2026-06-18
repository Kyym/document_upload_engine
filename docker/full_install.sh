#!/bin/bash
# full_install.sh — runs inside frappe_docker-backend-1
# Installs erpnext + ocr_validator on the 'frontend' site end-to-end

set -e
SITE="frontend"
BENCH="/home/frappe/frappe-bench"
cd $BENCH

echo ""
echo "============================================="
echo " OCR Validator — Full Site Install"
echo "============================================="

# ── Step 1: Check what apps are already installed ──────────────────────────
echo ""
echo "[1/6] Checking installed apps..."
INSTALLED=$(bench --site $SITE list-apps 2>/dev/null || echo "none")
echo "Currently installed: $INSTALLED"

# ── Step 2: Install ERPNext if not already there ───────────────────────────
if echo "$INSTALLED" | grep -q "erpnext"; then
    echo "[2/6] ERPNext already installed — skipping."
else
    echo "[2/6] Installing ERPNext (this takes 3-5 minutes)..."
    bench --site $SITE install-app erpnext
    echo "      ERPNext installed OK."
fi

# ── Step 3: Install ocr_validator ─────────────────────────────────────────
if echo "$INSTALLED" | grep -q "ocr_validator"; then
    echo "[3/6] ocr_validator already installed — running migrate to sync."
    bench --site $SITE migrate
else
    echo "[3/6] Installing ocr_validator..."
    bench --site $SITE install-app ocr_validator
    echo "      ocr_validator installed OK."
fi

# ── Step 4: Load seed OCR rules ───────────────────────────────────────────
echo ""
echo "[4/6] Loading seed OCR rules (fixtures)..."
bench --site $SITE import-fixtures --app ocr_validator 2>&1 || echo "      Fixtures skipped (may already exist)."

# ── Step 5: Set site as default ───────────────────────────────────────────
echo ""
echo "[5/6] Setting $SITE as default site..."
bench --site $SITE set-config serve_default_site true

# ── Step 6: Build assets ──────────────────────────────────────────────────
echo ""
echo "[6/6] Building frontend assets..."
bench build --app ocr_validator 2>&1 | tail -6

echo ""
echo "============================================="
echo " DONE!"
echo " Open: http://localhost:8080"
echo " Login: Administrator / admin"
echo " OCR UI: http://localhost:8080/ocr-validator"
echo "============================================="
