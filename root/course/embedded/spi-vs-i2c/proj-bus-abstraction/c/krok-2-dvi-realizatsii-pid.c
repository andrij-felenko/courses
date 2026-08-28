// Прочитати n байтів із регістра reg пристрою dev. 0 — успіх, інакше — код помилки.
int dev_read(const bus_device_t *dev, uint8_t reg, uint8_t *buf, int n) {
    if (dev->bus == BUS_I2C) {
        return i2c_read_reg(dev->i2c_addr, reg, buf, n);   // адреса в кадрі, ACK на кожен байт
    } else {
        gpio_set(dev->spi_cs, 0);          // опустити CS — почали обмін саме з цим чіпом
        spi_transfer(reg | 0x80);          // біт «читання» у старшому розряді (звичай багатьох чіпів)
        for (int i = 0; i < n; i++) {
            buf[i] = spi_transfer(0x00);   // висуваємо порожнє, забираємо корисне
        }
        gpio_set(dev->spi_cs, 1);          // підняти CS — відпустили шину
        return 0;                          // SPI не квитує — помилку ловить рівень вище
    }
}

int dev_write(const bus_device_t *dev, uint8_t reg, uint8_t val) {
    if (dev->bus == BUS_I2C) {
        return i2c_write_reg(dev->i2c_addr, reg, val);
    } else {
        gpio_set(dev->spi_cs, 0);
        spi_transfer(reg & 0x7F);          // старший біт нуль → запис
        spi_transfer(val);
        gpio_set(dev->spi_cs, 1);
        return 0;
    }
}
