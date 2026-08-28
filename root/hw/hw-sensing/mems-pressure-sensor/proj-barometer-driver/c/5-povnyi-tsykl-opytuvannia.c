// Прототип абстрактної функції читання I2C шини
int i2c_read_registers(void *bus, uint8_t addr, uint8_t reg, uint8_t *buf, uint16_t len);

void baro_polling_step(MemsBarometer *dev) {
    uint8_t burst_buffer[6];
    // Неподільне читання 6 байтів: 3 байти тиску + 3 байти температури
    if (i2c_read_registers(dev->bus_handle, dev->dev_addr, 0x04, burst_buffer, 6) != 0) {
        return;
    }

    uint32_t raw_p = ((uint32_t)burst_buffer[2] << 16) |
                     ((uint32_t)burst_buffer[1] << 8)  |
                     burst_buffer[0];

    uint32_t raw_t = ((uint32_t)burst_buffer[5] << 16) |
                     ((uint32_t)burst_buffer[4] << 8)  |
                     burst_buffer[3];

    double t_c = baro_compensate_temperature(&dev->calib, raw_t);
    double p_pa = baro_compensate_pressure(&dev->calib, raw_p, t_c);

    double smooth_p = 0.0;
    double altitude = 0.0;
    baro_process_sample(dev, p_pa, t_c, &smooth_p, &altitude);

    // Дані висоти готові для відправки в регулятор висоти польотного контролера
}
