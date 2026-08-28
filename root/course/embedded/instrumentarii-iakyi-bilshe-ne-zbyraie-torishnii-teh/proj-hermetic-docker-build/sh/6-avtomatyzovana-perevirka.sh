#!/usr/bin/env bash
set -euo pipefail

DIR1="/tmp/build_test_1"
DIR2="/tmp/build_test_2"

rm -rf "${DIR1}" "${DIR2}"
mkdir -p "${DIR1}" "${DIR2}"

cp -r . "${DIR1}"
cp -r . "${DIR2}"

echo "Запуск збірки 1..."
(cd "${DIR1}" && ./build.sh > /dev/null)
HASH1=$(sha256sum "${DIR1}/build/firmware.bin" | awk '{print $1}')

echo "Запуск збірки 2..."
(cd "${DIR2}" && ./build.sh > /dev/null)
HASH2=$(sha256sum "${DIR2}/build/firmware.bin" | awk '{print $1}')

rm -rf "${DIR1}" "${DIR2}"

if [ "${HASH1}" = "${HASH2}" ]; then
    echo "УСПІХ: Збірки бінарно ідентичні!"
    echo "SHA-256: ${HASH1}"
    exit 0
else
    echo "ПОМИЛКА: Виявлено розбіжність бінарників!"
    echo "Build 1: ${HASH1}"
    echo "Build 2: ${HASH2}"
    exit 1
fi
