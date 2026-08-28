#include "driver/i2c.h"
#include "esp_log.h"

#define HMC      0x1E                  // 7-бітна I²C-адреса HMC5883L
#define PORT     I2C_NUM_0
#define TMO      pdMS_TO_TICKS(100)

static esp_err_t hmc_write_reg(uint8_t reg, uint8_t val) {
    uint8_t buf[2] = { reg, val };
    return i2c_master_write_to_device(PORT, HMC, buf, sizeof(buf), TMO);
}

esp_err_t hmc_init(void) {
    i2c_config_t cfg = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = 21, .scl_io_num = 22,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,   // підтяжки є й на самій платі
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 100000,            // 100 кГц
    };
    ESP_ERROR_CHECK(i2c_param_config(PORT, &cfg));
    ESP_ERROR_CHECK(i2c_driver_install(PORT, cfg.mode, 0, 0, 0));

    ESP_ERROR_CHECK(hmc_write_reg(0x00, 0x70));   // Config A: 8 усереднень, 15 Гц
    ESP_ERROR_CHECK(hmc_write_reg(0x01, 0x20));   // Config B: підсилення ±1.3 Гаус
    return hmc_write_reg(0x02, 0x00);             // Mode: безперервний вимір
}

esp_err_t hmc_read(int16_t *x, int16_t *y, int16_t *z) {
    uint8_t reg = 0x03, b[6];                     // 6 байтів: X, Z, Y (саме такий порядок!)
    esp_err_t err = i2c_master_write_read_device(PORT, HMC, &reg, 1, b, sizeof(b), TMO);
    if (err != ESP_OK) { ESP_LOGE("hmc", "читання не вдалося: %s", esp_err_to_name(err)); return err; }
    *x = (int16_t)((b[0] << 8) | b[1]);
    *z = (int16_t)((b[2] << 8) | b[3]);           // Z йде ДРУГИМ, не третім
    *y = (int16_t)((b[4] << 8) | b[5]);
    return ESP_OK;
}
