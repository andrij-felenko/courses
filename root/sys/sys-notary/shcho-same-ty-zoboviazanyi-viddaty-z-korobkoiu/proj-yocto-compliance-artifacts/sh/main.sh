#!/usr/bin/env bash
set -euo pipefail

MANIFEST="output/legal-info/manifest.csv"
SOURCES_DIR="output/legal-info/sources"
LICENSES_DIR="output/legal-info/licenses"

echo "=== Запуск перевірки повноти ліцензійного пакета ==="

ERRORS=0

# Пропуск заголовка CSV та читання кожного рядка
tail -n +2 "$MANIFEST" | while IFS=',' read -r pkg ver lic licfile src site; do
    # Видалення лапок
    pkg="${pkg//\"/}"
    ver="${ver//\"/}"
    lic="${lic//\"/}"
    src="${src//\"/}"

    # Перевірка наявності вихідного архіву для копілефтних ліцензій
    if [[ "$lic" =~ GPL|LGPL|MPL|AGPL ]]; then
        ARCHIVE_PATH="$SOURCES_DIR/$src"
        if [[ ! -f "$ARCHIVE_PATH" || ! -s "$ARCHIVE_PATH" ]]; then
            echo "❌ ПОМИЛКА: Відсутній архів вихідних кодів для $pkg-$ver ($lic): $ARCHIVE_PATH"
            ERRORS=$((ERRORS + 1))
        else
            echo "  ✓ Знайдено вихідний код: $src"
        fi
    fi
done

if [[ "$ERRORS" -gt 0 ]]; then
    echo "❌ Валідація провалена: виявлено $ERRORS порушень у комплаєнс-пакеті."
    exit 1
fi

echo "✅ Усі обов'язкові вихідні коди та ліцензії присутні. Пакет готовий до релізу."
