#!/usr/bin/env bash
# bisect_runner.sh — Автоматичний пошук дефекту між релізами апстриму
set -euo pipefail

OLD_STABLE_TAG="v3.5.0"
NEW_TARGET_TAG="v3.6.0"

echo "[*] Ініціалізація бісекції між стабільним ${OLD_STABLE_TAG} та цільовим ${NEW_TARGET_TAG}..."
git bisect start "${NEW_TARGET_TAG}" "${OLD_STABLE_TAG}"

# Автоматичний запуск тестового скрипта на кожній ітерації
git bisect run bash -c '
    # 1. Експорт шляхів до нашого ізольованого позадеревного модуля драйверів
    export ZEPHYR_MODULES="$(pwd)/modules/custom_drivers"
    
    # 2. Спроба збирання тестового бінарного артефакту
    if ! west build -b qemu_cortex_m3 tests/drivers/spi -p auto > /dev/null 2>&1; then
        # Код 125 сигналізує Git пропустити цей комміт, якщо апстрим зламаний іншими авторами
        exit 125
    fi
    
    # 3. Виконання інтеграційного тесту в емуляторі
    ninja -C build run_tests
'

echo "[*] Бісекцію завершено. Комміт апстриму, що спричинив регресію:"
git bisect log
git bisect reset
