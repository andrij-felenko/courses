/* Небезпечний патерн: глобальний статичний буфер у вендорському коді */
static uint8_t temp_i2c_tx_buffer[64];
static uint8_t s_device_operating_mode;

void vendor_set_mode_unsafe(uint8_t mode) {
    s_device_operating_mode = mode;
    temp_i2c_tx_buffer[0] = 0xF4;
    temp_i2c_tx_buffer[1] = s_device_operating_mode;
    /* Відправка в шину без прив'язки до екземпляра */
}
