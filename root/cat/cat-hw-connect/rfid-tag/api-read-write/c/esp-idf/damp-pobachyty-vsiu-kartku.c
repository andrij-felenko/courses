// Готового дампера тут нема — і не треба: це цикл по 16 секторах Classic 1K.
// Автентифікація відкриває весь сектор, тож ключ подаємо раз на сектор.
static const uint8_t key_a[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

void dump_classic_1k(const uint8_t *uid, uint8_t uid_len) {
    for (uint8_t sector = 0; sector < 16; sector++) {
        uint8_t trailer = sector * 4 + 3;              // трейлер = S · 4 + 3
        if (pcd_authenticate(PICC_CMD_MF_AUTH_KEY_A, trailer, key_a, uid, uid_len) != ESP_OK) {
            ESP_LOGW(TAG, "Сектор %u: ключ не підійшов", sector);
            continue;                                  // не-заводський ключ — нормально
        }
        for (uint8_t local = 0; local < 4; local++) {
            uint8_t block = sector * 4 + local;        // наскрізний номер блока
            uint8_t buf[18], size = sizeof(buf);       // 16 даних + 2 CRC
            if (mifare_read(block, buf, &size) != ESP_OK) continue;
            ESP_LOGI(TAG, "Сектор %u, блок %2u%s", sector, block, local == 3 ? "  ← трейлер" : "");
            ESP_LOG_BUFFER_HEX(TAG, buf, 16);
        }
    }
    picc_halt_a();
    pcd_stop_crypto1();                                // пара до останньої автентифікації
}
