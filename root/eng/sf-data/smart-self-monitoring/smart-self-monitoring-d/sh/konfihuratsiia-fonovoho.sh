#!/usr/bin/env bash
set -euo pipefail

# Демон smartd передає змінні середовища:
# SMARTD_DEVICE — пристрій (/dev/sda)
# SMARTD_MESSAGE — текст повідомлення про помилку
# SMARTD_FAILTYPE — тип збою (EmailTest, Health, Attribute)

PAYLOAD=$(cat <<EOF
{
  "device": "${SMARTD_DEVICE}",
  "type": "${SMARTD_FAILTYPE}",
  "message": "${SMARTD_MESSAGE}",
  "timestamp": "$(date -Iseconds)"
}
EOF
)

# Відправка JSON-тривоги у внутрішній моніторинг (Alertmanager / Webhook)
curl -s -X POST -H "Content-Type: application/json" \
     -d "${PAYLOAD}" \
     http://alertmanager.internal:9093/api/v2/alerts || true
