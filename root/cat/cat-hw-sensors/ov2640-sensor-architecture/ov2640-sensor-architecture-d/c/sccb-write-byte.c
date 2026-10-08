#include "driver/i2c.h"
#include "esp_err.h"
#include <stdint.h>

#define OV2640_I2C_ADDR   0x30  // 7-бітна адреса OV2640
#define REG_BANK_SEL      0xFF  // Адреса реєстру вибору банку
#define I2C_MASTER_PORT   I2C_NUM_0

// Структура для збереження пар адреса-значення
typedef struct {
    uint8_t reg;
    uint8_t val;
} ov2640_reg_val_t;

static uint8_t s_current_bank = 0xFF; // Поточний активний банк

// Низькорівневий запис одного байта через I2C/SCCB
static esp_err_t sccb_write_byte(uint8_t reg, uint8_t val) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV2640_I2C_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_write_byte(cmd, val, true);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_PORT, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return ret;
}

// Безпечний запис у реєстр із контролем активного банку
esp_err_t ov2640_write_register_safe(uint8_t bank, uint8_t reg, uint8_t val) {
    if (s_current_bank != bank) {
        esp_err_t err = sccb_write_byte(REG_BANK_SEL, bank);
        if (err != ESP_OK) return err;
        s_current_bank = bank;
    }
    return sccb_write_byte(reg, val);
}

// Послідовний запис таблиці конфігурації
esp_err_t ov2640_load_reg_table(const ov2640_reg_val_t *table, size_t count, uint8_t default_bank) {
    s_current_bank = 0xFF; // Скидання стану перед початком
    for (size_t i = 0; i < count; i++) {
        if (table[i].reg == REG_BANK_SEL) {
            s_current_bank = table[i].val;
            esp_err_t err = sccb_write_byte(REG_BANK_SEL, table[i].val);
            if (err != ESP_OK) return err;
        } else {
            esp_err_t err = ov2640_write_register_safe(s_current_bank == 0xFF ? default_bank : s_current_bank, 
                                                       table[i].reg, table[i].val);
            if (err != ESP_OK) return err;
        }
    }
    return ESP_OK;
}
