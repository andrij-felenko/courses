esp_err_t read_sample(int16_t *out) {
    if (sensor_wake() == ESP_OK) {
        if (sensor_trigger() == ESP_OK) {
            if (sensor_fetch(out) == ESP_OK) {
                return ESP_OK;          // корисна дія — аж тут, найглибше
            }
        }
    }
    return ESP_FAIL;                     // а яка саме з трьох помилок? втрачено
}
