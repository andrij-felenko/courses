#include <stdio.h>
#include "driver/i2c.h"
#define QMC5883L_ADDR 0x0D

esp_err_t qmc5883l_init(i2c_port_t i2c_num) {
    // 1. Soft Reset (0x0A -> 0x80)
    uint8_t reset_cmd[] = {0x0A, 0x80};
    i2c_master_write_to_device(i2c_num, QMC5883L_ADDR, reset_cmd, 2, pdMS_TO_TICKS(50));
    vTaskDelay(pdMS_TO_TICKS(10));

    // 2. SET/RESET Period (0x0B -> 0x01)
    uint8_t set_period_cmd[] = {0x0B, 0x01};
    i2c_master_write_to_device(i2c_num, QMC5883L_ADDR, set_period_cmd, 2, pdMS_TO_TICKS(50));

    // 3. Control Register 1 (0x09 -> 0x1D): OSR=512 (00b), RNG=±8G (01b), ODR=200Hz (11b), Mode=Continuous (01b)
    // 00011101b = 0x1D
    uint8_t ctrl1_cmd[] = {0x09, 0x1D};
    return i2c_master_write_to_device(i2c_num, QMC5883L_ADDR, ctrl1_cmd, 2, pdMS_TO_TICKS(50));
}
