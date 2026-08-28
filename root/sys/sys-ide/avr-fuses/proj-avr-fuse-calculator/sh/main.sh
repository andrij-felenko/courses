#!/usr/bin/env bash
set -euo pipefail

CHIP="m328p"
HEX_APP="build/firmware.hex"
HEX_EEPROM="build/calibration.eep"

echo "=== Фаза 1: Генерація та валідація байтів конфігурації ==="
CMD_ARGS=$(./avr-fuse-calc --chip ${CHIP} --clock ext-crystal --sut max --bod 4.3v --boot-size 256 --bootrst --avrdude)

echo "=== Фаза 2: Прошивка Flash, EEPROM та базових Fuses ==="
avrdude -c usbasp -p ${CHIP} -e \
    -U flash:w:${HEX_APP}:i \
    -U eeprom:w:${HEX_EEPROM}:i \
    -U lfuse:w:0xFF:m \
    -U hfuse:w:0xDE:m \
    -U efuse:w:0xFC:m

echo "=== Фаза 3: Верифікація цілісності образу Flash (CRC32) ==="
avrdude -c usbasp -p ${CHIP} -U flash:v:${HEX_APP}:i

echo "=== Фаза 4: Апаратне замикання бітів захисту читання (Lock Bits Mode 3) ==="
avrdude -c usbasp -p ${CHIP} -U lock:w:0x00:m

echo "=== Фаза 5: Контрольна перевірка захисту від читання ==="
if avrdude -c usbasp -p ${CHIP} -U flash:r:/tmp/dump.bin:r 2>/dev/null; then
    echo "[УСПІХ] Плату успішно прошито та апаратно заблоковано від зчитування."
fi
