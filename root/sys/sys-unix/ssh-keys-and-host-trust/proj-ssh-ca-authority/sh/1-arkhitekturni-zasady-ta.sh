#!/usr/bin/env bash
set -euo pipefail

CA_DIR="/etc/ssh/ca"
mkdir -p "${CA_DIR}"
chmod 700 "${CA_DIR}"

# 1. Генерація кореневого ключа Host CA
ssh-keygen -t ed25519 -a 100 -f "${CA_DIR}/ssh_host_ca" \
    -C "CA-HOST-INFRASTRUCTURE-PROD" -N ""

# 2. Генерація кореневого ключа User CA
ssh-keygen -t ed25519 -a 100 -f "${CA_DIR}/ssh_user_ca" \
    -C "CA-USER-DEVELOPERS-PROD" -N ""

chmod 600 "${CA_DIR}/ssh_host_ca" "${CA_DIR}/ssh_user_ca"
chmod 644 "${CA_DIR}/ssh_host_ca.pub" "${CA_DIR}/ssh_user_ca.pub"
