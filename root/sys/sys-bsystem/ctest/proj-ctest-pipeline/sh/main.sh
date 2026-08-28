#!/usr/bin/env bash
set -euo pipefail

BUILD_DIR="build_ci"

# 1. Конфігурація з санітайзерами пам'яті
cmake -B "${BUILD_DIR}" -G Ninja \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DENABLE_ASAN=ON \
    -DBUILD_TESTING=ON

# 2. Паралельна компіляція бінарників
cmake --build "${BUILD_DIR}" --parallel "$(nproc)"

# 3. Налаштування опцій санітайзерів для автоматичного переривання при витоках
export ASAN_OPTIONS="detect_leaks=1:abort_on_error=1:halt_on_error=1"
export UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=1"

# 4. Виконання CTest з паралелізмом, лімітами та генерацією JUnit XML
ctest --test-dir "${BUILD_DIR}" \
    --parallel "$(nproc)" \
    --output-on-failure \
    --output-junit "${BUILD_DIR}/junit-report.xml" \
    --repeat until-pass:2

echo "Тестування завершено. Звіт збережено у ${BUILD_DIR}/junit-report.xml"
