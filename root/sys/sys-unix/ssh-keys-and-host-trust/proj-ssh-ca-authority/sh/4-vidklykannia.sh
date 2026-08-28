#!/usr/bin/env bash
set -euo pipefail

KRL_FILE="/etc/ssh/revoked_keys.krl"

# Створення або оновлення списку KRL за сертифікатом
ssh-keygen -k -f "${KRL_FILE}" -u id_ed25519-cert.pub

# Або відкликання за серійним номером та публічним ключем CA
# ssh-keygen -k -f "${KRL_FILE}" -s /etc/ssh/ca/ssh_user_ca.pub -z 10492
