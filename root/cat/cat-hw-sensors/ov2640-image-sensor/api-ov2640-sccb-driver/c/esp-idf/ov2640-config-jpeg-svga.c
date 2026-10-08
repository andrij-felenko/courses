esp_err_t ov2640_config_jpeg_svga(i2c_port_t i2c_num) {
    esp_err_t ret;
    
    // Переключення на банк DSP
    ret = ov2640_set_bank(i2c_num, BANK_DSP);
    if (ret != ESP_OK) return ret;
    
    // Ввімкнення режиму JPEG та вибір вихідного формату
    ret |= ov2640_write_reg(i2c_num, BANK_DSP, 0xDA, 0x10); // IMAGE_MODE: JPEG enable
    ret |= ov2640_write_reg(i2c_num, BANK_DSP, 0xD7, 0x03); // Format control
    ret |= ov2640_write_reg(i2c_num, BANK_DSP, 0xE0, 0x04); // RESET logic
    
    // Налаштування коефіцієнта квантування QS (якість JPEG)
    // Значення 0x0C забезпечує оптимальний баланс чіткості та розміру
    ret |= ov2640_write_reg(i2c_num, BANK_DSP, 0x44, 0x0C); 
    
    // Масштабування до SVGA (800x600)
    ret |= ov2640_write_reg(i2c_num, BANK_DSP, 0xE1, 0x67); // ZMOW width LSB
    ret |= ov2640_write_reg(i2c_num, BANK_DSP, 0xE2, 0x4B); // ZMOH height LSB
    ret |= ov2640_write_reg(i2c_num, BANK_DSP, 0xE3, 0x00); // ZMMS MSB control
    
    return ret;
}
