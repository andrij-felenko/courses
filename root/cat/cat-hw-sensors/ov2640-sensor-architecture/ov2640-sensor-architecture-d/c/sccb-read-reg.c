#include "driver/i2c.h"
#include "esp_log.h"
#include <stdint.h>

#define OV2640_ADDR       0x30
#define REG_BANK_SEL      0xFF
#define REG_PID           0x0A
#define REG_VER           0x0B

static const char *TAG = "OV2640_DIAG";

// Читання одного байта через SCCB з вибором банку
static esp_err_t sccb_read_reg(uint8_t bank, uint8_t reg, uint8_t *val) {
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
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV2640_ADDR << 1) | I2C_MASTER_READ, true);
    i2c_master_read_byte(cmd, val, I2C_MASTER_NACK);
    i2c_master_stop(cmd);
    ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return ret;
}

// Комплексна діагностика стану сенсора
bool ov2640_run_diagnostics(void) {
    uint8_t pid = 0, ver = 0;
    
    // Перевірка зв'язку та ідентифікаторів у Bank 1
    if (sccb_read_reg(1, REG_PID, &pid) != ESP_OK || sccb_read_reg(1, REG_VER, &ver) != ESP_OK) {
        ESP_LOGE(TAG, "Помилка SCCB! Перевірте наявність XVCLK та підтягувальних резисторів SIO_C/SIO_D.");
        return false;
    }

    if (pid != 0x26 || ver != 0x42) {
        ESP_LOGE(TAG, "Невідповідність PID/VER: 0x%02X 0x%02X (очікувалось 0x26 0x42)", pid, ver);
        return false;
    }

    ESP_LOGI(TAG, "Діагностика успішна: сенсор OV2640 виявлено (PID: 0x%02X, VER: 0x%02X).", pid, ver);
    return true;
}
