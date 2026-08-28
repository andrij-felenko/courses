// Готового дампера тут нема — і не треба: це цикл по 16 секторах Classic 1K.
// Автентифікація відкриває весь сектор, тож ключ подаємо раз на сектор.
static const uint8_t key_a[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

void dump_classic_1k(const uint8_t *uid, uint8_t uid_len) {
    char line[96];
    int  k;
    for (uint8_t sector = 0; sector < 16; sector++) {
        uint8_t trailer = sector * 4 + 3;              // трейлер = S · 4 + 3
        if (pcd_authenticate(PICC_CMD_MF_AUTH_KEY_A, trailer, key_a, uid, uid_len) != PICC_OK) {
            k = snprintf(line, sizeof line, "Сектор %u: ключ не підійшов\r\n", sector);
            HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);
            continue;                                  // не-заводський ключ — нормально
        }
        for (uint8_t local = 0; local < 4; local++) {
            uint8_t block = sector * 4 + local;        // наскрізний номер блока
            uint8_t buf[18], size = sizeof(buf);       // 16 даних + 2 CRC
            if (mifare_read(block, buf, &size) != PICC_OK) continue;
            k = snprintf(line, sizeof line, "%2u:", block);
            for (uint8_t i = 0; i < 16; i++)
                k += snprintf(line + k, sizeof line - k, " %02X", buf[i]);
            k += snprintf(line + k, sizeof line - k, "%s\r\n", local == 3 ? "  <- трейлер" : "");
            HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);
        }
    }
    picc_halt_a();
    pcd_stop_crypto1();                                // пара до останньої автентифікації
}
