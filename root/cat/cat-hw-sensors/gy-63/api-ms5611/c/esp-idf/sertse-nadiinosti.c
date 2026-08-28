#include "esp_log.h"

static const char *TAG = "ms5611";

void app_main(void) {
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = 21,                     // будь-який вільний GPIO
        .scl_io_num = 22,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,  // модуль GY-63 має свої підтяжки
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 400000,           // MS5611 тримає до 20 МГц по SPI, 400 кГц по I2C
    };
    ESP_ERROR_CHECK(i2c_param_config(I2C_PORT, &conf));
    ESP_ERROR_CHECK(i2c_driver_install(I2C_PORT, conf.mode, 0, 0, 0));

    if (ms5611_reset() != ESP_OK)     { ESP_LOGE(TAG, "немає ACK на скид");  vTaskSuspend(NULL); }
    if (ms5611_read_prom() != ESP_OK) { ESP_LOGE(TAG, "не прочитав PROM");   vTaskSuspend(NULL); }

    if (!ms5611_prom_crc_ok(g_prom)) {
        ESP_LOGE(TAG, "CRC-4 калібрування НЕ зійшлася — коефіцієнти пошкоджені!");
        vTaskSuspend(NULL);                   // працювати з такими даними не можна
    }
    ESP_LOGI(TAG, "PROM цілий, коефіцієнти дійсні.");
}
