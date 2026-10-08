// Зчитування цифрового стану (DO)
bool tcrt5000_read_digital_raw(const tcrt5000_t *dev) {
    if (!dev || !dev->initialized || dev->config.gpio_digital < 0) {
        return false;
    }
    // Опитування GPIO виводу (активний низький рівень)
    return false; // Заглушка апаратного виклику платформи
}

// Зчитування сирого аналогового значення (AO)
tcrt5000_err_t tcrt5000_read_analog_raw(tcrt5000_t *dev, uint16_t *raw_out) {
    if (!dev || !dev->initialized || !raw_out) {
        return TCRT5000_ERR_INVALID_ARG;
    }
    
    uint16_t raw_val = 0; 
    // raw_val = adc_read_channel(dev->config.adc_channel);
    
    dev->last_raw_value = raw_val;
    *raw_out = raw_val;
    return TCRT5000_OK;
}

// Зчитування нормованої напруги у мілівольтах
tcrt5000_err_t tcrt5000_read_voltage_mv(tcrt5000_t *dev, uint32_t v_ref_mv, uint8_t adc_bits, uint32_t *voltage_mv_out) {
    uint16_t raw_val;
    tcrt5000_err_t err = tcrt5000_read_analog_raw(dev, &raw_val);
    if (err != TCRT5000_OK) return err;
    
    uint32_t max_adc = (1U << adc_bits) - 1U;
    *voltage_mv_out = ((uint32_t)raw_val * v_ref_mv) / max_adc;
    return TCRT5000_OK;
}
