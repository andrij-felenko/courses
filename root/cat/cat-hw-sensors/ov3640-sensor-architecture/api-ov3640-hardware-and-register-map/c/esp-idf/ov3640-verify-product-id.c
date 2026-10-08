#include "esp_err.h"
#include "driver/i2c.h"

#define OV3640_SCCB_ADDR   0x3C
#define REG_BANK_SEL       0xFF
#define REG_PID_HIGH       0x0A
#define REG_PID_LOW        0x0B

esp_err_t ov3640_verify_product_id(i2c_port_t i2c_num) {
    uint8_t bank = 0x01; // Переключаємося на Bank 1
    uint8_t pid_h = 0, pid_l = 0;
    
    // Запис вибору банки
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV3640_SCCB_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, REG_BANK_SEL, true);
    i2c_master_write_byte(cmd, bank, true);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(i2c_num, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    if (ret != ESP_OK) return ret;

    // Зчитування PID High
    cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV3640_SCCB_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, REG_PID_HIGH, true);
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV3640_SCCB_ADDR << 1) | I2C_MASTER_READ, true);
    i2c_master_read_byte(cmd, &pid_h, I2C_MASTER_NACK);
    i2c_master_stop(cmd);
    ret = i2c_master_cmd_begin(i2c_num, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    if (ret != ESP_OK) return ret;

    // Зчитування PID Low
    cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV3640_SCCB_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, REG_PID_LOW, true);
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV3640_SCCB_ADDR << 1) | I2C_MASTER_READ, true);
    i2c_master_read_byte(cmd, &pid_l, I2C_MASTER_NACK);
    i2c_master_stop(cmd);
    ret = i2c_master_cmd_begin(i2c_num, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    if (ret != ESP_OK) return ret;

    if (pid_h == 0x36 && pid_l == 0x48) {
        return ESP_OK; // Ідентифікація успішна
    }
    return ESP_ERR_NOT_FOUND;
}
