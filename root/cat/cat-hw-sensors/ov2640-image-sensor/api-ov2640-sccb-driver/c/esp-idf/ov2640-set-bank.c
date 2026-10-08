#include <esp_err.h>
#include <driver/i2c.h>

#define OV2640_SCCB_ADDR   0x30  // 7-бітний I2C-адрес сенсора OV2640
#define OV2640_BANK_SEL    0xFF  // Службовий регістр вибору банку
#define BANK_DSP           0x00  // Цифровий процесор обробки
#define BANK_SENSOR        0x01  // Аналогова матриця сенсора

static uint8_t s_current_bank = 0xFF; // Поточний активний банк

esp_err_t ov2640_set_bank(i2c_port_t i2c_num, uint8_t bank) {
    if (s_current_bank == bank) {
        return ESP_OK; // Банк уже активний, уникнення зайвих транзакцій
    }
    
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV2640_SCCB_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, OV2640_BANK_SEL, true);
    i2c_master_write_byte(cmd, bank, true);
    i2c_master_stop(cmd);
    
    esp_err_t ret = i2c_master_cmd_begin(i2c_num, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    
    if (ret == ESP_OK) {
        s_current_bank = bank;
    }
    return ret;
}

esp_err_t ov2640_write_reg(i2c_port_t i2c_num, uint8_t bank, uint8_t reg, uint8_t val) {
    esp_err_t ret = ov2640_set_bank(i2c_num, bank);
    if (ret != ESP_OK) {
        return ret;
    }
    
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV2640_SCCB_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_write_byte(cmd, val, true);
    i2c_master_stop(cmd);
    
    ret = i2c_master_cmd_begin(i2c_num, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return ret;
}
