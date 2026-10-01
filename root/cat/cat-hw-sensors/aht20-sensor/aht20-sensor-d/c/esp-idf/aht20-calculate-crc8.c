#include <stdint.h>
#include <stdbool.h>
#include "driver/i2c.h"

#define AHT20_I2C_ADDR 0x38

uint8_t aht20_calculate_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

bool aht20_read_data(i2c_port_t port, uint32_t *raw_humidity, uint32_t *raw_temp) {
    uint8_t cmd_trigger[3] = {0xAC, 0x33, 0x00};
    i2c_master_write_to_device(port, AHT20_I2C_ADDR, cmd_trigger, 3, 100 / portTICK_PERIOD_MS);
    
    vTaskDelay(80 / portTICK_PERIOD_MS);
    
    uint8_t rx_buf[7] = {0};
    i2c_master_read_from_device(port, AHT20_I2C_ADDR, rx_buf, 7, 100 / portTICK_PERIOD_MS);
    
    // Перевірка прапорця Busy (біт 7) та Calibrated (біт 3)
    if ((rx_buf[0] & 0x80) != 0 || (rx_buf[0] & 0x08) == 0) {
        return false;
    }
    
    // Верифікація CRC-8
    if (aht20_calculate_crc8(rx_buf, 6) != rx_buf[6]) {
        return false;
    }
    
    *raw_humidity = ((uint32_t)rx_buf[1] << 12) | ((uint32_t)rx_buf[2] << 4) | ((uint32_t)rx_buf[3] >> 4);
    *raw_temp = (((uint32_t)rx_buf[3] & 0x0F) << 16) | ((uint32_t)rx_buf[4] << 8) | (uint32_t)rx_buf[5];
    
    return true;
}
