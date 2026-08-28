#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="/tmp/git_submodule_test_env"
rm -rf "${TEST_DIR}"
mkdir -p "${TEST_DIR}"

# 1. Створення фіктивних зовнішніх репозиторіїв
mkdir -p "${TEST_DIR}/remote/lib_a"
git -C "${TEST_DIR}/remote/lib_a" init
echo "/* SPDX-License-Identifier: MIT */" > "${TEST_DIR}/remote/lib_a/lib_a.c"
git -C "${TEST_DIR}/remote/lib_a" add lib_a.c
git -C "${TEST_DIR}/remote/lib_a" commit -m "Initial commit for lib_a"

mkdir -p "${TEST_DIR}/remote/lib_b"
git -C "${TEST_DIR}/remote/lib_b" init
echo "/* SPDX-License-Identifier: BSD-3-Clause */" > "${TEST_DIR}/remote/lib_b/lib_b.c"
git -C "${TEST_DIR}/remote/lib_b" add lib_b.c
git -C "${TEST_DIR}/remote/lib_b" commit -m "Initial commit for lib_b"

mkdir -p "${TEST_DIR}/remote/lib_c"
git -C "${TEST_DIR}/remote/lib_c" init
echo "/* SPDX-License-Identifier: GPL-3.0-only */" > "${TEST_DIR}/remote/lib_c/lib_c.c"
git -C "${TEST_DIR}/remote/lib_c" add lib_c.c
git -C "${TEST_DIR}/remote/lib_c" commit -m "Initial commit for lib_c"

# 2. Створення батьківського репозиторію та додавання підмодулів
mkdir -p "${TEST_DIR}/main_project"
git -C "${TEST_DIR}/main_project" init
git -C "${TEST_DIR}/main_project" submodule add "../remote/lib_a" libs/lib_a
git -C "${TEST_DIR}/main_project" submodule add "../remote/lib_b" libs/lib_b
git -C "${TEST_DIR}/main_project" submodule add "http://insecure-host.internal/lib_c.git" libs/lib_c
git -C "${TEST_DIR}/main_project" commit -m "Add submodules A, B, C"

# 3. Симуляція Commit Drift у lib_b
echo "/* New feature in lib_b */" >> "${TEST_DIR}/main_project/libs/lib_b/lib_b.c"
git -C "${TEST_DIR}/main_project/libs/lib_b" commit -am "Update lib_b locally"

# 4. Компіляція та запуск аудитора
gcc -O2 -std=c99 -Wall -Wextra submodule_tree_auditor.c -o "${TEST_DIR}/auditor"
"${TEST_DIR}/auditor" "${TEST_DIR}/main_project" || true
