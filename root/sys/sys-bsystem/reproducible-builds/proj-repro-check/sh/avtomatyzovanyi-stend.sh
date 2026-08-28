#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_A="/tmp/repro_env_alpha"
WORK_B="/tmp/repro_env_beta_other_path"

echo "=== 1. Ініціалізація ізольованих робочих середовищ ==="
rm -rf "$WORK_A" "$WORK_B"
mkdir -p "$WORK_A" "$WORK_B"

cp -r "$ROOT_DIR"/src "$ROOT_DIR"/Makefile "$WORK_A"/
cp -r "$ROOT_DIR"/src "$ROOT_DIR"/Makefile "$WORK_B"/

echo "=== 2. Запуск збірки 1 (Еталонне середовище Альфа) ==="
(
    cd "$WORK_A"
    export TZ="UTC+5"
    export LC_ALL="en_US.UTF-8"
    export umask=0022
    make clean
    make
)

echo "=== 3. Внесення мутацій та запуск збірки 2 (Середовище Бета) ==="
(
    cd "$WORK_B"
    export TZ="Asia/Tokyo"
    export LC_ALL="C.UTF-8"
    export umask=0002
    sleep 2
    make clean
    make
)

echo "=== 4. Порівняння криптографічних контрольних сум ==="
HASH_A=$(sha256sum "$WORK_A/bin/app" | awk '{print $1}')
HASH_B=$(sha256sum "$WORK_B/bin/app" | awk '{print $1}')

echo "SHA256 (Альфа): $HASH_A"
echo "SHA256 (Бета):  $HASH_B"

if [ "$HASH_A" = "$HASH_B" ]; then
    echo "УСПІХ: Отримано 100% побайтово ідентичний бінарний артефакт!"
    exit 0
else
    echo "ВІДХИЛЕННЯ: Артефакти різняться. Запуск діагностики розбіжностей..."
    diffoscope "$WORK_A/bin/app" "$WORK_B/bin/app" || true
    exit 1
fi
