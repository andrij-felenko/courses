#!/bin/sh
set -e

# 1. Оновлення кешу завантажувача динамічних бібліотек
if [ -x "$(command -v ldconfig)" ]; then
    ldconfig
fi

# 2. Оновлення конфігурації systemd, якщо сервіс встановлюється у працюючій системі
if [ -d /run/systemd/system ]; then
    systemctl --system daemon-reload >/dev/null 2>&1 || true
fi

exit 0
