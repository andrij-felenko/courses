#!/usr/bin/env bash
# Мережеве розблокування тома LUKS2 (NBDE) через Clevis: прив'язка до сервера
# Tang, порогова політика SSS «t із n», перелік пінів і пробне розблокування.
#
# Запускати з правами root на закритому томі. Пароль наявної шпарини питає
# сама clevis: без нього новий секрет нікуди покласти.
set -euo pipefail

die() {
    printf 'clevis-nbde: %s\n' "$1" >&2
    exit 1
}

need_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "немає утиліти $1 (пакет $2)"
}

usage() {
    cat <<'USAGE'
вжиток:
  clevis-nbde-bind.sh bind   <пристрій> <поріг> <url-tang>…  прив'язка (поріг 1 і один url = чистий tang)
  clevis-nbde-bind.sh list   <пристрій>                      зареєстровані піни
  clevis-nbde-bind.sh test   <пристрій>                      пробне розблокування й закриття
  clevis-nbde-bind.sh unbind <пристрій> <шпарина>            зняття прив'язки
приклад:
  clevis-nbde-bind.sh bind /dev/nvme0n1p3 2 http://tang1:8888 http://tang2:8888 http://tang3:8888
USAGE
}

require_luks2() {
    local device=$1
    [ -e "$device" ] || die "немає пристрою $device"
    cryptsetup isLuks --type luks2 "$device" ||
        die "$device не є томом LUKS2 (для LUKS1 спершу cryptsetup convert)"
}

# Відбиток thp рахуємо з підписаної об'яви сервера й кладемо в токен: він
# прив'язує клієнта до КЛЮЧА сервера, а не до адреси, яку легко підмінити.
tang_thumbprint() {
    local url=$1 advertisement
    advertisement=$(curl --fail --silent --show-error --max-time 10 "$url/adv") ||
        die "сервер $url не віддав /adv (мережа, порт або сам tangd)"
    printf '%s' "$advertisement" |
        jose fmt -j- -g payload -y -o- |
        jose jwk use -i- -r -u verify -o- |
        jose jwk thp -i- |
        head -n 1
}

bind_device() {
    local device=$1 threshold=$2
    shift 2
    local -a urls=("$@")
    local url thp pins config

    [ "${#urls[@]}" -ge 1 ] || die "не задано жодного сервера Tang"
    [[ $threshold =~ ^[0-9]+$ ]] || die "поріг мусить бути числом"
    [ "$threshold" -ge 1 ] || die "поріг менший за 1 не має сенсу"
    [ "$threshold" -le "${#urls[@]}" ] ||
        die "поріг $threshold більший за кількість серверів ${#urls[@]} — том не відкриється ніколи"

    pins='[]'
    for url in "${urls[@]}"; do
        thp=$(tang_thumbprint "$url")
        [ -n "$thp" ] || die "об'ява сервера $url не містить ключа підпису"
        printf '  %s → thp %s\n' "$url" "$thp"
        pins=$(jq -c --arg url "$url" --arg thp "$thp" \
            '. + [{url: $url, thp: $thp}]' <<<"$pins")
    done

    if [ "${#urls[@]}" -eq 1 ] && [ "$threshold" -eq 1 ]; then
        # Один сервер — прямий пін tang, без зайвого шару розділення секрету.
        config=$(jq -c '.[0]' <<<"$pins")
        clevis luks bind -d "$device" tang "$config"
    else
        config=$(jq -cn --argjson t "$threshold" --argjson pins "$pins" \
            '{t: $t, pins: {tang: $pins}}')
        clevis luks bind -d "$device" sss "$config"
    fi
}

list_pins() {
    local device=$1
    clevis luks list -d "$device" ||
        die "у томі $device немає жодного токена clevis"
}

# Пробне розблокування ловить недосяжний Tang ТУТ, а не в initramfs на
# перезавантаженні, коли лишається хіба аварійна оболонка dracut.
test_unlock() {
    local device=$1
    local name="clevis-probe-$$"

    clevis luks unlock -d "$device" -n "$name" ||
        die "розблокування не вдалося: недосяжний сервер, змінені PCR або знятий пін"
    printf 'том відкрито як /dev/mapper/%s — закриваю\n' "$name"
    cryptsetup close "$name"
}

unbind_slot() {
    local device=$1 slot=$2
    [[ $slot =~ ^[0-9]+$ ]] || die "номер шпарини мусить бути числом"
    clevis luks unbind -d "$device" -s "$slot"
}

main() {
    local command=${1:-}

    [ -n "$command" ] || { usage; exit 2; }
    shift
    [ "$(id -u)" -eq 0 ] || die "потрібні права root"
    need_cmd cryptsetup cryptsetup
    need_cmd clevis clevis-luks
    need_cmd jq jq

    case $command in
    bind)
        [ "$#" -ge 3 ] || { usage; exit 2; }
        need_cmd curl curl
        need_cmd jose jose
        require_luks2 "$1"
        bind_device "$@"
        list_pins "$1"
        ;;
    list)
        [ "$#" -eq 1 ] || { usage; exit 2; }
        require_luks2 "$1"
        list_pins "$1"
        ;;
    test)
        [ "$#" -eq 1 ] || { usage; exit 2; }
        require_luks2 "$1"
        test_unlock "$1"
        ;;
    unbind)
        [ "$#" -eq 2 ] || { usage; exit 2; }
        require_luks2 "$1"
        unbind_slot "$1" "$2"
        list_pins "$1"
        ;;
    *)
        usage
        exit 2
        ;;
    esac
}

main "$@"
