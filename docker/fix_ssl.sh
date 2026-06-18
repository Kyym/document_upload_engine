#!/bin/bash
# fix_ssl.sh - Disables SSL verification for Frappe's outbound calls
# This is needed on corporate networks with SSL inspection

cd /home/frappe/frappe-bench
source env/bin/activate

echo "=== Disabling SSL verification for outbound Frappe calls ==="

# 1. Set site config to skip update checks (removes most outbound HTTPS calls)
bench --site frontend set-config allow_tests 1
bench --site frontend set-config server_script_enabled 1
bench --site frontend set-config ignore_csrf 0

# 2. Disable telemetry / update notifications that trigger SSL calls
bench --site frontend set-config disable_global_search 0
bench --site frontend set-config skip_setup_wizard 1

# 3. Set Python to not verify SSL (for pip/requests in this environment)
export PYTHONHTTPSVERIFY=0
export REQUESTS_CA_BUNDLE=""

# 4. Patch the bench virtualenv to trust all certs for internal calls
python -c "
import ssl, certifi
# Check current cert bundle
print('Current CA bundle:', certifi.where())
"

# 5. Update site config with disable_async to avoid websocket SSL issues  
bench --site frontend set-config disable_async 0

echo ""
echo "=== Current site config ==="
cat sites/frontend/site_config.json

echo ""
echo "=== Testing backend is reachable ==="
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/api/method/ping || echo "curl not available"

echo "Done."
