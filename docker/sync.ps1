###############################################################################
#  sync.ps1 — Re-sync app code changes into the running container
#  Use this after every code edit instead of running setup.ps1 again.
#  Run from PowerShell:
#    cd C:\Users\GCA17689.GCA.000\Desktop\ocr_validator_app\docker
#    .\sync.ps1
###############################################################################

$DOCKER   = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
$APP_SRC  = "C:\Users\GCA17689.GCA.000\Desktop\ocr_validator_app"
$SITE     = "frontend"
$FRAPPE_DOCKER = "C:\Users\GCA17689.GCA.000\projects\frappe_docker"

Write-Host "`n--- Copying updated app files into container..." -ForegroundColor Cyan
& $DOCKER cp "$APP_SRC\." "frappe_docker-backend-1:/home/frappe/frappe-bench/apps/ocr_validator"
& $DOCKER exec frappe_docker-backend-1 bash -c "chown -R frappe:frappe /home/frappe/frappe-bench/apps/ocr_validator"

Write-Host "--- Running migrate..." -ForegroundColor Cyan
& $DOCKER exec frappe_docker-backend-1 bash -c "bench --site $SITE migrate 2>&1 | tail -10"

Write-Host "--- Rebuilding assets..." -ForegroundColor Cyan
& $DOCKER exec frappe_docker-backend-1 bash -c "bench build --app ocr_validator 2>&1 | tail -5"

Write-Host "--- Restarting backend..." -ForegroundColor Cyan
& $DOCKER compose -f "$FRAPPE_DOCKER\compose.yaml" restart backend queue-short queue-long

Write-Host "`nDone! Refresh http://localhost:8080/ocr-validator" -ForegroundColor Green
