#include <stdio.h>
#include <stdint.h>
#include "driver/i2c.h"

#define INA226_I2C_ADDR         0x40
#define INA226_REG_CALIBRATION  0x05
#define INA226_REG_CURRENT      0x04
#define INA226_REG_POWER        0x03

const float CURRENT_LSB = 0.0002f; // 200 мкА на LSB
const float POWER_LSB = 0.005f;   // 5 мВт на LSB

esp_err_t ina226_write_register(uint8_t reg, uint16_t value) {
    uint8_t data[3] = { reg, (uint8_t)(value >> 8), (uint8_t)(value & 0xFF) };
    return i2c_master_write_to_device(I2C_NUM_0, INA226_I2C_ADDR, data, 3, pdMS_TO_TICKS(100));
}

esp_err_t ina226_read_register(uint8_t reg, int16_t *value) {
    uint8_t data[2];
    esp_err_t ret = i2c_master_write_read_device(I2C_NUM_0, INA226_I2C_ADDR, &reg, 1, data, 2, pdMS_TO_TICKS(100));
    if (ret == ESP_OK) {
        *value = (int16_t)((data[0] << 8) | data[1]);
    }
    return ret;
}

void app_main(void) {
    // Запис значення калібрування CAL = 2560 (0x0A00)
    ina226_write_register(INA226_REG_CALIBRATION, 2560);

    int16_t raw_current = 0;
    int16_t raw_power = 0;

    if (ina226_read_register(INA226_REG_CURRENT, &raw_current) == ESP_OK) {
        float current_amps = raw_current * CURRENT_LSB;
        printf("Струм: %.3f A\n", current_amps);
    }

    if (ina226_read_register(INA226_REG_POWER, &raw_power) == ESP_OK) {
        float power_watts = (uint16_t)raw_power * POWER_LSB;
        printf("Потужність: %.3f Вт\n", power_watts);
    }
}
