// Регістри MFRC522 з даташита NXP — знадобляться лише ці:
#define REG_COMMAND     0x01     // яку команду виконує чип
#define REG_COM_IRQ     0x04     // прапорці завершення
#define REG_STATUS2     0x08     // біт 3 = MFCrypto1On
#define REG_FIFO_DATA   0x09
#define REG_FIFO_LEVEL  0x0A

// Читаємо блок 4 (перший блок сектора 1) ключем A = FF..FF.
esp_err_t read_block(uint8_t block) {
    uint8_t key[6];
    memset(key, 0xFF, sizeof(key));                    // дефолтний ключ

    // --- КРОК 1: автентифікація сектора, у якому лежить цей блок ---
    // Команда чипа MFAuthent (0x0E); у FIFO лягає 12 байтів:
    // [0x60 = ключем A][адреса блока][6 Б ключа][4 Б UID]
    uint8_t auth[12] = { 0x60, block };
    memcpy(&auth[2], key, 6);
    memcpy(&auth[8], uid, 4);
    pcd_write(REG_COMMAND, 0x00);                      // Idle — зупинити попереднє
    pcd_write(REG_FIFO_LEVEL, 0x80);                   // скинути FIFO
    for (int i = 0; i < 12; i++) pcd_write(REG_FIFO_DATA, auth[i]);
    pcd_write(REG_COMMAND, 0x0E);                      // MFAuthent
    for (int i = 0; i < 20 && !(pcd_read(REG_COM_IRQ) & 0x10); i++)
        vTaskDelay(pdMS_TO_TICKS(1));                  // чекаємо IdleIRq
    if (!(pcd_read(REG_STATUS2) & 0x08)) {             // Crypto1 так і не ввімкнувся
        ESP_LOGE(TAG, "Auth провалилась: не той ключ або не MIFARE Classic");
        return ESP_FAIL;
    }

    // --- КРОК 2: читання 16 байтів у буфер ---
    // УВАГА: буфер 18 байтів (16 даних + 2 CRC), і n теж 18.
    uint8_t cmd[2] = { 0x30, block };                  // MF_READ
    uint8_t buf[18]; uint8_t n = sizeof(buf);
    if (picc_transceive_crc(cmd, 2, buf, &n) != ESP_OK) {   // CRC дописує сам чип
        ESP_LOGE(TAG, "Read провалився");
        return ESP_FAIL;
    }
    ESP_LOGI(TAG, "Блок %d:", block);
    ESP_LOG_BUFFER_HEX(TAG, buf, 16);                  // 17-й і 18-й — CRC, не дані
    return ESP_OK;
}
