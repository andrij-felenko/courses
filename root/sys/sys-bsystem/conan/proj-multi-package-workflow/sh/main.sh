#!/usr/bin/env bash
set -euo pipefail

echo "==> 1. Підключення до корпоративного сховища JFrog Artifactory"
conan remote add artifactory https://artifactory.company.internal/artifactory/api/conan/conan-local --force
conan remote login artifactory "${CI_CONAN_USER}" -p "${CI_CONAN_TOKEN}"

echo "==> 2. Збірка та пакування бібліотеки під цільову платформу ARM64"
conan create libs/telemetry \
    --profile:build=profiles/linux-x86_64 \
    --profile:host=profiles/linux-arm64 \
    --build=missing

echo "==> 3. Публікація бінарного пакета на віддалений сервер"
conan upload telemetry/1.0.0 -r artifactory --confirm

echo "==> 4. Фіксація повного графа залежностей споживача у conan.lock"
conan lock create apps/telemetry_daemon/conanfile.py \
    --profile:build=profiles/linux-x86_64 \
    --profile:host=profiles/linux-arm64 \
    --lockfile-out=conan.lock

echo "==> 5. Детерміноване встановлення залежностей споживача за замком"
conan install apps/telemetry_daemon \
    --profile:build=profiles/linux-x86_64 \
    --profile:host=profiles/linux-arm64 \
    --lockfile=conan.lock \
    --build=missing

echo "==> 6. Компіляція бінарника через стандартні команди CMakePresets"
cmake --preset conan-armv8-release -S apps/telemetry_daemon
cmake --build --preset conan-armv8-release

echo "==> Успішно! Бінарний виконуваний файл telemetry_daemon зібрано для ARM64."
