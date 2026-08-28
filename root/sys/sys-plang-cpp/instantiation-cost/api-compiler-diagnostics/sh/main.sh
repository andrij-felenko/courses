#!/usr/bin/env bash
# Скрипт автоматичної перевірки відхилень часу компіляції
set -euo pipefail

BUILD_DIR="build_ci"
REPORT_FILE="time_report.txt"

# 1. Збірка з трасуванням
cmake -B "${BUILD_DIR}" -G Ninja -DCMAKE_CXX_FLAGS="-ftime-trace"
clang-build-analyzer --start "${BUILD_DIR}"
ninja -C "${BUILD_DIR}"
clang-build-analyzer --stop "${BUILD_DIR}" "${REPORT_FILE}"

# 2. Перевірка наявності важких інстанціацій
if grep -q "Expensive Templates" "${REPORT_FILE}"; then
    echo "[CI WARNING] Found heavy template instantiations in build report!"
    head -n 30 "${REPORT_FILE}"
fi
