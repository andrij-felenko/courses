#!/bin/bash
# module-setup.sh для модуля 95keycheck у dracut

# Перевірка, чи слід включати модуль у завантажувальний образ
check() {
    # Включати модуль лише якщо бинарник initramfs-keycheck присутній у системі
    type initramfs-keycheck >/dev/null 2>&1 || return 1
    return 0
}

# Визначення залежностей від інших модулів dracut
depends() {
    echo "udev-rules"
    return 0
}

# Встановлення файлів та скриптів виконання у cpio-архів
install() {
    # Скопіювати бінарний файл перевірки (dracut автоматично виконає ldd і копіює бібліотеки)
    inst_multiple initramfs-keycheck

    # Зареєструвати скрипт виконання у черзі initqueue перед монтуванням
    inst_hook initqueue/online 50 "$moddir/verify-key.sh"
}
