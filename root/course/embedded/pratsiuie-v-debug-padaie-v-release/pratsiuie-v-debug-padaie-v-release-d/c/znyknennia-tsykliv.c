// Наївна затримка: працює лише в -O0
void delay_ms(uint32_t count) {
    for (uint32_t i = 0; i < count * 1000; i++) {
        // Порожнє тіло
    }
}

void eeprom_write_page(uint16_t addr, uint8_t *data) {
    i2c_start();
    i2c_write(addr);
    i2c_write_buffer(data, 32);
    i2c_stop();

    // EEPROM вимагає 5 мс на запис комірок у внутрішню матрицю
    delay_ms(5); 
}
