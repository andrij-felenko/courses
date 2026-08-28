#!/usr/bin/env bash
# bisect_validator.sh — скрипт автоматичної локалізації регресії

set -e

# 1. Швидка збірка проєкту
cmake --build build --target test_suite --parallel $(nproc) > /dev/null 2>&1

# 2. Запуск цільового тесту під AddressSanitizer
export ASAN_OPTIONS="abort_on_error=1:detect_leaks=1"
./build/bin/test_suite --gtest_filter=PerformanceRegressionTest.* > /dev/null 2>&1

# Код виходу 0 — коміт хороший, код > 0 — коміт зламано
exit $?
