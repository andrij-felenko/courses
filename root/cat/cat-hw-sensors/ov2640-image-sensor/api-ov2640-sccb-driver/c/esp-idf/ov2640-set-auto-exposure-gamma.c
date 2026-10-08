esp_err_t ov2640_set_auto_exposure_gamma(i2c_port_t i2c_num) {
    esp_err_t ret = ESP_OK;
    
    // Налаштування AEC/AGC у банку Sensor
    ret |= ov2640_set_bank(i2c_num, BANK_SENSOR);
    ret |= ov2640_write_reg(i2c_num, BANK_SENSOR, 0x24, 0x40); // AEW: Верхній поріг яскравості
    ret |= ov2640_write_reg(i2c_num, BANK_SENSOR, 0x25, 0x38); // AEB: Нижній поріг яскравості
    ret |= ov2640_write_reg(i2c_num, BANK_SENSOR, 0x13, 0xE7); // COM8: Ввімкнути AEC, AGC, AWB
    
    // Налаштування тонової гама-кривої у банку DSP
    ret |= ov2640_set_bank(i2c_num, BANK_DSP);
    static const uint8_t gamma_curve[15] = {
        0x04, 0x0E, 0x1A, 0x31, 0x5A, 0x69, 0x75, 0x7E, 
        0x88, 0x8F, 0x96, 0xA3, 0xAF, 0xC4, 0xD7
    };
    
    for (int i = 0; i < 15; i++) {
        ret |= ov2640_write_reg(i2c_num, BANK_DSP, 0x7A + i, gamma_curve[i]);
    }
    
    return ret;
}
