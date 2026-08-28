#!/usr/bin/env bash
set -eo pipefail

SCENARIO_DIR="./scenarios"
LOG_DIR="./test_logs"
mkdir -p "$LOG_DIR"

PASSED_TESTS=0
FAILED_TESTS=0

echo "=== Запуск матриці регресійних стрес-тестів SITL ==="

for scenario_file in "$SCENARIO_DIR"/*.json; do
    test_name=$(basename "$scenario_file" .json)
    echo "--- Виконання тесту: $test_name ---"
    
    # 1. Старт SITL PX4 у фоні
    /px4/bin/px4 -d /px4/etc > "$LOG_DIR/${test_name}_px4.log" 2>&1 &
    PX4_PID=$!
    
    # 2. Старт Gazebo physics engine
    gz-server -r -s libgazebo_sitl.so > "$LOG_DIR/${test_name}_gz.log" 2>&1 &
    GZ_PID=$!
    
    # 3. Старт проксі-інжектора з таймаутом 60 секунд
    if ./injector_bin --scenario "$scenario_file" --timeout 60; then
        echo "PASS: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "FAIL: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    # Зупинка процесів
    kill -9 $PX4_PID $GZ_PID 2>/dev/null || true
    wait $PX4_PID $GZ_PID 2>/dev/null || true
    sleep 1
done

echo "=== Результати тестування: Пройдено: $PASSED_TESTS, Провалено: $FAILED_TESTS ==="
if [ "$FAILED_TESTS" -gt 0 ]; then
    exit 1
fi
exit 0
