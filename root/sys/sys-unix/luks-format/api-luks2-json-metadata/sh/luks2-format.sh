#!/usr/bin/env bash
# Форматування блокового пристрою у LUKS2: Argon2id, AES-256-XTS, сектор 4 КіБ.
# Після форматування друкує бінарний заголовок і сирий документ JSON метаданих.
#
# ⚠ Операція незворотна: старий заголовок затирається, а без нього попередні
# дані не розшифрує вже ніхто.
set -euo pipefail

CIPHER=${CIPHER:-aes-xts-plain64}
KEY_SIZE=${KEY_SIZE:-512}              # 512 бітів XTS = два незалежні 256-бітні ключі
HASH=${HASH:-sha256}
PBKDF=${PBKDF:-argon2id}
PBKDF_MEMORY=${PBKDF_MEMORY:-1048576}  # КіБ матриці Argon2, тобто 1 ГіБ
PBKDF_PARALLEL=${PBKDF_PARALLEL:-4}
ITER_TIME=${ITER_TIME:-4000}           # мс цільової затримки розтягування пароля
SECTOR_SIZE=${SECTOR_SIZE:-4096}

die() {
    printf 'luks2-format: %s\n' "$1" >&2
    exit 1
}

need_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "немає утиліти $1 (пакет $2)"
}

usage() {
    cat <<'USAGE'
вжиток:  luks2-format.sh <пристрій> [мітка] [підсистема]
приклад: luks2-format.sh /dev/nvme0n1p3 secure_storage production
змінні:  CIPHER KEY_SIZE HASH PBKDF PBKDF_MEMORY PBKDF_PARALLEL ITER_TIME SECTOR_SIZE
USAGE
}

# Пам'ять під Argon2 потрібна не лише зараз, а й на КОЖНОМУ відкритті тома:
# вузол із меншою вільною пам'яттю або піде у своп, або не відкриє том узагалі.
check_memory() {
    local available
    available=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
    [ -n "$available" ] || return 0
    if [ "$available" -lt "$PBKDF_MEMORY" ]; then
        die "вільно $available КіБ, а Argon2 просить $PBKDF_MEMORY КіБ — знизь PBKDF_MEMORY"
    fi
    if [ "$available" -lt $((PBKDF_MEMORY * 2)) ]; then
        printf 'увага: запас пам'"'"'яті малий (%s КіБ) — на слабшому вузлі том не відкриється\n' \
            "$available" >&2
    fi
}

# Форматувати змонтований чи вже відображений пристрій — це знищити чужі дані
# просто зараз, під працюючою файловою системою.
check_free() {
    local device=$1 mountpoint name holders
    mountpoint=$(lsblk --noheadings --output MOUNTPOINT "$device" | tr -d ' \n')
    [ -z "$mountpoint" ] || die "$device змонтовано в $mountpoint — спершу відмонтуй"
    name=$(basename "$(readlink -f "$device")")
    holders=$(ls -A "/sys/class/block/$name/holders" 2>/dev/null || true)
    [ -z "$holders" ] || die "поверх $device уже стоїть відображення: $holders"
}

confirm() {
    local device=$1 kind answer
    kind=$(blkid --probe --output value --match-tag TYPE "$device" 2>/dev/null || true)
    printf 'пристрій:      %s (%s)\n' "$device" "$(lsblk -dno SIZE "$device" | tr -d ' ')"
    printf 'наявний вміст: %s\n' "${kind:-невідомий, схоже порожній}"
    printf 'шифр:          %s, ключ %s бітів, сектор %s\n' "$CIPHER" "$KEY_SIZE" "$SECTOR_SIZE"
    printf 'KDF:           %s, %s КіБ, %s потоків, %s мс\n' \
        "$PBKDF" "$PBKDF_MEMORY" "$PBKDF_PARALLEL" "$ITER_TIME"
    read -r -p 'усе на пристрої буде втрачено; надрукуй ЗНИЩИТИ: ' answer
    [ "$answer" = "ЗНИЩИТИ" ] || die "скасовано"
}

main() {
    local device=${1:-} label=${2:-secure_storage} subsystem=${3:-production}

    [ -n "$device" ] || { usage; exit 2; }
    [ "$(id -u)" -eq 0 ] || die "потрібні права root"
    need_cmd cryptsetup cryptsetup
    need_cmd lsblk util-linux
    need_cmd blkid util-linux

    [ -b "$device" ] || die "$device не є блоковим пристроєм"
    # Мітка й підсистема лежать у полях char[48] дескриптора — з термінатором.
    [ "${#label}" -le 47 ] || die "мітка довша за 47 символів у заголовок не влізе"
    [ "${#subsystem}" -le 47 ] || die "назва підсистеми довша за 47 символів не влізе"

    check_memory
    check_free "$device"
    confirm "$device"

    cryptsetup luksFormat \
        --type luks2 \
        --cipher "$CIPHER" \
        --key-size "$KEY_SIZE" \
        --hash "$HASH" \
        --pbkdf "$PBKDF" \
        --pbkdf-memory "$PBKDF_MEMORY" \
        --pbkdf-parallel "$PBKDF_PARALLEL" \
        --iter-time "$ITER_TIME" \
        --sector-size "$SECTOR_SIZE" \
        --label "$label" \
        --subsystem "$subsystem" \
        "$device"

    printf '\nзаголовок:\n'
    cryptsetup luksDump "$device"

    if command -v jq >/dev/null 2>&1; then
        printf '\nметадані JSON:\n'
        cryptsetup luksDump --dump-json-metadata "$device" | jq .
    fi

    printf '\nнаступний крок — схов заголовка (без нього биті перші сектори = втрата даних):\n'
    printf '  cryptsetup luksHeaderBackup %s --header-backup-file <файл>\n' "$device"
}

main "$@"
