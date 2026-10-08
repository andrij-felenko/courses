// Перетворення сирого відліку АЦП у градуси Цельсія
float lm35_raw_to_celsius(const lm35_t *dev, uint32_t raw_adc) {
    if (dev == NULL || dev->lsb_mv <= 0.0f) {
        return 0.0f;
    }
    // Обчислення напруги у мілівольтах
    float voltage_mv = (float)raw_adc * dev->lsb_mv;
    
    // Перетворення напруги у температуру (10 мВ = 1 °C)
    float temp_raw = voltage_mv / 10.0f;
    
    // Застосування коефіцієнтів калібрування
    float temp_calibrated = (temp_raw * dev->config.scale_factor) + dev->config.offset_celsius;
    
    return temp_calibrated;
}
