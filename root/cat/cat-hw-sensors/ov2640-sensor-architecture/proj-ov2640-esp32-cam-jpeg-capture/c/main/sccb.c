#include "sccb.h"
#include "driver/i2c.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "sccb";
static bool s_sccb_initialized = false;
static uint8_t s_current_bank = 0xFF;

esp_err_t sccb_init(int sda_pin, int scl_pin, uint32_t freq_hz) {
    if (s_sccb_initialized) {
        ESP_LOGW(TAG, "Шина SCCB вже ініціалізована");
        return ESP_OK;
    }

    if (freq_hz == 0) {
        freq_hz = 100000;
    }

    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = sda_pin,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = scl_pin,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = freq_hz,
        .clk_flags = 0
    };

    esp_err_t err = i2c_param_config(SCCB_I2C_PORT, &conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка конфігурації параметрів I2C: 0x%x", err);
        return err;
    }

    err = i2c_driver_install(SCCB_I2C_PORT, conf.mode, 0, 0, 0);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка встановлення драйвера I2C: 0x%x", err);
        return err;
    }

    s_sccb_initialized = true;
    s_current_bank = 0xFF;
    ESP_LOGI(TAG, "Шина SCCB успішно ініціалізована (SDA=%d, SCL=%d, Freq=%lu Гц)",
             sda_pin, scl_pin, (unsigned long)freq_hz);
    return ESP_OK;
}

esp_err_t sccb_deinit(void) {
    if (!s_sccb_initialized) {
        return ESP_OK;
    }
    esp_err_t err = i2c_driver_delete(SCCB_I2C_PORT);
    if (err == ESP_OK) {
        s_sccb_initialized = false;
        s_current_bank = 0xFF;
        ESP_LOGI(TAG, "Драйвер SCCB видалено");
    }
    return err;
}

esp_err_t sccb_write_reg(uint8_t slv_addr, uint8_t reg, uint8_t val) {
    if (!s_sccb_initialized) {
        ESP_LOGE(TAG, "Помилка: шину SCCB не ініціалізовано");
        return ESP_ERR_INVALID_STATE;
    }

    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (slv_addr << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_write_byte(cmd, val, true);
    i2c_master_stop(cmd);

    esp_err_t err = i2c_master_cmd_begin(SCCB_I2C_PORT, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка запису SCCB [0x%02X] = 0x%02X (err: 0x%x)", reg, val, err);
    }
    return err;
}

esp_err_t sccb_read_reg(uint8_t slv_addr, uint8_t reg, uint8_t *val) {
    if (!s_sccb_initialized || !val) {
        return ESP_ERR_INVALID_ARG;
    }

    /* Фаза 1: Передача адреси регістру для читання */
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (slv_addr << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_stop(cmd);

    esp_err_t err = i2c_master_cmd_begin(SCCB_I2C_PORT, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка запису адреси регістру SCCB 0x%02X: 0x%x", reg, err);
        return err;
    }

    /* Фаза 2: Зчитування даних з відправкою NACK наприкінці за специфікацією SCCB */
    cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (slv_addr << 1) | I2C_MASTER_READ, true);
    i2c_master_read_byte(cmd, val, I2C_MASTER_NACK);
    i2c_master_stop(cmd);

    err = i2c_master_cmd_begin(SCCB_I2C_PORT, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка зчитування байта SCCB з 0x%02X: 0x%x", reg, err);
    }
    return err;
}

esp_err_t sccb_set_bank(uint8_t slv_addr, uint8_t bank) {
    if (s_current_bank == bank) {
        return ESP_OK;
    }

    esp_err_t err = sccb_write_reg(slv_addr, SCCB_REG_BANK_SEL, bank);
    if (err == ESP_OK) {
        s_current_bank = bank;
    }
    return err;
}
