#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# VPN connection script - Banco Atlántida (Cisco AnyConnect via openconnect)
#
# IMPORTANT:
#   - This script DOES NOT automate MFA. It runs openconnect in interactive
#     mode so the second factor must be approved manually (push) or entered
#     by a human operator when openconnect prompts for it.
#   - Credentials are read from environment variables ONLY. Never hardcode.
#       BANCATLAN_VPN_USER      -> VPN username
#       BANCATLAN_VPN_PASSWORD  -> VPN primary password (factor #1)
#     If these are not set, openconnect will prompt interactively.
#   - Requires sudo (openconnect needs to configure tun0 and routes).
# ---------------------------------------------------------------------------
 
set -euo pipefail
 
VPN_HOST="vpn.bancatlan.hn"
VPN_PROTOCOL="anyconnect"
 
USER_NAME="${BANCATLAN_VPN_USER:-}"
if [[ -z "${USER_NAME}" ]]; then
  read -r -p "Usuario VPN: " USER_NAME
fi
 
echo ">>> Conectando a ${VPN_HOST} como ${USER_NAME} (protocolo ${VPN_PROTOCOL})"
echo ">>> Cuando aparezca la solicitud de MFA / segundo factor, apruébalo"
echo "    desde tu dispositivo o ingresa el código manualmente."
echo
 
if [[ -n "${BANCATLAN_VPN_PASSWORD:-}" ]]; then
  # Feed only the first password via stdin. Any additional prompts
  # (MFA token, secondary password) will block waiting for interactive input,
  # which is exactly what we want: no MFA automation.
  #
  # --useragent: Spoof AnyConnect client version to prevent
  #              "Please upgrade your AnyConnect Client" rejection.
  printf '%s\n' "${BANCATLAN_VPN_PASSWORD}" | sudo -E openconnect \
    --protocol="${VPN_PROTOCOL}" \
    --user="${USER_NAME}" \
    --useragent="AnyConnect Linux_64 4.10.07061" \
    --passwd-on-stdin \
    "${VPN_HOST}"
else
  sudo -E openconnect \
    --protocol="${VPN_PROTOCOL}" \
    --user="${USER_NAME}" \
    --useragent="AnyConnect Linux_64 4.10.07061" \
    "${VPN_HOST}"
fi
