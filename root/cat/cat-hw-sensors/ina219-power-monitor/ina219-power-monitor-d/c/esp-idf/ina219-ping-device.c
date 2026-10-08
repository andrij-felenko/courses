// Ініціалізація I2C та перевірка зв'язку з INA219 за адресою 0x40
#include <stdio.h>
#include "driver/i2c.h"
#include "esp_err.h"

#define I2C_MASTER_NUM         I2C_NUM_0
#define INA219_ADDR_GND_GND    0x40
#define INA219_REG_CONFIG      0x00

esp_err_t ina219_ping_device(uint8_t dev_addr) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (dev_addr << 1) | I2C_MASTER_WRITE, true);
    i2c_master_stop(cmd);
    
    esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return ret; // ESP_OK якщо пристрій підтвердив команду (ACK)
}
