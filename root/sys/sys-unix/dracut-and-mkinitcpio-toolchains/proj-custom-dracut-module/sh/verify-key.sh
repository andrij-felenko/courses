#!/bin/sh
# verify-key.sh — виконується в initramfs під час події initqueue

type getarg >/dev/null 2>&1 || . /lib/dracut-lib.sh

# Зчитати параметр з командного рядка ядра (наприклад, keycheck.path=/key.bin)
KEY_PATH=$(getarg keycheck.path=)

if [ -n "$KEY_PATH" ]; then
    echo "dracut: Starting token verification at $KEY_PATH..."
    if ! initramfs-keycheck "$KEY_PATH"; then
        echo "dracut: FATAL key verification failed! Halting boot."
        warn "Token validation failure: $KEY_PATH"
        emergency_shell
    fi
fi
