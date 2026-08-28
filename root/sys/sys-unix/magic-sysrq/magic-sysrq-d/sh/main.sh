#!/bin/bash
# Скид буферів через /proc/sysrq-trigger.
# Маска тут нічого не забороняє — вона стосується лише клавіатури,
# тому перевіряємо її винятково щоб попередити адміністратора.

SYSRQ_MASK=$(cat /proc/sys/kernel/sysrq)

if [ "$SYSRQ_MASK" -eq 0 ]; then
    echo "Увага: клавіатурний SysRq вимкнено (маска = 0); через тригер команда все одно спрацює."
elif [ "$SYSRQ_MASK" -ne 1 ] && [ $(( SYSRQ_MASK & 16 )) -eq 0 ]; then
    echo "Увага: у масці $SYSRQ_MASK немає біта sync (16) — з клавіатури 's' не спрацює."
fi

echo "Скидання буферів..."
# Увага: потрібні права root!
echo s > /proc/sysrq-trigger
echo "Команду надіслано; на завершення скиду вкаже 'Emergency Sync complete' у dmesg."
