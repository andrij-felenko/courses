#!/bin/sh
set -e

case "$1" in
    configure)
        # 1. Оновлення системного кешу динамічних бібліотек
        if [ -x "$(command -v ldconfig)" ]; then
            ldconfig
        fi

        # 2. Перезавантаження конфігурації та запуск сервісу systemd
        if [ -d /run/systemd/system ]; then
            systemctl --system daemon-reload >/dev/null 2>&1 || true
            systemctl enable --now telemetryd.service >/dev/null 2>&1 || true
        fi
        ;;
esac

exit 0
