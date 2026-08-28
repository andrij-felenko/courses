#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THIRD_PARTY_DIR="${PROJECT_ROOT}/third_party"
PATCHES_DIR="${PROJECT_ROOT}/patches"

echo "[1/3] Оновлення бібліотеки TinyXML2..."
TINYXML2_TAG="10.0.0"
TINYXML2_DIR="${THIRD_PARTY_DIR}/tinyxml2"
rm -rf "${TINYXML2_DIR}"

# Завантажуємо чистий стан релізу з глибиною 1
git clone --depth 1 --branch "${TINYXML2_TAG}" https://github.com/leethomason/tinyxml2.git "${TINYXML2_DIR}"

# Очищуємо каталог від службових файлів Git, документації та важких тестів
rm -rf "${TINYXML2_DIR}/.git" "${TINYXML2_DIR}/docs" "${TINYXML2_DIR}/test"

# Накладання локального патчу за наявності
if [ -f "${PATCHES_DIR}/0001-tinyxml2-disable-warnings.patch" ]; then
    echo "  -> Накладання локального патчу на TinyXML2..."
    git -C "${PROJECT_ROOT}" apply --directory="third_party/tinyxml2" "${PATCHES_DIR}/0001-tinyxml2-disable-warnings.patch"
fi

echo "[2/3] Оновлення однофайлової бібліотеки Miniz (C-джерело та заголовок)..."
MINIZ_TAG="3.0.2"
MINIZ_DIR="${THIRD_PARTY_DIR}/miniz"
mkdir -p "${MINIZ_DIR}"
curl -sSL "https://raw.githubusercontent.com/richgel999/miniz/${MINIZ_TAG}/miniz.c" -o "${MINIZ_DIR}/miniz.c"
curl -sSL "https://raw.githubusercontent.com/richgel999/miniz/${MINIZ_TAG}/miniz.h" -o "${MINIZ_DIR}/miniz.h"

echo "[3/3] Синхронізацію завершено успішно. Усі файли зафіксовано в каталозі third_party/."
