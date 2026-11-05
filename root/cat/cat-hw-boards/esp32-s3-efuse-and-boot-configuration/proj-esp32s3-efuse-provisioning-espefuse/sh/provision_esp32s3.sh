#!/usr/bin/env bash

set -euo pipefail

PORT=${1:-/dev/ttyUSB0}
DRY_RUN=${2:-true}

# За замовчуванням espefuse.py показує плановані зміни і вимагає ввести "BURN"
# для підтвердження. Це і є безпечний режим "dry-run" для перевірки.
# Щоб застосувати зміни незворотно, необхідно передати прапорець --do-not-confirm.
CONFIRM_FLAG=""
if [ "$DRY_RUN" = "false" ]; then
    CONFIRM_FLAG="--do-not-confirm"
    echo "УВАГА: Виконується НЕЗВОРОТНИЙ запис у eFuse!"
else
    echo "Режим Dry-Run: зміни будуть лише показані для перевірки, запису не відбудеться."
fi

ESPEFUSE_CMD="espefuse.py -p $PORT"

echo "1. Зчитування поточного стану eFuse..."
$ESPEFUSE_CMD summary

echo "2. Генерація ключів (якщо відсутні)..."
if [ ! -f "flash_enc_key.bin" ]; then
    espsecure.py generate_flash_encryption_key flash_enc_key.bin
    echo "Згенеровано ключ Flash Encryption: flash_enc_key.bin"
fi

if [ ! -f "secure_boot_key.pem" ]; then
    espsecure.py generate_signing_key secure_boot_key.pem
    echo "Згенеровано ключ Secure Boot V2: secure_boot_key.pem"
fi

echo "3. Запікання ключа Flash Encryption (BLOCK_KEY0)..."
$ESPEFUSE_CMD $CONFIRM_FLAG burn_key BLOCK_KEY0 flash_enc_key.bin XTS_AES_128_KEY

echo "4. Запікання ключа Secure Boot (BLOCK_KEY1)..."
$ESPEFUSE_CMD $CONFIRM_FLAG burn_key BLOCK_KEY1 secure_boot_key.pem SECURE_BOOT_DIGEST0

echo "5. Активація захисних механізмів..."
# Увімкнення Flash Encryption
$ESPEFUSE_CMD $CONFIRM_FLAG burn_efuse FLASH_CRYPT_CNT 127
$ESPEFUSE_CMD $CONFIRM_FLAG burn_efuse FLASH_CRYPT_CONFIG 0xF

# Увімкнення Secure Boot V2
$ESPEFUSE_CMD $CONFIRM_FLAG burn_efuse SECURE_BOOT_EN 1

echo "6. Встановлення бітів блокування (RD_DIS, WR_DIS)..."
# Заборона зчитування ключів ззовні та з ПЗ (RD_DIS)
$ESPEFUSE_CMD $CONFIRM_FLAG read_protect_efuse BLOCK_KEY0
$ESPEFUSE_CMD $CONFIRM_FLAG read_protect_efuse BLOCK_KEY1

# Заборона перезапису конфігурацій (WR_DIS)
$ESPEFUSE_CMD $CONFIRM_FLAG write_protect_efuse FLASH_CRYPT_CNT
$ESPEFUSE_CMD $CONFIRM_FLAG write_protect_efuse SECURE_BOOT_EN

echo "Операції провіжинінгу завершено."
