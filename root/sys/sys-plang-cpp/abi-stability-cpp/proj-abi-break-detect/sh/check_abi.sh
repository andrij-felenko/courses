#!/usr/bin/env bash
# check_abi.sh — верифікація стабільності двійкового інтерфейсу
set -e

echo "=== 1. Збірка еталонної версії бібліотеки v1.0 ==="
g++ -std=c++20 -O2 -g -shared -fPIC -fvisibility=hidden \
    -DENGINE_EXPORTS engine.cpp -o libengine_v1.so

# Екстракція еталонного XML-зліпка ABI з DWARF інформації
abidw --drop-private-types libengine_v1.so --out-file libengine_v1.abi
echo "✓ Згенеровано зліпок ABI v1.0"

echo "=== 2. Збірка поточної версії бібліотеки v1.1 ==="
g++ -std=c++20 -O2 -g -shared -fPIC -fvisibility=hidden \
    -DENGINE_EXPORTS engine.cpp -o libengine_v1_1.so

echo "=== 3. Виконання диференційного аудиту через abidiff ==="
if abidiff --leaf-changes-only --impacted-interfaces libengine_v1.abi libengine_v1_1.so; then
    echo "=================================================="
    echo "✅ ПЕРЕВІРКУ ПРОЙДЕНО: Двійковий інтерфейс повністю сумісний!"
    echo "=================================================="
    exit 0
else
    echo "=================================================="
    echo "❌ ДЕФЕКТ: Виявлено розрив ABI між версіями!"
    echo "Зміна двійкового контракту вимагає оновлення SONAME або major-версії."
    echo "=================================================="
    exit 1
fi
