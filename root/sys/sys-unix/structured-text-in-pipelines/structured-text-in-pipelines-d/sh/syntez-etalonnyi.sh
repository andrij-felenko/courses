#!/usr/bin/env bash
set -euo pipefail

# Конвеєр аналізу журналів доступу API в режимі реального часу:
# 1. curl отримує потік подій у форматі ndjson;
# 2. jq виконує безпечну параметризовану фільтрацію та проєкцію;
# 3. yq перетворює критичні інциденти у формат YAML для систем сповіщення.

LOG_ENDPOINT="https://logs.internal.net/stream"
MIN_LATENCY=1500

curl -sN "${LOG_ENDPOINT}" \
  | jq -c --unbuffered --argjson min_lat "${MIN_LATENCY}" '
      select(.status >= 500 or .latency_ms > $min_lat)
      | {
          alert: "CRITICAL_LATENCY",
          service: .service_name,
          endpoint: .path,
          status: .status,
          latency: .latency_ms,
          timestamp: .ts
        }
    ' \
  | yq -p=json -o=yaml -
