#!/usr/bin/env bash
# Хостова обгортка герметичної збірки: усе, що вміє хост, — передати в контейнер
# час коміту й свій UID. Компіляція йде без мережі, у зафіксованому образі.
set -euo pipefail

IMAGE="embedded-builder:v1.4.2"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
DOCKERFILE="${REPO_ROOT}/docker/Dockerfile.builder"

die() {
    printf 'build.sh: %s\n' "$*" >&2
    exit 1
}

command -v docker >/dev/null 2>&1 || die "docker не знайдено у PATH"
[ -f "${DOCKERFILE}" ] || die "немає ${DOCKERFILE}"

# 1. Час і коміт. У чистому експорті дерева (так робить verify.sh) каталогу
#    .git немає — тоді обидва значення мусять прийти ззовні, інакше збірка
#    мовчки взяла б дефолт і перестала бути відтворюваною.
if git -C "${REPO_ROOT}" rev-parse --git-dir >/dev/null 2>&1; then
    if [ -n "$(git -C "${REPO_ROOT}" status --porcelain)" ]; then
        die "робоче дерево брудне: закоміть або сховай зміни перед релізною збіркою"
    fi
    : "${SOURCE_DATE_EPOCH:=$(git -C "${REPO_ROOT}" log -1 --format=%ct)}"
    : "${FW_GIT_COMMIT:=$(git -C "${REPO_ROOT}" rev-parse HEAD)}"
else
    [ -n "${SOURCE_DATE_EPOCH:-}" ] || die "поза git-деревом SOURCE_DATE_EPOCH задають явно"
    [ -n "${FW_GIT_COMMIT:-}" ] || die "поза git-деревом FW_GIT_COMMIT задають явно"
fi

[ "${#FW_GIT_COMMIT}" -eq 40 ] || die "FW_GIT_COMMIT має бути повним SHA-1 із 40 символів"
export SOURCE_DATE_EPOCH FW_GIT_COMMIT

# 2. Образ будуємо лише якщо його ще немає локально. Це ЄДИНИЙ крок, якому
#    потрібна мережа, і саме тому він відділений від компіляції.
if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    printf 'build.sh: складаємо образ %s (потрібна мережа)\n' "${IMAGE}"
    docker build -t "${IMAGE}" -f "${DOCKERFILE}" "${REPO_ROOT}/docker"
fi

printf '=== герметична збірка: epoch=%s commit=%s ===\n' \
    "${SOURCE_DATE_EPOCH}" "${FW_GIT_COMMIT:0:12}"

# 3. Компіляція. --network none відрізає будь-яке тихе довантаження з мережі,
#    --user підставляє UID/GID хоста, щоб build/ не дістався root'ові.
docker run --rm \
    --network none \
    --user "$(id -u):$(id -g)" \
    --env SOURCE_DATE_EPOCH \
    --env FW_GIT_COMMIT \
    --volume "${REPO_ROOT}:/workspace" \
    --workdir /workspace \
    "${IMAGE}" \
    'make -f make/Makefile clean && make -f make/Makefile -j"$(nproc)"'

printf '=== збірку завершено, хеші релізних файлів ===\n'
cat "${REPO_ROOT}/build/firmware.sha256"
