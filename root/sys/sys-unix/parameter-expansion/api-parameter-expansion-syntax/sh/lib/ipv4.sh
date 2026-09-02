#!/usr/bin/env bash
# Валідація IPv4 без regex, без grep і без підпроцесів: рядок ітеративно
# вкорочується обрізанням ${ip%%.*} (голова) та ${ip#*.} (хвіст).

# 0 — адреса валідна, 1 — ні.
validate_ipv4_address() {
    local ip=$1
    local octet next_ip
    local octet_count=0

    [[ -n $ip ]] || return 1

    while [[ -n $ip ]]; do
        octet=${ip%%.*}    # перший октет до крапки
        next_ip=${ip#*.}   # залишок після першої крапки

        # Лише цифри, від одного до трьох знаків.
        [[ -n $octet ]] || return 1
        [[ -z ${octet//[0-9]/} ]] || return 1
        (( ${#octet} <= 3 )) || return 1

        # Провідний нуль забороняємо: "010" історично читали як вісімкове,
        # і "10.0.0.011" означало б різні адреси для різних розбирачів.
        [[ ${#octet} -eq 1 || ${octet:0:1} != 0 ]] || return 1

        (( octet <= 255 )) || return 1

        octet_count=$(( octet_count + 1 ))
        (( octet_count <= 4 )) || return 1

        if [[ $ip == "$next_ip" ]]; then
            # Крапок більше немає — це був останній октет.
            ip=""
        else
            ip=$next_ip
            # Хвостова крапка ("1.2.3.4.") лишає порожній залишок.
            [[ -n $ip ]] || return 1
        fi
    done

    (( octet_count == 4 ))
}

# Розбір CIDR-запису "10.0.0.0/24": адреса + довжина префікса.
validate_ipv4_cidr() {
    local cidr=$1
    local addr=${cidr%%/*}
    local bits=${cidr#*/}

    [[ $cidr == */* ]] || return 1
    validate_ipv4_address "$addr" || return 1
    [[ -n $bits && -z ${bits//[0-9]/} ]] || return 1
    (( ${#bits} <= 2 )) || return 1
    (( bits <= 32 ))
}
