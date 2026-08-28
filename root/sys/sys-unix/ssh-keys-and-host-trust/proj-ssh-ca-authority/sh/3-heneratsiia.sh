#!/usr/bin/env bash
set -euo pipefail

USER_PUB="id_ed25519.pub"
CA_KEY="/etc/ssh/ca/ssh_user_ca"
KEY_ID="bohdan.felenko@company.com"
SERIAL="10492"
PRINCIPALS="bohdan,ubuntu,deploy"
VALIDITY="+8h"

ssh-keygen -s "${CA_KEY}" \
    -I "${KEY_ID}" \
    -z "${SERIAL}" \
    -n "${PRINCIPALS}" \
    -V "${VALIDITY}" \
    -O no-agent-forwarding \
    -O no-x11-forwarding \
    "${USER_PUB}"

# Згенеровано файл id_ed25519-cert.pub
