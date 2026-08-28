// Записати 16 байтів у блок 4. Спершу — та сама автентифікація.
static const uint8_t key_a[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

uint8_t block = 4;

// Дані на запис — РІВНО 16 байтів. Тут: рядок-мітка + число балансу.
uint8_t data[16] = {
    'B', 'A', 'L', 0x00,               // сигнатура «BAL» + роздільник
    0x00, 0x00, 0x27, 0x10,            // баланс = 0x2710 = 10000 (напр. копійок)
    0x00, 0x00, 0x00, 0x00,            // решта — про запас, нулі
    0x00, 0x00, 0x00, 0x00
};

esp_err_t err = pcd_authenticate(PICC_CMD_MF_AUTH_KEY_A, block, key_a, uid, uid_len);
if (err != ESP_OK) {
    ESP_LOGE(TAG, "Авт. перед записом не вдалась: %s", esp_err_to_name(err));
    picc_halt_a();
    pcd_stop_crypto1();
    return;
}

// Запис: РІВНО 16 байтів, розмір теж 16 — CRC додає рівень протоколу
err = mifare_write(block, data, 16);
if (err == ESP_OK) ESP_LOGI(TAG, "Записано.");
else               ESP_LOGE(TAG, "Запис не вдався: %s", esp_err_to_name(err));

picc_halt_a();
pcd_stop_crypto1();
