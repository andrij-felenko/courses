#!/usr/bin/env bash
# ==============================================================================
# Сценарій автоматичної перевірки контрактів у CI/CD пайплайні
# ==============================================================================
set -euo pipefail

BROKER_URL="http://pact-broker.internal.net"
CONSUMER_NAME="DigitalHomes-MonolithBackend"
PROVIDER_NAME="Telemetry-Microservice"
GIT_COMMIT=$(git rev-parse HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "=== 1. ЗАПУСК КЛІЄНТСЬКИХ ТЕСТІВ ТА ГЕНЕРАЦІЯ КОНТРАКТІВ ==="
# Виконання unit-тестів моноліта, які генерують файли в ./pacts/
npm test -- --grep "PactContractTests"

echo "=== 2. ПУБЛІКАЦІЯ КОНТРАКТУ В PACT BROKER ==="
pact-broker publish ./pacts \
  --consumer-app-version="${GIT_COMMIT}" \
  --branch="${GIT_BRANCH}" \
  --broker-base-url="${BROKER_URL}"

echo "=== 3. ПЕРЕВІРКА МАТРИЦІ СУМІСНОСТІ (CAN-I-DEPLOY) ==="
# Команда запитує в Broker: "Чи безпечно розгортати цю версію моноліта на Production?"
# Broker перевіряє, чи верифікував Провайдер, розгорнутий на Production, саме цей коміт.
if pact-broker can-i-deploy \
    --pacticipant "${CONSUMER_NAME}" \
    --version "${GIT_COMMIT}" \
    --to-environment production \
    --broker-base-url="${BROKER_URL}"; then
  echo "[SUCCESS] Матриця сумісна! Розпочинаємо розгортання на Production."
else
  echo "[FAILURE] Злам сумісності контрактів! Деплой заблоковано."
  exit 1
fi
