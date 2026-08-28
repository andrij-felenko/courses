#!/usr/bin/env bash
set -euo pipefail

HOST_PUB="/etc/ssh/ssh_host_ed25519_key.pub"
CA_KEY="/etc/ssh/ca/ssh_host_ca"
HOST_ID="srv-db-prod-01"
PRINCIPALS="srv-db-prod-01,srv-db-prod-01.infra.company.com,10.20.0.15"

# Підпис хост-сертифіката (-h вказує тип host certificate)
ssh-keygen -s "${CA_KEY}" \
    -I "${HOST_ID}" \
    -h \
    -n "${PRINCIPALS}" \
    -V "+365d" \
    "${HOST_PUB}"

# Результат: згенеровано файл /etc/ssh/ssh_host_ed25519_key-cert.pub
chmod 644 /etc/ssh/ssh_host_ed25519_key-cert.pub
