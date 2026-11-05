#include <stdio.h>
#include "esp_sleep.h"
#include "driver/i2c.h"
#include "esp_log.h"

#define I2C_PORT         I2C_NUM_0
#define I2C_SDA_PIN      GPIO_NUM_21
#define I2C_SCL_PIN      GPIO_NUM_22
#define AHT20_ADDR       0x38
#define SLEEP_SEC        60

// Змінні у пам'яті RTC SRAM зберігаються під час Deep Sleep
RTC_DATA_ATTR static uint32_t boot_count = 0;
RTC_DATA_ATTR static float last_temp = 0.0f;
RTC_DATA_ATTR static float last_hum = 0.0f;

static uint8_t aht20_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++) {
            crc = (crc & 0x80) ? ((crc << 1) ^ 0x31) : (crc << 1);
        }
    }
    return crc;
}

void app_main(void) {
    boot_count++;

    // Налаштування та запуск шини I2C
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_SDA_PIN,
        .scl_io_num = I2C_SCL_PIN,
        .sda_pullup_en = GPIO_PULLUP_DISABLE,
        .scl_pullup_en = GPIO_PULLUP_DISABLE,
        .master.clk_speed = 100000
    };
    i2c_param_config(I2C_PORT, &conf);
    i2c_driver_install(I2C_PORT, conf.mode, 0, 0, 0);

    // Команда запуску вимірювання: 0xAC, 0x33, 0x00
    uint8_t cmd[3] = {0xAC, 0x33, 0x00};
    i2c_master_write_to_device(I2C_PORT, AHT20_ADDR, cmd, sizeof(cmd), pdMS_TO_TICKS(50));

    // Енергозберігаюче очікування: легкий сон на 80 мс замість активного циклу
    esp_sleep_enable_timer_wakeup(80ULL * 1000ULL);
    esp_light_sleep_start();

    // Зчитування 7 байтів: статус, 20 біт вологості, 20 біт температури, CRC
    uint8_t rx[7] = {0};
    esp_err_t err = i2c_master_read_from_device(I2C_PORT, AHT20_ADDR, rx, sizeof(rx), pdMS_TO_TICKS(50));

    if (err == ESP_OK && !(rx[0] & 0x80) && (aht20_crc8(rx, 6) == rx[6])) {
        uint32_t raw_hum = (((uint32_t)rx[1] << 16) | ((uint32_t)rx[2] << 8) | rx[3]) >> 4;
        uint32_t raw_temp = (((uint32_t)(rx[3] & 0x0F) << 16) | ((uint32_t)rx[4] << 8) | rx[5]);

        last_hum = ((float)raw_hum / 1048576.0f) * 100.0f;
        last_temp = ((float)raw_temp / 1048576.0f) * 200.0f - 50.0f;
    }

    // Звільнення шини перед глибоким сном
    i2c_driver_delete(I2C_PORT);

    // Встановлення тривалого сну на 60 секунд
    esp_sleep_enable_timer_wakeup((uint64_t)SLEEP_SEC * 1000000ULL);
    esp_deep_sleep_start();
}
