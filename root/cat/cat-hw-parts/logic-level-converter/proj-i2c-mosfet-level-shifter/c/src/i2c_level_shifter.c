#include "i2c_level_shifter.h"
#include "esp_log.h"

static const char *TAG = "I2C_SHIFTER";

esp_err_t i2c_shifter_init(const i2c_shifter_config_t *cfg) {
    if (!cfg) {
        return ESP_ERR_INVALID_ARG;
    }

    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = cfg->sda_pin,
        .sda_pullup_en = cfg->enable_internal_pullup ? GPIO_PULLUP_ENABLE : GPIO_PULLUP_DISABLE,
        .scl_io_num = cfg->scl_pin,
        .scl_pullup_en = cfg->enable_internal_pullup ? GPIO_PULLUP_ENABLE : GPIO_PULLUP_DISABLE,
        .master.clk_speed = (uint32_t)cfg->speed_hz,
        .clk_flags = 0
    };

    esp_err_t err = i2c_param_config(cfg->port, &conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка конфігурації параметрів I2C: %s", esp_err_to_name(err));
        return err;
    }

    // Встановлюємо драйвер без RX/TX буферів, оскільки ESP32 працює в режимі майстра
    err = i2c_driver_install(cfg->port, conf.mode, 0, 0, 0);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка встановлення драйвера I2C: %s", esp_err_to_name(err));
        return err;
    }

    ESP_LOGI(TAG, "I2C порт %d успішно ініціалізовано на швидкості %u Гц (SDA=%d, SCL=%d)",
             cfg->port, (unsigned)cfg->speed_hz, cfg->sda_pin, cfg->scl_pin);
    return ESP_OK;
}

esp_err_t i2c_shifter_write_reg(const i2c_shifter_config_t *cfg,
                                uint8_t dev_addr,
                                uint8_t reg_addr,
                                const uint8_t *data,
                                size_t len) {
    if (!cfg || (len > 0 && !data)) {
        return ESP_ERR_INVALID_ARG;
    }

    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    if (!cmd) {
        return ESP_ERR_NO_MEM;
    }

    // Формування послідовності: START -> ADDR+WRITE -> REG_ADDR -> DATA -> STOP
    esp_err_t err = i2c_master_start(cmd);
    if (err == ESP_OK) {
        err = i2c_master_write_byte(cmd, (dev_addr << 1) | I2C_MASTER_WRITE, true);
    }
    if (err == ESP_OK) {
        err = i2c_master_write_byte(cmd, reg_addr, true);
    }
    if (err == ESP_OK && len > 0) {
        err = i2c_master_write(cmd, (uint8_t *)data, len, true);
    }
    if (err == ESP_OK) {
        err = i2c_master_stop(cmd);
    }

    if (err == ESP_OK) {
        TickType_t ticks_to_wait = pdMS_TO_TICKS(cfg->timeout_ms > 0 ? cfg->timeout_ms : 50);
        err = i2c_master_cmd_begin(cfg->port, cmd, ticks_to_wait);
    }

    i2c_cmd_link_delete(cmd);

    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Помилка запису в пристрій 0x%02X, регістр 0x%02X: %s",
                 dev_addr, reg_addr, esp_err_to_name(err));
    }
    return err;
}

esp_err_t i2c_shifter_read_reg(const i2c_shifter_config_t *cfg,
                               uint8_t dev_addr,
                               uint8_t reg_addr,
                               uint8_t *data,
                               size_t len) {
    if (!cfg || !data || len == 0) {
        return ESP_ERR_INVALID_ARG;
    }

    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    if (!cmd) {
        return ESP_ERR_NO_MEM;
    }

    // Послідовність: START -> ADDR+WRITE -> REG_ADDR -> REPEATED_START -> ADDR+READ -> READ_BYTES -> STOP
    esp_err_t err = i2c_master_start(cmd);
    if (err == ESP_OK) {
        err = i2c_master_write_byte(cmd, (dev_addr << 1) | I2C_MASTER_WRITE, true);
    }
    if (err == ESP_OK) {
        err = i2c_master_write_byte(cmd, reg_addr, true);
    }
    if (err == ESP_OK) {
        err = i2c_master_start(cmd); // Повторний START для перемикання напрямку
    }
    if (err == ESP_OK) {
        err = i2c_master_write_byte(cmd, (dev_addr << 1) | I2C_MASTER_READ, true);
    }
    if (err == ESP_OK) {
        if (len > 1) {
            err = i2c_master_read(cmd, data, len - 1, I2C_MASTER_ACK);
        }
        if (err == ESP_OK) {
            err = i2c_master_read_byte(cmd, data + len - 1, I2C_MASTER_NACK);
        }
    }
    if (err == ESP_OK) {
        err = i2c_master_stop(cmd);
    }

    if (err == ESP_OK) {
        TickType_t ticks_to_wait = pdMS_TO_TICKS(cfg->timeout_ms > 0 ? cfg->timeout_ms : 50);
        err = i2c_master_cmd_begin(cfg->port, cmd, ticks_to_wait);
    }

    i2c_cmd_link_delete(cmd);

    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Помилка читання з пристрою 0x%02X, регістр 0x%02X: %s",
                 dev_addr, reg_addr, esp_err_to_name(err));
    }
    return err;
}

esp_err_t i2c_shifter_deinit(i2c_port_t port) {
    esp_err_t err = i2c_driver_delete(port);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "I2C порт %d деініціалізовано", port);
    }
    return err;
}
