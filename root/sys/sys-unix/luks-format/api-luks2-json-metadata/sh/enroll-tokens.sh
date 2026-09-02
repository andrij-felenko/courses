#!/usr/bin/env bash
# Прив'язка апаратних і аварійних токенів до тома LUKS2 через systemd-cryptenroll:
# TPM 2.0 (з PIN-кодом і без), FIDO2, смарткарта PKCS#11, ключ відновлення.
#
# Кожна прив'язка займає НОВУ шпарину, а наявний пароль питається інтерактивно.
set -euo pipefail

PCRS=${PCRS:-0+7}   # 0 — прошивка платформи, 7 — стан Secure Boot

die() {
    printf 'enroll-tokens: %s\n' "$1" >&2
    exit 1
}

need_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "немає утиліти $1 (пакет $2)"
}

usage() {
    cat <<'USAGE'
вжиток:
  enroll-tokens.sh list     <пристрій>
  enroll-tokens.sh tpm2     <пристрій> [pin]        прив'язка до PCR (типово 0+7)
  enroll-tokens.sh fido2    <пристрій>              апаратний ключ, дотик + PIN
  enroll-tokens.sh pkcs11   <пристрій> <uri>        смарткарта за RFC 7512
  enroll-tokens.sh recovery <пристрій>              аварійний ключ відновлення
  enroll-tokens.sh wipe     <пристрій> <різновид>   tpm2|fido2|pkcs11|recovery|password|empty
змінні: PCRS (типово 0+7)
USAGE
}

require_luks2() {
    local device=$1
    [ -e "$device" ] || die "немає пристрою $device"
    cryptsetup isLuks --type luks2 "$device" || die "$device не є томом LUKS2"
}

count_keyslots() {
    cryptsetup luksDump "$1" | grep -cE '^[[:space:]]+[0-9]+: luks2' || true
}

# Прив'язка до PCR злітає від першого ж оновлення прошивки чи Secure Boot.
# Якщо в томі одна шпарина, після такої події відкривати його буде нічим.
require_fallback() {
    local device=$1
    [ "$(count_keyslots "$device")" -ge 2 ] ||
        die "у томі одна шпарина: спершу заведи запасний пароль (luksAddKey) або recovery"
}

enroll_tpm2() {
    local device=$1 with_pin=${2:-}
    [ -e /dev/tpmrm0 ] || die "немає /dev/tpmrm0 — ядро не бачить TPM 2.0"
    require_fallback "$device"

    if [ "$with_pin" = "pin" ]; then
        systemd-cryptenroll --tpm2-device=auto --tpm2-pcrs="$PCRS" \
            --tpm2-with-pin=true "$device"
    elif [ -z "$with_pin" ]; then
        systemd-cryptenroll --tpm2-device=auto --tpm2-pcrs="$PCRS" "$device"
    else
        die "другим аргументом буває лише слово pin"
    fi
}

enroll_fido2() {
    local device=$1
    require_fallback "$device"
    systemd-cryptenroll --fido2-device=auto \
        --fido2-with-client-pin=true \
        --fido2-with-user-presence=true "$device"
}

enroll_pkcs11() {
    local device=$1 uri=$2
    case $uri in
    pkcs11:*) ;;
    *) die "URI мусить починатися з pkcs11: (RFC 7512)" ;;
    esac
    require_fallback "$device"
    systemd-cryptenroll --pkcs11-token-uri="$uri" "$device"
}

enroll_recovery() {
    # Ключ друкується один раз і ніде не зберігається — далі його носить людина.
    systemd-cryptenroll --recovery-key "$1"
}

wipe_binding() {
    local device=$1 kind=$2
    case $kind in
    tpm2|fido2|pkcs11|recovery|password|empty) ;;
    *) die "невідомий різновид прив'язки: $kind" ;;
    esac
    [ "$(count_keyslots "$device")" -ge 2 ] ||
        die "лишилася одна шпарина — знявши її, том не відкриє вже ніхто"
    systemd-cryptenroll --wipe-slot="$kind" "$device"
}

show() {
    local device=$1
    printf 'шпарин: %s\n' "$(count_keyslots "$device")"
    if command -v jq >/dev/null 2>&1; then
        printf 'токени:\n'
        cryptsetup luksDump --dump-json-metadata "$device" | jq '.tokens'
    else
        cryptsetup luksDump "$device" | sed -n '/^Tokens:/,/^Digests:/p'
    fi
}

main() {
    local command=${1:-} device=${2:-}

    [ -n "$command" ] && [ -n "$device" ] || { usage; exit 2; }
    [ "$(id -u)" -eq 0 ] || die "потрібні права root"
    need_cmd cryptsetup cryptsetup
    need_cmd systemd-cryptenroll systemd
    require_luks2 "$device"

    case $command in
    list)     show "$device" ;;
    tpm2)     enroll_tpm2 "$device" "${3:-}"; show "$device" ;;
    fido2)    enroll_fido2 "$device"; show "$device" ;;
    pkcs11)   [ -n "${3:-}" ] || { usage; exit 2; }
              enroll_pkcs11 "$device" "$3"; show "$device" ;;
    recovery) enroll_recovery "$device"; show "$device" ;;
    wipe)     [ -n "${3:-}" ] || { usage; exit 2; }
              wipe_binding "$device" "$3"; show "$device" ;;
    *)        usage; exit 2 ;;
    esac
}

main "$@"
