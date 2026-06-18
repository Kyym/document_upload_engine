###############################################################################
#  OCR Validator – Full Docker Setup Script
#  Run this from PowerShell as Administrator:
#    cd C:\Users\GCA17689.GCA.000\Desktop\ocr_validator_app\docker
#    .\setup.ps1
###############################################################################

$ErrorActionPreference = "Stop"
$DOCKER  = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
$COMPOSE = "C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe"

# If docker-compose not found at that path, try the plugin version
if (-not (Test-Path $COMPOSE)) {
    $COMPOSE = $DOCKER   # will use 'docker compose' subcommand below
    $USE_PLUGIN = $true
} else {
    $USE_PLUGIN = $false
}

$APP_SRC  = "C:\Users\GCA17689.GCA.000\Desktop\ocr_validator_app"
$COMPOSE_DIR = $PSScriptRoot   # same folder as this script
$FRAPPE_DOCKER = "C:\Users\GCA17689.GCA.000\projects\frappe_docker"
$SITE     = "frontend"
$DB_PASS  = "admin"
$ADMIN_PASS = "admin"

function dc {
    param([string[]]$args_)
    if ($USE_PLUGIN) {
        & $DOCKER compose --project-directory $COMPOSE_DIR -f "$COMPOSE_DIR\compose.yaml" @args_
    } else {
        & $COMPOSE --project-directory $COMPOSE_DIR -f "$COMPOSE_DIR\compose.yaml" @args_
    }
}

function dexec {
    param([string]$container, [string]$cmd)
    & $DOCKER exec $container bash -c $cmd
}

###############################################################################
Write-Host "`n=== STEP 1: Ensure frappe_docker_redis-cache-data volume exists ===" -ForegroundColor Cyan
& $DOCKER volume create frappe_docker_redis-cache-data 2>&1 | Out-Null
Write-Host "Volume ready." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 2: Copy updated compose.yaml to frappe_docker folder ===" -ForegroundColor Cyan
Copy-Item "$COMPOSE_DIR\compose.yaml" "$FRAPPE_DOCKER\compose.yaml" -Force
Write-Host "compose.yaml copied to $FRAPPE_DOCKER" -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 3: Bring down the existing broken stack ===" -ForegroundColor Cyan
Set-Location $FRAPPE_DOCKER
& $DOCKER compose -f "$FRAPPE_DOCKER\compose.yaml" down --remove-orphans 2>&1
Write-Host "Stack stopped." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 4: Start the full stack (mariadb + redis + frappe) ===" -ForegroundColor Cyan
& $DOCKER compose -f "$FRAPPE_DOCKER\compose.yaml" up -d --wait 2>&1
Write-Host "Stack started." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 5: Wait for backend to be healthy ===" -ForegroundColor Cyan
$retries = 0
do {
    Start-Sleep -Seconds 5
    $status = & $DOCKER inspect frappe_docker-backend-1 --format "{{.State.Status}}" 2>&1
    Write-Host "  backend status: $status"
    $retries++
} while ($status -ne "running" -and $retries -lt 20)
Write-Host "Backend is running." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 6: Check if site '$SITE' exists, create if needed ===" -ForegroundColor Cyan
$siteExists = & $DOCKER exec frappe_docker-backend-1 bash -c "test -f /home/frappe/frappe-bench/sites/$SITE/site_config.json && echo yes || echo no" 2>&1
if ($siteExists.Trim() -eq "no") {
    Write-Host "  Creating site '$SITE'..." -ForegroundColor Yellow
    & $DOCKER exec frappe_docker-backend-1 bash -c "bench new-site $SITE --mariadb-root-password $DB_PASS --admin-password $ADMIN_PASS --no-mariadb-socket" 2>&1
    Write-Host "  Site created." -ForegroundColor Green
} else {
    Write-Host "  Site '$SITE' already exists, skipping creation." -ForegroundColor Green
}

###############################################################################
Write-Host "`n=== STEP 7: Set site to serve as default ===" -ForegroundColor Cyan
& $DOCKER exec frappe_docker-backend-1 bash -c "bench --site $SITE set-config serve_default_site true" 2>&1
Write-Host "Done." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 8: Install Tesseract + Python deps inside container ===" -ForegroundColor Cyan
& $DOCKER exec frappe_docker-backend-1 bash -c @"
apt-get update -qq && apt-get install -y -qq tesseract-ocr tesseract-ocr-eng poppler-utils libgl1 2>&1 | tail -5
pip install pytesseract Pillow pdf2image --quiet
echo 'DEPS_OK'
"@ 2>&1
Write-Host "Tesseract and Python dependencies installed." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 9: Copy ocr_validator app into the container ===" -ForegroundColor Cyan
& $DOCKER cp "$APP_SRC\." "frappe_docker-backend-1:/home/frappe/frappe-bench/apps/ocr_validator" 2>&1
# Fix ownership
& $DOCKER exec frappe_docker-backend-1 bash -c "chown -R frappe:frappe /home/frappe/frappe-bench/apps/ocr_validator" 2>&1
Write-Host "App copied." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 10: Install ocr_validator app on the site ===" -ForegroundColor Cyan
& $DOCKER exec frappe_docker-backend-1 bash -c "cd /home/frappe/frappe-bench && pip install -e apps/ocr_validator --quiet" 2>&1
& $DOCKER exec frappe_docker-backend-1 bash -c "bench --site $SITE install-app ocr_validator 2>&1" 2>&1
Write-Host "App installed." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 11: Run migrate (creates DocTypes in DB) ===" -ForegroundColor Cyan
& $DOCKER exec frappe_docker-backend-1 bash -c "bench --site $SITE migrate 2>&1" 2>&1
Write-Host "Migration done." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 12: Load seed OCR rules (fixtures) ===" -ForegroundColor Cyan
& $DOCKER exec frappe_docker-backend-1 bash -c "bench --site $SITE import-fixtures --app ocr_validator 2>&1" 2>&1
Write-Host "Fixtures loaded." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 13: Build assets ===" -ForegroundColor Cyan
& $DOCKER exec frappe_docker-backend-1 bash -c "bench build --app ocr_validator 2>&1 | tail -5" 2>&1
Write-Host "Assets built." -ForegroundColor Green

###############################################################################
Write-Host "`n=== STEP 14: Restart services to pick up new app ===" -ForegroundColor Cyan
& $DOCKER compose -f "$FRAPPE_DOCKER\compose.yaml" restart backend queue-short queue-long scheduler websocket 2>&1
Write-Host "Services restarted." -ForegroundColor Green

###############################################################################
Write-Host "`n======================================================" -ForegroundColor Green
Write-Host "  DONE! Open http://localhost:8080 in your browser." -ForegroundColor Green
Write-Host "  Login:  Administrator / $ADMIN_PASS"              -ForegroundColor Green
Write-Host "  OCR Validator UI: http://localhost:8080/ocr-validator" -ForegroundColor Green
Write-Host "======================================================`n" -ForegroundColor Green
