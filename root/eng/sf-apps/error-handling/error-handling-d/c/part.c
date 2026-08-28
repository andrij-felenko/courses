// ПОГАНО: помилку проковтнуто
void read_and_log_temp(void) {
    uint8_t buf[2];
    // i2c_master_read_from_device повертає esp_err_t, але ми її ігноруємо
    i2c_master_read_from_device(I2C_NUM_0, SENSOR_ADDR,
                                buf, sizeof(buf), pdMS_TO_TICKS(50));
    // якщо зчитування провалилось — buf містить сміття
    // (або нулі після ініціалізації — але нуль теж брехня)
    int16_t raw = (buf[0] << 8) | buf[1];
    float temp_c = raw * 0.0625f;           // для LM75: 0.0625 °C/біт
    ESP_LOGI(TAG, "Temp: %.2f C", temp_c);  // може вивести -1000 C
}
