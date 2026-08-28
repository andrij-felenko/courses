#!/usr/bin/env bash
set -euo pipefail

echo "Executing heavy shell initialization..."
sleep 3

# Сповіщаємо systemd через стандартну утиліту
if command -v systemd-notify &>/dev/null; then
    systemd-notify --ready --status="Shell script initialized successfully."
else
    # Резервний варіант через socat, якщо systemd-notify відсутній
    if [ -n "${NOTIFY_SOCKET:-}" ]; then
        if [[ "$NOTIFY_SOCKET" == @* ]]; then
            TARGET="abstract-sendto:${NOTIFY_SOCKET:1}"
        else
            TARGET="unix-sendto:$NOTIFY_SOCKET"
        fi
        echo -e "READY=1\nSTATUS=Socat fallback ready." | socat -u STDIN "$TARGET"
    fi
fi

# Головний цикл скрипта з надсиланням watchdog
while true; do
    sleep 10
    if command -v systemd-notify &>/dev/null; then
        systemd-notify --watchdog
    fi
done
