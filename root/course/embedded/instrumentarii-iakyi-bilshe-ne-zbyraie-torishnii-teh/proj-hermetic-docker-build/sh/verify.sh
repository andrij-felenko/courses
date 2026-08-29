#!/usr/bin/env bash
# Перевірка детермінізму: дві незалежні збірки того самого коміту в різних
# тимчасових каталогах мусять дати побайтово однакові релізні файли.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

die() {
    printf 'verify.sh: %s\n' "$*" >&2
    exit 1
}

git -C "${REPO_ROOT}" rev-parse --git-dir >/dev/null 2>&1 \
    || die "потрібне git-дерево: перевіряємо відтворюваність конкретного коміту"
[ -z "$(git -C "${REPO_ROOT}" status --porcelain)" ] \
    || die "робоче дерево брудне: перевіряти нема чого, поки зміни не закомічені"

EPOCH="$(git -C "${REPO_ROOT}" log -1 --format=%ct)"
COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"

DIR1="$(mktemp -d)"
DIR2="$(mktemp -d)"
KEEP=0

cleanup() {
    if [ "${KEEP}" -eq 0 ]; then
        rm -rf "${DIR1}" "${DIR2}"
    else
        printf 'verify.sh: каталоги збірок лишено для розбору:\n  %s\n  %s\n' "${DIR1}" "${DIR2}" >&2
    fi
}
trap cleanup EXIT

# git archive віддає рівно закомічений стан: ні залишкових об'єктників,
# ні .git, ні редакторського сміття — два каталоги стартують однаково.
export_tree() {
    git -C "${REPO_ROOT}" archive --format=tar HEAD | tar -x -C "$1"
}

# Обом збіркам явно передаємо ті самі час і коміт: у розпакованому дереві
# git-каталогу немає, і build.sh взяти їх нізвідки.
run_build() {
    local dir="$1"
    SOURCE_DATE_EPOCH="${EPOCH}" FW_GIT_COMMIT="${COMMIT}" "${dir}/sh/build.sh" >/dev/null \
        || die "збірка в ${dir} впала"
    (cd "${dir}/build" && sha256sum firmware.elf firmware.bin)
}

printf 'verify.sh: коміт %s, epoch %s\n' "${COMMIT:0:12}" "${EPOCH}"

export_tree "${DIR1}"
export_tree "${DIR2}"

printf 'verify.sh: збірка 1 із 2...\n'
HASHES1="$(run_build "${DIR1}")"
printf 'verify.sh: збірка 2 із 2...\n'
HASHES2="$(run_build "${DIR2}")"

if [ "${HASHES1}" = "${HASHES2}" ]; then
    printf 'УСПІХ: збірки побайтово тотожні\n%s\n' "${HASHES1}"
    exit 0
fi

KEEP=1
printf 'ПОМИЛКА: збірки розійшлися\n--- збірка 1 ---\n%s\n--- збірка 2 ---\n%s\n' \
    "${HASHES1}" "${HASHES2}" >&2
printf 'Джерело розбіжності шукають так:\n  diffoscope %s/build/firmware.elf %s/build/firmware.elf\n' \
    "${DIR1}" "${DIR2}" >&2
exit 1
