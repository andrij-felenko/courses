#include "driver/i2c.h"
#include "esp_err.h"
#include <stdint.h>

#define OV2640_ADDR       0x30
#define REG_BANK_SEL      0xFF
#define REG_CLKRC         0x11
#define REG_COM10         0x15

// Бітові маски для COM10 (Bank 0)
#define COM10_PCLK_REV    (1 << 4) // Інверсія фази PCLK
#define COM10_HREF_REV    (1 << 3) // Інверсія полярності HREF
#define COM10_VSYNC_NEG   (1 << 1) // Інверсія полярності VSYNC

static esp_err_t write_sccb(uint8_t bank, uint8_t reg, uint8_t val) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV2640_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, REG_BANK_SEL, true);
    i2c_master_write_byte(cmd, bank, true);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    if (ret != ESP_OK) return ret;

    cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV2640_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_write_byte(cmd, val, true);
    i2c_master_stop(cmd);
    ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return ret;
}

// Конфігурація PLL та полярностей DVP
esp_err_t ov2640_configure_dvp_clock(uint8_t clkrc_div, bool pclk_invert, bool vsync_negative) {
    // Встановлення дільника CLKRC у Bank 0
    esp_err_t err = write_sccb(0, REG_CLKRC, clkrc_div & 0x3F);
    if (err != ESP_OK) return err;

    // Налаштування полярності синхросигналів у COM10
    uint8_t com10_val = 0x00;
    if (pclk_invert) com10_val |= COM10_PCLK_REV;
    if (vsync_negative) com10_val |= COM10_VSYNC_NEG;
    
    err = write_sccb(0, REG_COM10, com10_val);
    return err;
}
