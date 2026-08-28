// ДОБРЕ: помилка перевіряється й обробляється
void read_and_log_temp(void) {
    uint8_t buf[2];
    esp_err_t err = i2c_master_read_from_device(
        I2C_NUM_0, SENSOR_ADDR, buf, sizeof(buf), pdMS_TO_TICKS(50));

    if (err != ESP_OK) {
        ESP_LOGW(TAG, "I2C read failed: %s — skipping sample",
                 esp_err_to_name(err));
        return;   // не чіпаємо buf — він ненадійний; чекаємо наступного зразка
    }

    int16_t raw = (buf[0] << 8) | buf[1];
    float temp_c = raw * 0.0625f;
    ESP_LOGI(TAG, "Temp: %.2f C", temp_c);
}
