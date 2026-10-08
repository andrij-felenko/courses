esp_err_t ov2640_check_id(i2c_port_t i2c_num) {
    uint8_t pid = 0, ver = 0;
    esp_err_t ret = ov2640_set_bank(i2c_num, BANK_SENSOR);
    if (ret != ESP_OK) return ret;
    
    // Зчитування PID і VER з банку Sensor
    i2c_master_write_read_device(i2c_num, OV2640_SCCB_ADDR, (uint8_t[]){0x0A}, 1, &pid, 1, pdMS_TO_TICKS(100));
    i2c_master_write_read_device(i2c_num, OV2640_SCCB_ADDR, (uint8_t[]){0x0B}, 1, &ver, 1, pdMS_TO_TICKS(100));
    
    if (pid != 0x26 || ver != 0x42) {
        return ESP_ERR_NOT_FOUND; // Невідомий сенсор або помилка шини
    }
    return ESP_OK;
}

esp_err_t ov2640_set_standby(i2c_port_t i2c_num, bool enable) {
    esp_err_t ret = ov2640_set_bank(i2c_num, BANK_SENSOR);
    if (ret != ESP_OK) return ret;
    
    // Читання поточного значення COM7 (0x12)
    uint8_t com7 = 0;
    i2c_master_write_read_device(i2c_num, OV2640_SCCB_ADDR, (uint8_t[]){0x12}, 1, &com7, 1, pdMS_TO_TICKS(100));
    
    if (enable) {
        com7 |= (1 << 6);  // Встановити біт Standby
    } else {
        com7 &= ~(1 << 6); // Скинути біт Standby
    }
    
    return ov2640_write_reg(i2c_num, BANK_SENSOR, 0x12, com7);
}
