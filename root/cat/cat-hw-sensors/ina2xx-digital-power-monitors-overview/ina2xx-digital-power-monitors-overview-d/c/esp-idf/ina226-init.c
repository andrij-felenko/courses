#include <stdio.h>
#include "esp_err.h"
#include "driver/i2c.h"

#define INA226_I2C_ADDR         0x40
#define INA226_REG_CONFIG       0x00
#define INA226_REG_SHUNTVOLT    0x01
#define INA226_REG_BUSVOLT      0x02
#define INA226_REG_POWER        0x03
#define INA226_REG_CURRENT      0x04
#define INA226_REG_CALIBRATION  0x05

// Ініціалізація та запис конфігурації у монітор INA226
esp_err_t ina226_init(i2c_port_t i2c_num, uint16_t cal_val) {
    uint8_t data[3];
    
    // Запис у регістр калібрування Calibration Register
    data[0] = INA226_REG_CALIBRATION;
    data[1] = (cal_val >> 8) & 0xFF;
    data[2] = cal_val & 0xFF;
    
    esp_err_t ret = i2c_master_write_to_device(i2c_num, INA226_I2C_ADDR, data, 3, pdMS_TO_TICKS(1000));
    if (ret != ESP_OK) return ret;

    // Конфігурація: усереднення 16 вибірок, час перетворення 1.1 мс для Bus та Shunt, безперервний режим
    uint16_t config = 0x4527;
    data[0] = INA226_REG_CONFIG;
    data[1] = (config >> 8) & 0xFF;
    data[2] = config & 0xFF;

    return i2c_master_write_to_device(i2c_num, INA226_I2C_ADDR, data, 3, pdMS_TO_TICKS(1000));
}

// Зчитати значення струму в міліамперах
esp_err_t ina226_read_current(i2c_port_t i2c_num, float current_lsb_mA, float *current_mA) {
    uint8_t reg = INA226_REG_CURRENT;
    uint8_t data[2];

    esp_err_t ret = i2c_master_write_read_device(i2c_num, INA226_I2C_ADDR, &reg, 1, data, 2, pdMS_TO_TICKS(1000));
    if (ret == ESP_OK) {
        int16_t raw_val = (int16_t)((data[0] << 8) | data[1]);
        *current_mA = raw_val * current_lsb_mA;
    }
    return ret;
}
