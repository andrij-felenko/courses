#include "driver/i2c.h"
#include "esp_err.h"

#define BME280_I2C_PORT       I2C_NUM_0
#define BME280_I2C_ADDR       0x76

#define BME280_REG_CTRL_HUM   0xF2
#define BME280_REG_CTRL_MEAS  0xF4
#define BME280_REG_CONFIG     0xF5

static esp_err_t bme280_write_reg(uint8_t reg, uint8_t data) {
    uint8_t write_buf[2] = {reg, data};
    return i2c_master_write_to_device(BME280_I2C_PORT, BME280_I2C_ADDR, 
                                      write_buf, sizeof(write_buf), 
                                      1000 / portTICK_PERIOD_MS);
}

esp_err_t bme280_configure_pipeline(void) {
    esp_err_t ret;

    // 1. Налаштування оверсемплінгу вологості osrs_h = x1 (0b001)
    ret = bme280_write_reg(BME280_REG_CTRL_HUM, 0x01);
    if (ret != ESP_OK) return ret;

    // 2. Налаштування IIR-фільтра x4 (0b010) та Standby 1000 мс (0b101): 0xA8
    ret = bme280_write_reg(BME280_REG_CONFIG, 0xA8);
    if (ret != ESP_OK) return ret;

    // 3. Налаштування оверсемплінгу T = x2 (0b010), P = x16 (0b101), Mode = Normal (0b11): 0x57
    ret = bme280_write_reg(BME280_REG_CTRL_MEAS, 0x57);
    return ret;
}
