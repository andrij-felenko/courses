// межа шару давача: усередині — деталі шини, назовні — одне поняття
esp_err_t sensor_read(int16_t *out) {
    esp_err_t err = bus_transfer(...);          // низ говорить мовою шини
    if (err == ESP_ERR_TIMEOUT ||
        err == ESP_ERR_INVALID_CRC) {
        ESP_LOGW(TAG, "bus error %s", esp_err_to_name(err));  // подробиця — у лог
        return ESP_ERR_SENSOR_OFFLINE;          // нагору — одне поняття шару
    }
    return err;
}
