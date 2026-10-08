#include "driver/i2c.h"
#include "esp_err.h"

#define INA226_I2C_ADDR         0x40
#define INA226_REG_MASK_ENABLE   0x06
#define INA226_REG_ALERT_LIMIT   0x07

// Налаштування апаратного захисту за перевищенням струму (SOL) у режимі фіксації (Latch)
esp_err_t ina226_configure_overcurrent_alert(i2c_port_t i2c_num, uint16_t alert_limit_code) {
    uint8_t write_buf[3];
    
    // 1. Запис порогового значення в регістр Alert Limit
    write_buf[0] = INA226_REG_ALERT_LIMIT;
    write_buf[1] = (uint8_t)(alert_limit_code >> 8);   // Старший байт
    write_buf[2] = (uint8_t)(alert_limit_code & 0xFF);  // Молодший байт
    
    esp_err_t err = i2c_master_write_to_device(i2c_num, INA226_I2C_ADDR, write_buf, 3, pdMS_TO_TICKS(100));
    if (err != ESP_OK) return err;

    // 2. Налаштування MASK_ENABLE: SOL = 1 (біт 15), LEN = 1 (біт 0 — Latch Enable)
    uint16_t mask_enable_val = (1 << 15) | (1 << 0);
    write_buf[0] = INA226_REG_MASK_ENABLE;
    write_buf[1] = (uint8_t)(mask_enable_val >> 8);
    write_buf[2] = (uint8_t)(mask_enable_val & 0xFF);

    return i2c_master_write_to_device(i2c_num, INA226_I2C_ADDR, write_buf, 3, pdMS_TO_TICKS(100));
}
