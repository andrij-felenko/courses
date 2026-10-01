#!/usr/bin/env bash

# ==============================================================================
# flash_and_monitor.sh
# ------------------------------------------------------------------------------
# Сценарій автоматизації розробки для WeAct Mini Debugger (DAPLink / ST-Link V2.1).
# Виконує перевірку залежностей, зчитує конфігурацію, прошиває мікроконтролер
# за допомогою pyOCD, здійснює скидання (reset) та відкриває UART-термінал.
# ==============================================================================

set -euo pipefail

# Визначення шляху до файлу конфігурації (за замовчуванням config.env)
CONFIG_FILE="${1:-config.env}"

# 1. Завантаження конфігураційного файла
if [[ -f "$CONFIG_FILE" ]]; then
    echo "[INFO] Завантаження конфігурації з '$CONFIG_FILE'..."
    # shellcheck disable=SC1090
    source "$CONFIG_FILE"
else
    echo "[ERROR] Конфігураційний файл '$CONFIG_FILE' не знайдено!" >&2
    exit 1
fi

# Значення за замовчуванням, якщо параметри не задані в config.env
TARGET_MCU="${TARGET_MCU:-stm32f411ce}"
SWD_FREQUENCY="${SWD_FREQUENCY:-4000000}"
FIRMWARE_PATH="${FIRMWARE_PATH:-build/firmware.bin}"
PORT="${PORT:-/dev/ttyACM0}"
BAUD_RATE="${BAUD_RATE:-115200}"
SERIAL_TERMINAL="${SERIAL_TERMINAL:-picocom}"

# 2. Перевірка наявності необхідних CLI-інструментів
check_dependency() {
    local cmd="$1"
    if ! command -v "$cmd" &> /dev/null; then
        echo "[ERROR] Необхідна утиліта '$cmd' не встановлена або відсутня в PATH." >&2
        return 1
    fi
}

echo "[INFO] Перевірка системних залежностей..."
if ! check_dependency "pyocd"; then
    echo "[HINT] Встановіть pyOCD за допомогою: pip install pyocd" >&2
    exit 1
fi

if ! check_dependency "$SERIAL_TERMINAL"; then
    echo "[HINT] Встановіть термінал '$SERIAL_TERMINAL' або змініть SERIAL_TERMINAL у $CONFIG_FILE" >&2
    exit 1
fi

# 3. Перевірка існування бінарного файла прошивки
if [[ ! -f "$FIRMWARE_PATH" ]]; then
    echo "[ERROR] Файл прошивки '$FIRMWARE_PATH' не існує!" >&2
    echo "[HINT] Переконайся, що проєкт зкомпільовано і шлях у config.env вказано вірно." >&2
    exit 1
fi

# 4. Прошивка мікроконтролера через pyOCD та WeAct Mini Debugger
echo "----------------------------------------------------------------------"
echo "[INFO] Початок запису прошивки через pyOCD..."
echo "       Цільовий МК : $TARGET_MCU"
echo "       Частота SWD : $((SWD_FREQUENCY / 1000000)) МГц"
echo "       Файл        : $FIRMWARE_PATH"
echo "----------------------------------------------------------------------"

# Запуск запису flash-пам'яті
if pyocd flash --target "$TARGET_MCU" --frequency "$SWD_FREQUENCY" "$FIRMWARE_PATH"; then
    echo "[OK] Прошивку успішно записано у flash-пам'ять!"
else
    echo "[ERROR] Збій під час запису прошивки через pyOCD!" >&2
    echo "[HINT] Перевірте підключення WeAct Mini Debugger, SWD-кабелі та живлення плати." >&2
    exit 1
fi

# 5. Скидання (reset) мікроконтролера
echo "[INFO] Виконання системного скидання (reset) мікроконтролера..."
if pyocd reset --target "$TARGET_MCU" --method hw; then
    echo "[OK] Мікроконтролер успішно скинуто!"
else
    echo "[WARNING] Не вдалося виконати апаратне скидання, спроба програмного скидання..."
    pyocd reset --target "$TARGET_MCU" || echo "[WARNING] Скидання через pyOCD повернуло помилку."
fi

# 6. Запуск UART-термінала для моніторингу логів
echo "----------------------------------------------------------------------"
echo "[INFO] Підготовка до запуску UART-моніторингу..."
echo "       Порт     : $PORT"
echo "       Швидкість: $BAUD_RATE бод"
echo "       Термінал : $SERIAL_TERMINAL"
echo "----------------------------------------------------------------------"

if [[ ! -e "$PORT" ]]; then
    echo "[WARNING] Послідовний порт '$PORT' не виявлено в системі." >&2
    echo "[HINT] Перевірте підключення USB-UART адаптера WeAct Mini Debugger." >&2
    exit 1
fi

# Запуск вибраного UART-термінала
case "$SERIAL_TERMINAL" in
    picocom)
        exec picocom -b "$BAUD_RATE" "$PORT"
        ;;
    minicom)
        exec minicom -D "$PORT" -b "$BAUD_RATE"
        ;;
    screen)
        exec screen "$PORT" "$BAUD_RATE"
        ;;
    *)
        echo "[ERROR] Непідтримуваний термінал: '$SERIAL_TERMINAL'" >&2
        exit 1
        ;;
esac
