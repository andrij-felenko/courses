// Ті самі чотири кроки поверх нашого транспорту; причина невдачі їде в esp_err_t.
static const uint8_t key_a[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };  // заводський ключ

uint8_t block = 4;
uint8_t buf[18];                  // 16 байтів даних + 2 байти CRC — МУСИТЬ бути 18
uint8_t size = sizeof(buf);       // передаємо ЄМНІСТЬ буфера (18), не 16

// КРОК 2: довести знання ключа A саме цього сектора (команда чипа MFAuthent).
esp_err_t err = pcd_authenticate(PICC_CMD_MF_AUTH_KEY_A, block, key_a, uid, uid_len);
if (err != ESP_OK) {
    ESP_LOGE(TAG, "Автентифікація не вдалась: %s", esp_err_to_name(err));
    picc_halt_a();
    pcd_stop_crypto1();           // навіть після невдачі — опустити шифрування
    return;
}

// КРОК 3: сектор відкрито — читаємо 16 байтів блока
err = mifare_read(block, buf, &size);
if (err == ESP_OK) {
    ESP_LOGI(TAG, "Блок %u:", block);
    ESP_LOG_BUFFER_HEX(TAG, buf, 16);          // друкуємо ЛИШЕ 16, не 18
} else {
    ESP_LOGE(TAG, "Читання не вдалось: %s", esp_err_to_name(err));
}

picc_halt_a();                    // відпустити мітку
pcd_stop_crypto1();               // ОБОВ'ЯЗКОВО опустити шифрування
