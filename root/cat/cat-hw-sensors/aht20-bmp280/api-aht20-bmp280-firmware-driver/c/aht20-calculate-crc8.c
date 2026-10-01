// Перевірка CRC8 для AHT20 та зчитування сирих даних у C
uint8_t aht20_calculate_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; b++) {
            if (crc & 0x80) crc = (crc << 1) ^ 0x31;
            else crc <<= 1;
        }
    }
    return crc;
}

int combo_sensor_read_raw(combo_sensor_t *dev, uint32_t *raw_hum, uint32_t *raw_temp_aht, uint32_t *raw_temp_bmp, uint32_t *raw_press) {
    uint8_t aht_buf[7];
    // Зчитати 7 байтів з AHT20 через I2C
    if (aht20_calculate_crc8(aht_buf, 6) != aht_buf[6]) return -1; // Помилка CRC

    *raw_hum = ((uint32_t)aht_buf[1] << 12) | ((uint32_t)aht_buf[2] << 4) | (aht_buf[3] >> 4);
    *raw_temp_aht = (((uint32_t)aht_buf[3] & 0x0F) << 16) | ((uint32_t)aht_buf[4] << 8) | aht_buf[5];
    return 0;
}
