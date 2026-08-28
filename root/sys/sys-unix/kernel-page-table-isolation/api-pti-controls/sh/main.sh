#!/bin/sh
# Стан ізоляції таблиць сторінок ядра на цій машині.

vuln=/sys/devices/system/cpu/vulnerabilities/meltdown

if [ -r "$vuln" ]; then
    printf 'sysfs   : %s\n' "$(cat "$vuln")"
else
    printf 'sysfs   : файлу немає — ядро старше за 4.15\n'
fi

if grep -qw pti /proc/cpuinfo; then
    printf 'cpuinfo : прапорець pti є\n'
else
    printf 'cpuinfo : прапорця pti немає\n'
fi
grep -qw pcid /proc/cpuinfo && printf 'cpuinfo : pcid є — перемикання дешеве\n'

printf 'збірка  : %s\n' "$(zgrep -h -E '^CONFIG_(MITIGATION_)?PAGE_TABLE_ISOLATION=|^CONFIG_UNMAP_KERNEL_AT_EL0=' \
        /proc/config.gz "/boot/config-$(uname -r)" 2>/dev/null | head -1)"
printf 'cmdline : %s\n' "$(cat /proc/cmdline)"

printf 'журнал  :\n'
{ dmesg 2>/dev/null || journalctl -k -o cat 2>/dev/null; } |
    grep -i -e 'page tables isolation' -e 'page table isolation'
