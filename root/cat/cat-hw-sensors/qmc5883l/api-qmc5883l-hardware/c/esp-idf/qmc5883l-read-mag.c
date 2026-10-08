#include <stdio.h>
#include <stdint.h>
#include "driver/i2c.h"

#define QMC5883L_ADDR       0x0D
#define QMC5883L_REG_DATA   0x00
#define QMC5883L_REG_STAT   0x06

esp_err_t qmc5883l_read_mag(i2c_port_t i2c_num, int16_t *x, int16_t *y, int16_t *z, uint8_t *status) {
    uint8_t buffer[6];
    
    // Перевірка готовності даних через Status Register
    esp_err_t ret = i2c_master_write_read_device(i2c_num, QMC5883L_ADDR, 
                                                 (uint8_t[]){QMC5883L_REG_STAT}, 1, 
                                                 status, 1, pdMS_TO_TICKS(50));
    if (ret != ESP_OK || !(*status & 0x01)) {
        return ESP_ERR_INVALID_STATE; // Дані ще не готові (DRDY == 0)
    }

    // Групове (burst) зчитання 6 байтів від 0x00 до 0x05
    ret = i2c_master_write_read_device(i2c_num, QMC5883L_ADDR, 
                                       (uint8_t[]){QMC5883L_REG_DATA}, 1, 
                                       buffer, 6, pdMS_TO_TICKS(50));
    if (ret == ESP_OK) {
        *x = (int16_t)((uint16_t)buffer[1] << 8 | buffer[0]);
        *y = (int16_t)((uint16_t)buffer[3] << 8 | buffer[2]);
        *z = (int16_t)((uint16_t)buffer[5] << 8 | buffer[4]);
    }
    return ret;
}
