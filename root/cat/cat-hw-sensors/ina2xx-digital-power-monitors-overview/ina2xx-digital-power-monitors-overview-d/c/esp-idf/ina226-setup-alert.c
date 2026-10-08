#include <stdio.h>
#include <stdint.h>
#include "driver/i2c.h"

#define INA226_I2C_ADDR         0x40
#define INA226_REG_CONFIG       0x00
#define INA226_REG_MASK_ENABLE  0x06
#define INA226_REG_ALERT_LIMIT  0x07

// Конфігурація: 16 вибірок усереднення, 1.1 мс час перетворення
// Біти CONFIG: AVG=010 (16x), VBUS=100 (1.1ms), VSH=100 (1.1ms), MODE=111 (Continuous Shunt&Bus)
#define CONFIG_VALUE            0x44B7

// Поріг тривоги по струму (SOL): 4.0 А при Current_LSB = 200 мкА => 4.0 / 0.0002 = 20000 (0x4E20)
#define ALERT_LIMIT_VALUE       0x4E20

// Маска переривань: SOL = 1 (біт 15), Latch Enable = 1 (біт 0) => 0x8001
#define MASK_ENABLE_VALUE       0x8001

esp_err_t ina226_setup_alert(void) {
    uint8_t cfg_data[3] = { INA226_REG_CONFIG, (uint8_t)(CONFIG_VALUE >> 8), (uint8_t)(CONFIG_VALUE & 0xFF) };
    i2c_master_write_to_device(I2C_NUM_0, INA226_I2C_ADDR, cfg_data, 3, pdMS_TO_TICKS(100));

    uint8_t limit_data[3] = { INA226_REG_ALERT_LIMIT, (uint8_t)(ALERT_LIMIT_VALUE >> 8), (uint8_t)(ALERT_LIMIT_VALUE & 0xFF) };
    i2c_master_write_to_device(I2C_NUM_0, INA226_I2C_ADDR, limit_data, 3, pdMS_TO_TICKS(100));

    uint8_t mask_data[3] = { INA226_REG_MASK_ENABLE, (uint8_t)(MASK_ENABLE_VALUE >> 8), (uint8_t)(MASK_ENABLE_VALUE & 0xFF) };
    return i2c_master_write_to_device(I2C_NUM_0, INA226_I2C_ADDR, mask_data, 3, pdMS_TO_TICKS(100));
}
