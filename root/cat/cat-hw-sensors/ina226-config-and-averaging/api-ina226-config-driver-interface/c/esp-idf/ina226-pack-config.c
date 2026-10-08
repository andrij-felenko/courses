#include "ina226_types.h"
#include "driver/i2c.h"

#define INA226_REG_CONFIG       0x00
#define INA226_REG_MASK_ENABLE  0x06
#define INA226_BIT_CVRF         (1 << 3)
#define INA226_BIT_RST          (1 << 15)

// Перетворення структури конфігурації у 16-бітове значення
static uint16_t ina226_pack_config(const ina226_config_t *cfg) {
    return ((uint16_t)cfg->avg_samples << 9) |
           ((uint16_t)cfg->vbus_conv_time << 6) |
           ((uint16_t)cfg->vsh_conv_time << 3) |
           ((uint16_t)cfg->mode);
}

// Запис 16-бітового регістру по I2C (MSB first)
static esp_err_t ina226_write_reg(i2c_port_t port, uint8_t dev_addr, uint8_t reg, uint16_t val) {
    uint8_t data[3] = { reg, (uint8_t)(val >> 8), (uint8_t)(val & 0xFF) };
    return i2c_master_write_to_device(port, dev_addr, data, sizeof(data), pdMS_TO_TICKS(100));
}

// Читання 16-бітового регістру по I2C (MSB first)
static esp_err_t ina226_read_reg(i2c_port_t port, uint8_t dev_addr, uint8_t reg, uint16_t *val) {
    uint8_t data[2] = {0};
    esp_err_t err = i2c_master_write_read_device(port, dev_addr, &reg, 1, data, 2, pdMS_TO_TICKS(100));
    if (err == ESP_OK) {
        *val = ((uint16_t)data[0] << 8) | data[1];
    }
    return err;
}

// Ініціалізація та застосування конфігурації
esp_err_t ina226_init_device(i2c_port_t port, uint8_t dev_addr, const ina226_config_t *cfg) {
    // 1. Програмне скидання пристрою
    esp_err_t err = ina226_write_reg(port, dev_addr, INA226_REG_CONFIG, INA226_BIT_RST);
    if (err != ESP_OK) return err;

    // 2. Запис нової конфігурації
    uint16_t reg_val = ina226_pack_config(cfg);
    return ina226_write_reg(port, dev_addr, INA226_REG_CONFIG, reg_val);
}

// Перевірка прапора готовності даних CVRF
esp_err_t ina226_check_data_ready(i2c_port_t port, uint8_t dev_addr, bool *ready) {
    uint16_t mask_reg = 0;
    esp_err_t err = ina226_read_reg(port, dev_addr, INA226_REG_MASK_ENABLE, &mask_reg);
    if (err == ESP_OK) {
        *ready = (mask_reg & INA226_BIT_CVRF) != 0;
    }
    return err;
}
