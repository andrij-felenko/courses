#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="embedded-builder:v1.4.2"
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Отримання часу останнього коміту в форматі UNIX Epoch
if [ -d ".git" ]; then
    SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
else
    SOURCE_DATE_EPOCH="1700000000"
fi

echo "=== Запуск герметичної збірки (SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}) ==="

# Запуск збірки з вимкненою мережею та ізольованим середовищем
docker run --rm \
    --network none \
    --user "$(id -u):$(id -g)" \
    --env SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}" \
    --volume "${WORKSPACE_DIR}:/workspace" \
    "${IMAGE_TAG}" \
    "make clean && make -j$(nproc)"

echo "=== Збірку завершено. Хеш релізу: ==="
sha256sum build/firmware.bin
