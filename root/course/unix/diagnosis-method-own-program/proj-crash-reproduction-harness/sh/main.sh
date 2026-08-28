#!/usr/bin/env bash
set -euo pipefail

TARGET_SRC="crash_target.c"
TARGET_BIN="./crash_target_bin"
CORE_FILE="./core"
REPORT_FILE="crash_triage_report.txt"

SCENARIO="${1:-1}"

echo "=== [1/4] Компіляція бінарника з DWARF символами ==="
gcc -g -O1 -fno-omit-frame-pointer "${TARGET_SRC}" -o "${TARGET_BIN}"

echo "=== [2/4] Налаштування оточення для фіксації Core Dump ==="
ulimit -c unlimited

# Видаляємо старий дамп, якщо існував
rm -f "${CORE_FILE}" "${REPORT_FILE}"

echo "=== [3/4] Запуск програми-мішені зі сценарієм ${SCENARIO} ==="
set +e
"${TARGET_BIN}" "${SCENARIO}"
EXIT_CODE=$?
set -e

echo "Процес завершився з кодом: ${EXIT_CODE}"
if [ "${EXIT_CODE}" -le 128 ]; then
    echo "Помилка: Програма завершилася штатно або без сигналу."
    exit 1
fi

SIGNAL=$((EXIT_CODE - 128))
echo "Зафіксовано сигнал-вбивцю: ${SIGNAL}"

# Перевіряємо локальний core або шукаємо через coredumpctl
if [ ! -f "${CORE_FILE}" ]; then
    if command -v coredumpctl &>/dev/null; then
        echo "Локальний core не знайдено, витягуємо останній знімок через coredumpctl..."
        coredumpctl dump "${TARGET_BIN}" -o "${CORE_FILE}" || true
    fi
fi

if [ ! -f "${CORE_FILE}" ]; then
    echo "Увага: Файл Core Dump не згенеровано. Перевірте /proc/sys/kernel/core_pattern."
    exit 1
fi

echo "=== [4/4] Автоматичний аналіз у GDB Batch Mode ==="
gdb -batch \
    -ex "echo \n--- [СТЕК ВИКЛИКІВ З ЛОКАЛЬНИМИ ЗМІННИМИ] ---\n" \
    -ex "bt full" \
    -ex "echo \n--- [РЕГІСТРИ ПРОЦЕСОРА] ---\n" \
    -ex "info registers" \
    -ex "echo \n--- [ПАМ'ЯТЬ ВЕРШИНИ СТЕКА] ---\n" \
    -ex "x/16gx \$rsp" \
    -ex "echo \n--- [ДИЗАСЕМБЛЮВАННЯ НАВКОЛО ВКАЗІВНИКА ІНСТРУКЦІЙ] ---\n" \
    -ex "disassemble \$rip-16, \$rip+16" \
    "${TARGET_BIN}" "${CORE_FILE}" > "${REPORT_FILE}"

echo "Аналіз успішно завершено. Звіт збережено у: ${REPORT_FILE}"
echo "=========================================================="
head -n 25 "${REPORT_FILE}"
