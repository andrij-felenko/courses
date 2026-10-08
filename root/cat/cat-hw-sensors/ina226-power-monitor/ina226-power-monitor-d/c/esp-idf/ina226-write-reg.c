#include <stdio.h>
#include "driver/i2c.h"
#include "esp_err.h"

#define INA226_I2C_ADDR       0x40
#define INA226_REG_CONFIG     0x00
#define INA226_REG_CALIB      0x05
#define INA226_REG_MASK_EN    0x06
#define INA226_REG_ALERT_LIM  0x07

// Налаштування INA226: AVG=64, VBUS_CT=1.1ms, VSH_CT=1.1ms, Mode=Continuous
// Маска бітів CONFIG: 0x4000 (AVG=64) | 0x01C0 (VBUS=1.1ms) | 0x0038 (VSH=1.1ms) | 0x0007 (Continuous)
#define INA226_CONFIG_VAL     0x41F7 

esp_err_t ina226_write_reg(i2c_port_t port, uint8_t reg, uint16_t val) {
    uint8_t data[3] = { reg, (uint8_t)(val >> 8), (uint8_t)(val & 0xFF) };
    return i2c_master_write_to_device(port, INA226_I2C_ADDR, data, 3, pdMS_TO_TICKS(100));
}

void app_main(void) {
    // Ініціалізація I2C шини на ESP32
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = 21,
        .scl_io_num = 22,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 400000
    };
    i2c_param_config(I2C_NUM_0, &conf);
    i2c_driver_install(I2C_NUM_0, conf.mode, 0, 0, 0);

    // 1. Запис регістра конфігурації (усереднення 64 вибірки, час конверсії 1.1 мс)
    ina226_write_reg(I2C_NUM_0, INA226_REG_CONFIG, INA226_CONFIG_VAL);

    // 2. Запис регістра калібрування (CAL = 2048 для R_shunt = 10 мОм, Current_LSB = 250 мкА)
    ina226_write_reg(I2C_NUM_0, INA226_REG_CALIB, 2048);

    // 3. Налаштування апаратного захисту від перевантаження за струмом (SOL)
    // Поріг 5.0 А при R_shunt = 10 мОм відповідає V_shunt = 50 мВ (20000 відліків АЦП по 2.5 мкВ)
    ina226_write_reg(I2C_NUM_0, INA226_REG_ALERT_LIM, 20000);
    
    // Активація переривання SOL (Shunt Over Limit) та режиму фіксації Latch Mode (0x8001)
    ina226_write_reg(I2C_NUM_0, INA226_REG_MASK_EN, 0x8001);
}
