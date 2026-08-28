// Доброчесніший варіант spi_read: дешева перевірка зв'язку через сталий регістр.
static baro_status_t spi_read_checked(baro_t *self, uint32_t *out_pa) {
    bme280_spi_t *d = (bme280_spi_t *)self;
    uint8_t id = 0;
    spi_read_reg(d->cs_pin, BME280_REG_ID, &id, 1);
    if (id != BME280_CHIP_ID) {
        return BARO_ERR_BUS;        // chip-id «поплив» → зв'язок розірвано
    }
    uint8_t raw[3];
    spi_read_reg(d->cs_pin, BME280_REG_PRESS, raw, 3);
    int32_t v = ((int32_t)raw[0] << 12) | ((int32_t)raw[1] << 4) | (raw[2] >> 4);
    uint32_t pa = compensate(d, v);
    if (pa < 30000u || pa > 110000u) return BARO_ERR_RANGE;
    *out_pa = pa;
    return BARO_OK;
}
