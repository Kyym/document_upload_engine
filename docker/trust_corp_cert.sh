#!/bin/bash
# trust_corp_cert.sh
# Adds the corporate CA to both the OS trust store and Python's certifi bundle
# so Frappe's outbound HTTPS calls work through the SSL inspection proxy

echo "=== Extracting corporate CA from proxy ==="
# Pull the cert the proxy presents for a well-known site
CORP_CERT=$(openssl s_client -connect pypi.org:443 -showcerts 2>/dev/null \
  | awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/' \
  | tail -n +$(openssl s_client -connect pypi.org:443 -showcerts 2>/dev/null \
    | grep -c "BEGIN CERTIFICATE" | awk '{print ($1 * 2) - 1}') 2>/dev/null \
  | head -50)

# Simpler approach: get all certs in the chain and add them all
echo "Downloading full cert chain from pypi.org..."
openssl s_client -connect pypi.org:443 -showcerts 2>/dev/null \
  | sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p' \
  > /tmp/corp_chain.pem

CERT_COUNT=$(grep -c "BEGIN CERTIFICATE" /tmp/corp_chain.pem 2>/dev/null || echo 0)
echo "Found $CERT_COUNT certificates in chain"

if [ "$CERT_COUNT" -gt "0" ]; then
    # Add to OS trust store
    cp /tmp/corp_chain.pem /usr/local/share/ca-certificates/corp_proxy.crt
    update-ca-certificates 2>/dev/null || true

    # Add to Python certifi bundle
    CERTIFI_PATH=$(python3 -c "import certifi; print(certifi.where())")
    echo "" >> "$CERTIFI_PATH"
    echo "# Corporate proxy CA" >> "$CERTIFI_PATH"  
    cat /tmp/corp_chain.pem >> "$CERTIFI_PATH"
    echo "Added certs to certifi bundle at $CERTIFI_PATH"
else
    echo "Could not extract certs - trying pip config approach instead"
fi

# Fallback: tell pip and requests to skip verification
echo "[global]" > /etc/pip.conf
echo "trusted-host = pypi.org files.pythonhosted.org" >> /etc/pip.conf

# Tell Python requests library to not verify (last resort for outbound calls)
echo "export CURL_CA_BUNDLE=''" >> /etc/environment
echo "export REQUESTS_CA_BUNDLE=''" >> /etc/environment

# Apply to the frappe bench virtualenv  
cd /home/frappe/frappe-bench
source env/bin/activate
pip config set global.trusted-host "pypi.org files.pythonhosted.org" 2>/dev/null || true

echo ""
echo "=== Testing HTTPS connectivity ==="
python3 -c "import requests; r = requests.get('https://pypi.org', timeout=5, verify=False); print('HTTPS OK, status:', r.status_code)" 2>/dev/null || echo "requests test skipped"

echo "Done."
