#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# CA trust setup - Banco Atlántida SAP host (10.165.6.8)
#
# The SAP server at 10.165.6.8 uses a self-signed / internal-CA TLS
# certificate. This script:
#   1. Downloads the server certificate via openssl s_client.
#   2. Installs it into the system trust store (/usr/local/share/ca-certificates).
#   3. Exports NODE_EXTRA_CA_CERTS so Node.js / Playwright trust it.
#   4. Exports SSL_CERT_FILE so Python / requests trust it.
#
# Requires sudo to write into the system trust store.
#
# NOTE: The host 10.165.6.8 is only reachable through the corporate VPN,
#       so this script must be run AFTER the VPN tunnel is established
#       (see connect-bancatlan.sh).
# ---------------------------------------------------------------------------

set -euo pipefail

SAP_HOST="10.165.6.8"
SAP_PORT="44300"  # SAP Fiori ICM HTTPS port (not 443)
TMP_CERT="/tmp/bancatlan-ca.pem"
TRUST_STORE_DIR="/usr/local/share/ca-certificates"
TRUST_STORE_FILE="${TRUST_STORE_DIR}/bancatlan-ca.crt"

echo ">>> Descargando certificado desde ${SAP_HOST}:${SAP_PORT} ..."
openssl s_client -showcerts -connect "${SAP_HOST}:${SAP_PORT}" </dev/null 2>/dev/null \
  | openssl x509 -outform PEM > "${TMP_CERT}"

if [[ ! -s "${TMP_CERT}" ]]; then
  echo "ERROR: no se pudo descargar el certificado de ${SAP_HOST}:${SAP_PORT}." >&2
  echo "       Verifique que la VPN esté activa y el host sea alcanzable." >&2
  exit 1
fi

echo ">>> Instalando certificado en el trust store del sistema ..."
sudo cp "${TMP_CERT}" "${TRUST_STORE_FILE}"
sudo update-ca-certificates

# Export certificate paths for Node.js (Playwright) and Python (requests).
# These need to be `source`d by the caller's shell; running this script in a
# subshell will not propagate them. Persist them in the current user's
# ~/.bashrc for convenience as well.
export NODE_EXTRA_CA_CERTS="${TRUST_STORE_FILE}"
export SSL_CERT_FILE="${TRUST_STORE_FILE}"

if ! grep -q "NODE_EXTRA_CA_CERTS=${TRUST_STORE_FILE}" "${HOME}/.bashrc" 2>/dev/null; then
  {
    echo ""
    echo "# Banco Atlántida CA trust (added by setup-ca-trust.sh)"
    echo "export NODE_EXTRA_CA_CERTS=${TRUST_STORE_FILE}"
    echo "export SSL_CERT_FILE=${TRUST_STORE_FILE}"
  } >> "${HOME}/.bashrc"
fi

echo ">>> Certificado CA instalado correctamente en ${TRUST_STORE_FILE}"
echo ">>> NODE_EXTRA_CA_CERTS y SSL_CERT_FILE exportados."
