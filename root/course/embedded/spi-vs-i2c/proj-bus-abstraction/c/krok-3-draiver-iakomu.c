// Давач на I2C: різнить його адреса.
static const bus_device_t imu  = { .bus = BUS_I2C, .i2c_addr = 0x68 };
// Флеш на SPI: різнить його лінія CS.
static const bus_device_t flash = { .bus = BUS_SPI, .spi_cs = 17 };

// Звірка ID — однакова для обох, бо говорить через обгортку, а не через шину.
int check_id(const bus_device_t *dev, uint8_t who_am_i_reg, uint8_t expected) {
    uint8_t id = 0;
    if (dev_read(dev, who_am_i_reg, &id, 1) != 0) {
        return -1;                 // I2C повідомив про збій; для SPI завжди 0
    }
    return (id == expected) ? 0 : -2;
}
