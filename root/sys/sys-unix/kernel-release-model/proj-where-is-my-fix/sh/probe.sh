#!/bin/sh
# ~/probe.sh — один крок двійкового пошуку: зібрати, завантажити, подивитися.
# Коди виходу тут — інтерфейс до git bisect, а не «успіх/невдача» скрипта.
set -u

make olddefconfig >/dev/null 2>&1        || exit 125
make -j"$(nproc)" bzImage >/dev/null 2>&1 || exit 125

rm -f /tmp/console.log
timeout 180 qemu-system-x86_64 \
    -kernel arch/x86/boot/bzImage \
    -initrd "$HOME/repro-initramfs.cpio.gz" \
    -append 'console=ttyS0 panic=1' \
    -nographic -no-reboot >/tmp/console.log 2>&1

grep -q 'REPRO: OK'   /tmp/console.log && exit 0
grep -q 'REPRO: FAIL' /tmp/console.log && exit 1
exit 125
