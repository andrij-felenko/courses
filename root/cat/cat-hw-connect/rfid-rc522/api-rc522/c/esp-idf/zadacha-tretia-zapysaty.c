// Записати 16 байтів у блок і перечитати назад для перевірки.
esp_err_t write_and_verify(uint8_t block, const uint8_t *data16) {
    if (pcd_authenticate(0x60, block) != ESP_OK) return ESP_FAIL;  // auth як для читання

    // --- ЗАПИС: MIFARE Write іде у ДВА прийоми, на кожен мітка відповідає ACK (0x0A) ---
    uint8_t hdr[2] = { 0xA0, block };                  // 1) «готуйся писати в цей блок»
    if (picc_mf_command(hdr, 2) != ESP_OK) {
        ESP_LOGE(TAG, "Write: мітка не прийняла адресу");
        return ESP_FAIL;
    }
    if (picc_mf_command(data16, 16) != ESP_OK) {       // 2) рівно 16 Б (не 18! CRC — чип)
        ESP_LOGE(TAG, "Write провалився");
        return ESP_FAIL;
    }
    ESP_LOGI(TAG, "Записано.");

    // --- Перечитуємо назад для впевненості ---
    uint8_t cmd[2] = { 0x30, block };
    uint8_t buf[18]; uint8_t n = sizeof(buf);
    if (picc_transceive_crc(cmd, 2, buf, &n) == ESP_OK) {
        ESP_LOGI(TAG, "Перечитано:");
        ESP_LOG_BUFFER_HEX(TAG, buf, 16);
    }

    // ОБОВ'ЯЗКОВИЙ фінал сесії з міткою:
    picc_halta();                                      // 1. відпустити мітку (HLTA)
    pcd_write(REG_STATUS2, pcd_read(REG_STATUS2) & ~0x08);   // 2. скинути MFCrypto1On
    return ESP_OK;
}
