// ESP-IDF: Налаштування шини I2C та програмної підтяжки для AHT20
#include "driver/i2c.h"

#define I2C_MASTER_SDA_IO           21    // Пін SDA мікроконтролера ESP32
#define I2C_MASTER_SCL_IO           22    // Пін SCL мікроконтролера ESP32
#define I2C_MASTER_NUM              I2C_NUM_0
#define I2C_MASTER_FREQ_HZ          400000 // Частота обміну 400 кГц (Fast Mode)

esp_err_t aht20_i2c_init(void)
{
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE, // Активуємо внутрішню підтяжку SDA
        .scl_io_num = I2C_MASTER_SCL_IO,
        .scl_pullup_en = GPIO_PULLUP_ENABLE, // Активуємо внутрішню підтяжку SCL
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };
    esp_err_t err = i2c_param_config(I2C_MASTER_NUM, &conf);
    if (err != ESP_OK) {
        return err;
    }
    return i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
}
