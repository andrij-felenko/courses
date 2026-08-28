/* ========================================================================= */
/* Драйвер датчика BME280 на C99, що працює суто через hal_i2c_bus_t         */
/* ========================================================================= */

#define BME280_I2C_ADDR_PRIM   0x76
#define BME280_I2C_ADDR_SEC    0x77
#define BME280_REG_CHIP_ID     0xD0
#define BME280_REG_RESET       0xE0
#define BME280_REG_CTRL_HUM    0xF2
#define BME280_REG_STATUS      0xF3
#define BME280_REG_CTRL_MEAS   0xF4
#define BME280_REG_CONFIG      0xF5
#define BME280_REG_PRESS_MSB   0xF7
#define BME280_REG_TEMP_MSB    0xFA
#define BME280_REG_CALIB00     0x88

#define BME280_CHIP_ID_VAL     0x60

typedef struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
} bme280_calib_t;

typedef struct {
    const hal_i2c_bus_t *bus;
    uint8_t i2c_addr;
    bme280_calib_t calib;
    int32_t t_fine;
} bme280_driver_t;

hal_status_t bme280_init(bme280_driver_t *dev, const hal_i2c_bus_t *bus, uint8_t addr) {
    if (!dev || !bus) return HAL_STATUS_INVALID_ARG;
    dev->bus = bus;
    dev->i2c_addr = addr;
    dev->t_fine = 0;

    /* 1. Перевірка Chip ID */
    uint8_t reg = BME280_REG_CHIP_ID;
    uint8_t chip_id = 0;
    hal_status_t status = hal_i2c_write_read(dev->bus, dev->i2c_addr,
                                             &reg, 1, &chip_id, 1, 100);
    if (status != HAL_STATUS_OK) return status;
    if (chip_id != BME280_CHIP_ID_VAL) return HAL_STATUS_ERROR;

    /* 2. Зчитування калібрувальних коефіцієнтів температури */
    uint8_t calib_reg = BME280_REG_CALIB00;
    uint8_t calib_buf[6];
    status = hal_i2c_write_read(dev->bus, dev->i2c_addr,
                                &calib_reg, 1, calib_buf, 6, 100);
    if (status != HAL_STATUS_OK) return status;

    dev->calib.dig_T1 = (uint16_t)(calib_buf[0] | (calib_buf[1] << 8));
    dev->calib.dig_T2 = (int16_t)(calib_buf[2] | (calib_buf[3] << 8));
    dev->calib.dig_T3 = (int16_t)(calib_buf[4] | (calib_buf[5] << 8));

    /* 3. Конфігурація: режим Normal, Oversampling x1 */
    uint8_t cfg_data[2];
    cfg_data[0] = BME280_REG_CTRL_MEAS;
    cfg_data[1] = (1U << 5) | (1U << 2) | (3U); /* osrs_t x1, osrs_p x1, mode Normal */
    return hal_i2c_write(dev->bus, dev->i2c_addr, cfg_data, 2, 100);
}

hal_status_t bme280_read_temperature(bme280_driver_t *dev, int32_t *out_temp_c_x100) {
    if (!dev || !dev->bus || !out_temp_c_x100) return HAL_STATUS_INVALID_ARG;

    uint8_t reg = BME280_REG_TEMP_MSB;
    uint8_t raw[3];
    hal_status_t status = hal_i2c_write_read(dev->bus, dev->i2c_addr, &reg, 1, raw, 3, 100);
    if (status != HAL_STATUS_OK) return status;

    int32_t adc_T = (int32_t)(((uint32_t)raw[0] << 12) | ((uint32_t)raw[1] << 4) | ((uint32_t)raw[2] >> 4));

    /* Формула компенсації за даташитом Bosch BME280 */
    int32_t var1 = ((((adc_T >> 3) - ((int32_t)dev->calib.dig_T1 << 1))) * ((int32_t)dev->calib.dig_T2)) >> 11;
    int32_t var2 = (((((adc_T >> 4) - ((int32_t)dev->calib.dig_T1)) *
                      ((adc_T >> 4) - ((int32_t)dev->calib.dig_T1))) >> 12) *
                    ((int32_t)dev->calib.dig_T3)) >> 14;

    dev->t_fine = var1 + var2;
    *out_temp_c_x100 = (dev->t_fine * 5 + 128) >> 8;
    return HAL_STATUS_OK;
}
