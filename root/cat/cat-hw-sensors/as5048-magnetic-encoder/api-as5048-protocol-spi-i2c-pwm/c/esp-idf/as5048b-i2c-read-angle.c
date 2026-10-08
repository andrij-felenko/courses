#include <stdint.h>
#include <stdbool.h>
#include "driver/i2c.h"

#define AS5048B_I2C_ADDR    0x40  // Базова 7-бітна адреса I2C
#define AS5048B_REG_ANGLMSB 0xFE  // Старший байт кута [13:6]
#define AS5048B_REG_ANGLLSB 0xFF  // Молодший байт кута [5:0]

bool as5048b_i2c_read_angle(i2c_port_t i2c_num, float *angle_deg) {
    uint8_t msb = 0, lsb = 0;

    // 1. Зчитання MSB (регістр 0xFE), що одночасно фіксує значення LSB у буфері
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (AS5048B_I2C_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, AS5048B_REG_ANGLMSB, true);
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (AS5048B_I2C_ADDR << 1) | I2C_MASTER_READ, true);
    i2c_master_read_byte(cmd, &msb, I2C_MASTER_NACK);
    i2c_master_stop(cmd);
    
    if (i2c_master_cmd_begin(i2c_num, cmd, pdMS_TO_TICKS(10)) != ESP_OK) {
        i2c_cmd_link_delete(cmd);
        return false;
    }
    i2c_cmd_link_delete(cmd);

    // 2. Зчитання LSB (регістр 0xFF)
    cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (AS5048B_I2C_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, AS5048B_REG_ANGLLSB, true);
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (AS5048B_I2C_ADDR << 1) | I2C_MASTER_READ, true);
    i2c_master_read_byte(cmd, &lsb, I2C_MASTER_NACK);
    i2c_master_stop(cmd);

    if (i2c_master_cmd_begin(i2c_num, cmd, pdMS_TO_TICKS(10)) != ESP_OK) {
        i2c_cmd_link_delete(cmd);
        return false;
    }
    i2c_cmd_link_delete(cmd);

    // Збірка 14-бітного кута (8 бітів MSB зсуваються на 6 позицій ліворуч)
    uint16_t raw_angle = ((uint16_t)msb << 6) | (lsb & 0x3F);
    *angle_deg = ((float)raw_angle * 360.0f) / 16384.0f;
    return true;
}
