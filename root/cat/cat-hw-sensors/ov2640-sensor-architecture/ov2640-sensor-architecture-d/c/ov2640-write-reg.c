#include "driver/i2c.h"
#include "esp_err.h"

#define OV2640_SCCB_ADDR 0x30  // 7-бітна адреса OV2640 на шині I2C/SCCB
#define BANK_SEL_REG     0xFF  // Реєстр вибору банку даних

// Функція запису байта в реєстр OV2640 через SCCB/I2C
esp_err_t ov2640_write_reg(uint8_t reg_addr, uint8_t reg_val) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV2640_SCCB_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg_addr, true);
    i2c_master_write_byte(cmd, reg_val, true);
    i2c_master_stop(cmd);
    
    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return ret;
}

// Перемикання адресації на Bank 1 (DSP та JPEG конфігурація)
esp_err_t ov2640_select_bank1(void) {
    return ov2640_write_reg(BANK_SEL_REG, 0x01);
}

// Перемикання адресації на Bank 0 (сенсорне ядро та ADC)
esp_err_t ov2640_select_bank0(void) {
    return ov2640_write_reg(BANK_SEL_REG, 0x00);
}
