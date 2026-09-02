#!/usr/bin/env bash
# Керування паролями тома LUKS2: додавання шпарини з явними параметрами KDF,
# зміна пароля в наявній шпарині, видалення й безумовне стирання шпарини.
#
# Останню шпарину зняти не дає: том без жодного ключа не відкриє вже ніхто.
set -euo pipefail

PBKDF=${PBKDF:-argon2id}
PBKDF_MEMORY=${PBKDF_MEMORY:-1048576}  # КіБ матриці Argon2
PBKDF_PARALLEL=${PBKDF_PARALLEL:-4}
ITER_TIME=${ITER_TIME:-4000}           # мс цільової затримки відкриття

die() {
    printf 'manage-keys: %s\n' "$1" >&2
    exit 1
}

need_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "немає утиліти $1 (пакет $2)"
}

usage() {
    cat <<'USAGE'
вжиток:
  manage-keys.sh list   <пристрій>
  manage-keys.sh add    <пристрій> [шпарина]   новий пароль у вільну шпарину
  manage-keys.sh change <пристрій> <шпарина>   заміна пароля в наявній шпарині
  manage-keys.sh remove <пристрій>             видалення шпарини за її паролем
  manage-keys.sh kill   <пристрій> <шпарина>   стирання шпарини без її пароля
змінні: PBKDF PBKDF_MEMORY PBKDF_PARALLEL ITER_TIME
USAGE
}

require_luks2() {
    local device=$1
    [ -e "$device" ] || die "немає пристрою $device"
    cryptsetup isLuks --type luks2 "$device" || die "$device не є томом LUKS2"
}

used_slots() {
    cryptsetup luksDump "$1" | sed -n 's/^[[:space:]]*\([0-9]\{1,\}\): luks2$/\1/p'
}

slot_used() {
    used_slots "$1" | grep -qx "$2"
}

count_keyslots() {
    used_slots "$1" | wc -l
}

require_slot_number() {
    [[ $1 =~ ^[0-9]+$ ]] || die "номер шпарини мусить бути числом"
    [ "$1" -le 31 ] || die "LUKS2 знає шпарини 0..31"
}

# Знімати останню шпарину — це знищити том: Master Key більше нізвідки взяти.
require_spare() {
    [ "$(count_keyslots "$1")" -ge 2 ] ||
        die "у томі одна шпарина — спершу додай другу (manage-keys.sh add)"
}

add_key() {
    local device=$1 slot=${2:-}
    local -a options=(
        --pbkdf "$PBKDF"
        --pbkdf-memory "$PBKDF_MEMORY"
        --pbkdf-parallel "$PBKDF_PARALLEL"
        --iter-time "$ITER_TIME"
    )

    if [ -n "$slot" ]; then
        require_slot_number "$slot"
        ! slot_used "$device" "$slot" || die "шпарина $slot уже зайнята"
        options+=(--key-slot "$slot")
    fi
    # Пароль НАЯВНОЇ шпарини питається першим: без нього Master Key не відновити.
    cryptsetup luksAddKey "${options[@]}" "$device"
}

change_key() {
    local device=$1 slot=$2
    require_slot_number "$slot"
    slot_used "$device" "$slot" || die "шпарина $slot порожня"
    cryptsetup luksChangeKey --key-slot "$slot" "$device"
}

remove_key() {
    local device=$1
    require_spare "$device"
    cryptsetup luksRemoveKey "$device"
}

kill_slot() {
    local device=$1 slot=$2 answer
    require_slot_number "$slot"
    slot_used "$device" "$slot" || die "шпарина $slot і так порожня"
    require_spare "$device"
    read -r -p "стерти шпарину $slot без її пароля? надрукуй ТАК: " answer
    [ "$answer" = "ТАК" ] || die "скасовано"
    # Смуги AFSplit зануляються, шпарина зникає з JSON, seqid росте на одиницю.
    cryptsetup luksKillSlot "$device" "$slot"
}

show() {
    local device=$1
    printf 'зайняті шпарини: %s\n' "$(used_slots "$device" | tr '\n' ' ')"
    cryptsetup luksDump "$device" | sed -n '/^Keyslots:/,/^Tokens:/p'
}

main() {
    local command=${1:-} device=${2:-}

    [ -n "$command" ] && [ -n "$device" ] || { usage; exit 2; }
    [ "$(id -u)" -eq 0 ] || die "потрібні права root"
    need_cmd cryptsetup cryptsetup
    require_luks2 "$device"

    case $command in
    list)   show "$device" ;;
    add)    add_key "$device" "${3:-}"; show "$device" ;;
    change) [ -n "${3:-}" ] || { usage; exit 2; }
            change_key "$device" "$3" ;;
    remove) remove_key "$device"; show "$device" ;;
    kill)   [ -n "${3:-}" ] || { usage; exit 2; }
            kill_slot "$device" "$3"; show "$device" ;;
    *)      usage; exit 2 ;;
    esac
}

main "$@"
