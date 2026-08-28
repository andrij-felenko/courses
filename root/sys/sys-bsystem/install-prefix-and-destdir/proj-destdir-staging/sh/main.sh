#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(pwd)"
BUILD_DIR="${PROJECT_ROOT}/build"
STAGING_DIR="${PROJECT_ROOT}/staging_root"
DIST_DIR="${PROJECT_ROOT}/dist"
TARGET_PREFIX="/usr"
PKG_NAME="calcapp-1.0.0-linux-x86_64"

echo "=== 1. Очищення робочих просторів ==="
rm -rf "${BUILD_DIR}" "${STAGING_DIR}" "${DIST_DIR}"
mkdir -p "${STAGING_DIR}" "${DIST_DIR}"

echo "=== 2. Конфігурація проєкту для цільового префікса ${TARGET_PREFIX} ==="
cmake -S "${PROJECT_ROOT}" -B "${BUILD_DIR}" \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_INSTALL_PREFIX="${TARGET_PREFIX}" \
    -DCMAKE_INSTALL_SYSCONFDIR=/etc \
    -DCMAKE_INSTALL_LOCALSTATEDIR=/var

echo "=== 3. Компіляція вихідного коду ==="
cmake --build "${BUILD_DIR}" --parallel "$(nproc)"

echo "=== 4. Ізольоване встановлення у Staging Root (DESTDIR) ==="
# Викликаємо cmake --install із передачею DESTDIR
DESTDIR="${STAGING_DIR}" cmake --install "${BUILD_DIR}"

echo "=== 5. Відокремлення налагоджувальних символів (Split Debug) ==="
BIN_FILE="${STAGING_DIR}${TARGET_PREFIX}/bin/calc_cli"
LIB_FILE="${STAGING_DIR}${TARGET_PREFIX}/lib/libcalc.so.1.0.0"
DEBUG_DIR="${STAGING_DIR}${TARGET_PREFIX}/lib/debug"
mkdir -p "${DEBUG_DIR}"

# Обробка виконуваного файлу
objcopy --only-keep-debug "${BIN_FILE}" "${DEBUG_DIR}/calc_cli.debug"
strip --strip-unneeded "${BIN_FILE}"
objcopy --add-gnu-debuglink="${DEBUG_DIR}/calc_cli.debug" "${BIN_FILE}"

# Обробка спільної бібліотеки
objcopy --only-keep-debug "${LIB_FILE}" "${DEBUG_DIR}/libcalc.so.debug"
strip --strip-unneeded "${LIB_FILE}"
objcopy --add-gnu-debuglink="${DEBUG_DIR}/libcalc.so.debug" "${LIB_FILE}"

echo "=== 6. Автоматизована валідація артефактів у Staging ==="

# Перевірка 1: Фізична присутність файлів
test -f "${BIN_FILE}" || { echo "ПОМИЛКА: calc_cli відсутній!"; exit 1; }
test -f "${LIB_FILE}" || { echo "ПОМИЛКА: libcalc.so відсутня!"; exit 1; }
test -f "${STAGING_DIR}${TARGET_PREFIX}/share/calcapp/operations.json" || \
    { echo "ПОМИЛКА: operations.json відсутній!"; exit 1; }

# Перевірка 2: Контроль RUNPATH у бінарнику через readelf
echo "--- Перевірка RUNPATH у виконуваному файлі ---"
RUNPATH_ENTRY=$(readelf -d "${BIN_FILE}" | grep -E '(RUNPATH|RPATH)' || true)
echo "Знайдено: ${RUNPATH_ENTRY}"

# Перевіряємо, чи містить бінарник очікуваний відносний шлях
if ! echo "${RUNPATH_ENTRY}" | grep -q '\$ORIGIN/../lib'; then
    echo "ПОМИЛКА: RUNPATH не містить \$ORIGIN/../lib!"
    exit 1
fi

# Сувора перевірка: чи не потрапив шлях staging у заголовок ELF
if echo "${RUNPATH_ENTRY}" | grep -q "${STAGING_DIR}"; then
    echo "КРИТИЧНИЙ ДЕФЕКТ: Шлях Staging (${STAGING_DIR}) витік у заголовок ELF!"
    exit 1
fi

# Перевірка 3: Сканування скомпільованих констант утилітою strings
echo "--- Сканування зашитих рядків у секції .rodata ---"
if strings "${BIN_FILE}" | grep -q "${STAGING_DIR}"; then
    echo "КРИТИЧНИЙ ДЕФЕКТ: Тимчасовий каталог збірки зашитий у двійковий код!"
    exit 1
fi

if strings "${BIN_FILE}" | grep -q "${TARGET_PREFIX}/share/calcapp"; then
    echo "OK: Вшитий шлях відповідає цільовому префіксу (${TARGET_PREFIX}/share/calcapp)"
else
    echo "ПОМИЛКА: Цільовий префікс відсутній у бінарнику!"
    exit 1
fi

echo "=== 7. Нормалізація прав доступу та створення пакетного архіву ==="
# Встановлюємо стандартні права FHS: 0755 для каталогів та бінарників, 0644 для даних
find "${STAGING_DIR}" -type d -exec chmod 0755 {} +
find "${STAGING_DIR}${TARGET_PREFIX}/bin" -type f -exec chmod 0755 {} +
find "${STAGING_DIR}${TARGET_PREFIX}/lib" -type f -name "*.so*" -exec chmod 0755 {} +
find "${STAGING_DIR}${TARGET_PREFIX}/share" -type f -exec chmod 0644 {} +
find "${STAGING_DIR}${TARGET_PREFIX}/include" -type f -exec chmod 0644 {} +

# Формуємо стиснений tarball із закріпленням власника root:root (UID=0, GID=0)
tar --create --gzip --verbose \
    --owner=0 --group=0 --numeric-owner \
    --directory="${STAGING_DIR}" \
    --file="${DIST_DIR}/${PKG_NAME}.tar.gz" .

# Генеруємо контрольну суму SHA-256 для верифікації дистрибутива
(cd "${DIST_DIR}" && sha256sum "${PKG_NAME}.tar.gz" > "${PKG_NAME}.tar.gz.sha256")

echo "=== Пакування успішно завершено ==="
echo "Пакет: ${DIST_DIR}/${PKG_NAME}.tar.gz"
cat "${DIST_DIR}/${PKG_NAME}.tar.gz.sha256"
