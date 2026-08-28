#!/usr/bin/env bash
set -euo pipefail

# Перевірка наявності аргументів командного рядка
if [ "$#" -ne 2 ]; then
    echo "Використання: $0 <шлях_до_старої_бібліотеки.so> <шлях_до_нової_бібліотеки.so>"
    echo "Приклад:     $0 /usr/lib/libtelemetry.so.1.0 /build/libtelemetry.so.1.1"
    exit 1
fi

OLD_LIB="$1"
NEW_LIB="$2"

if [ ! -f "${OLD_LIB}" ] || [ ! -f "${NEW_LIB}" ]; then
    echo "Помилка: один із вказаних файлів бібліотек не існує!"
    exit 1
fi

# Створення тимчасового каталогу для проміжних файлів
TMP_DIR="$(mktemp -d /tmp/abi-audit-XXXXXX)"
trap 'rm -rf "${TMP_DIR}"' EXIT

OLD_SYM="${TMP_DIR}/old_symbols.txt"
NEW_SYM="${TMP_DIR}/new_symbols.txt"

# Функція вилучення та нормалізації символів
extract_public_symbols() {
    local lib_file="$1"
    local out_file="$2"
    
    nm -D --defined-only "${lib_file}" \
        | awk '$2 ~ /^[TDBRW]$/ { print $2, $3 }' \
        | grep -vE ' ( _init|_fini|__bss_start|_edata|_end|__gmon_start__|_ITM_.*)$' \
        | sort -u -k2,2 > "${out_file}"
}

echo "[*] Вилучення публічних динамічних символів..."
extract_public_symbols "${OLD_LIB}" "${OLD_SYM}"
extract_public_symbols "${NEW_LIB}" "${NEW_SYM}"

# Знаходження видалених символів (були в старій версії, зникли в новій)
REMOVED_SYMBOLS=$(comm -23 "${OLD_SYM}" "${NEW_SYM}")

# Знаходження доданих символів (нові функції, розширення API)
ADDED_SYMBOLS=$(comm -13 "${OLD_SYM}" "${NEW_SYM}")

# Знаходження символів зі зміненим типом (наприклад, функція T стала змінною D)
CHANGED_TYPE=$(join -1 2 -2 2 "${OLD_SYM}" "${NEW_SYM}" | awk '$2 != $3 { print $1 ": " $2 " -> " $3 }')

echo "=================================================================="
echo "      Звіт про двійкову сумісність спільного об'єкта (ABI Diff)   "
echo "  Базовий об'єкт (OLD): ${OLD_LIB}"
echo "  Новий об'єкт   (NEW): ${NEW_LIB}"
echo "=================================================================="

ABI_BROKEN=0

if [ -n "${REMOVED_SYMBOLS}" ]; then
    echo -e "\n[!] КРИТИЧНИЙ РОЗРИВ ABI: Видалено публічні символи!"
    echo "    Усі програми, зібрані з попередньою версією, зазнають аварії:"
    echo "${REMOVED_SYMBOLS}" | sed 's/^/      [-] /'
    ABI_BROKEN=1
fi

if [ -n "${CHANGED_TYPE}" ]; then
    echo -e "\n[!] КРИТИЧНИЙ РОЗРИВ ABI: Змінено тип секції символів!"
    echo "${CHANGED_TYPE}" | sed 's/^/      [!] /'
    ABI_BROKEN=1
fi

if [ -n "${ADDED_SYMBOLS}" ]; then
    echo -e "\n[i] Безпечне розширення API (додано нові функції/змінні):"
    echo "${ADDED_SYMBOLS}" | sed 's/^/      [+] /'
fi

if [ "${ABI_BROKEN}" -eq 0 ] && [ -z "${ADDED_SYMBOLS}" ]; then
    echo -e "\n[OK] Двійковий інтерфейс повністю ідентичний (100% сумісність)."
fi

echo -e "\n------------------------------------------------------------------"
if [ "${ABI_BROKEN}" -eq 1 ]; then
    echo "ВИСНОВОК: Двійкову сумісність порушено. Обов'язково підвищіть SONAME (MAJOR версію)!"
    exit 2
else
    echo "ВИСНОВОК: Зворотна сумісність збережена. Дозволено мінорне оновлення (MINOR/PATCH)."
    exit 0
fi
