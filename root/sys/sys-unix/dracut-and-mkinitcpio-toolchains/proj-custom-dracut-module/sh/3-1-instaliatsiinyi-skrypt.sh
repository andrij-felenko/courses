#!/bin/bash
# /usr/lib/initcpio/install/keycheck — інсталяційний файл mkinitcpio

build() {
    # Додати бінарник перевірки (mkinitcpio відстежить залежні .so бібліотеки через ldd)
    add_binary "initramfs-keycheck"

    # Додати скрипт виконання в рантайм раннього простору користувача
    add_runscript
}

help() {
    cat <<HELPEOF
Цей хук додає перевірку апаратного токена ключа перед монтуванням кореня.
Вимагає налаштування параметра keycheck.path= в cmdline ядра.
HELPEOF
}
