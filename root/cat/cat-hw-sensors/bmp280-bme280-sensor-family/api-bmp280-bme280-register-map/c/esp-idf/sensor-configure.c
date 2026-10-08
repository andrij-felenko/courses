// Приклад коректної конфігурації цифрового тракту BME280
void sensor_configure(uint8_t dev_addr) {
    // 1. Налаштування IIR-фільтра (кофіцієнт 4) та standby 62.5 мс
    uint8_t config_val = (0x02 << 5) | (0x02 << 2);
    i2c_write_reg(dev_addr, 0xF5, &config_val, 1);

    // 2. Налаштування оверсемплінгу вологості (x1)
    uint8_t ctrl_hum_val = 0x01;
    i2c_write_reg(dev_addr, 0xF2, &ctrl_hum_val, 1);

    // 3. Налаштування оверсемплінгу температури (x2), тиску (x16) та запуску Normal mode
    // Вчинення цього запису також активує значення з 0xF2!
    uint8_t ctrl_meas_val = (0x02 << 5) | (0x05 << 2) | 0x03;
    i2c_write_reg(dev_addr, 0xF4, &ctrl_meas_val, 1);
}
