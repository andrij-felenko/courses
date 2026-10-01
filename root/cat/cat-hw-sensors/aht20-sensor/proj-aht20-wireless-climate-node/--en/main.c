#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "esp_sleep.h"
#include "esp_now.h"
#include "esp_wifi.h"
#include "nvs_flash.h"
#include "esp_log.h"

#define SENSOR_POWER_PIN GPIO_NUM_4
#define I2C_MASTER_SCL_IO 22
#define I2C_MASTER_SDA_IO 21
#define I2C_MASTER_NUM I2C_NUM_0
#define I2C_MASTER_FREQ_HZ 100000
#define AHT20_ADDR 0x38

#define SLEEP_DURATION_SEC 60

static const char *TAG = "CLIMATE_NODE_C";

// MAC-адреса шлюзу приймача ESP-NOW
static uint8_t receiver_mac[] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

typedef struct {
    float humidity;
    float temperature;
    uint32_t reading_id;
} climate_packet_t;

RTC_DATA_ATTR static uint32_t boot_count = 0;

static uint8_t calculate_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

static esp_err_t i2c_master_init(void) {
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };
    esp_err_t err = i2c_param_config(I2C_MASTER_NUM, &conf);
    if (err != ESP_OK) return err;
    return i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
}

static esp_err_t aht20_read_sensor(float *humidity, float *temperature) {
    // 1. Команда ініціалізації
    uint8_t init_cmd[3] = {0xBE, 0x08, 0x00};
    i2c_master_write_to_device(I2C_MASTER_NUM, AHT20_ADDR, init_cmd, sizeof(init_cmd), pdMS_TO_TICKS(100));
    vTaskDelay(pdMS_TO_TICKS(10));

    // 2. Команда тригера вимірювання
    uint8_t trigger_cmd[3] = {0xAC, 0x33, 0x00};
    esp_err_t err = i2c_master_write_to_device(I2C_MASTER_NUM, AHT20_ADDR, trigger_cmd, sizeof(trigger_cmd), pdMS_TO_TICKS(100));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка надсилання тригера I2C: %s", esp_err_to_name(err));
        return err;
    }

    // Затримка 80 мс на виконання вимірювання сенсором
    vTaskDelay(pdMS_TO_TICKS(80));

    // 3. Зчитування 7 байтів
    uint8_t rx_buf[7] = {0};
    err = i2c_master_read_from_device(I2C_MASTER_NUM, AHT20_ADDR, rx_buf, sizeof(rx_buf), pdMS_TO_TICKS(100));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка зчитування даних I2C: %s", esp_err_to_name(err));
        return err;
    }

    // Перевірка готовності (Busy Bit[7] == 0)
    if (rx_buf[0] & 0x80) {
        ESP_LOGE(TAG, "Сенсор AHT20 все ще зайнятий!");
        return ESP_ERR_INVALID_STATE;
    }

    // Перевірка контрольної суми CRC-8
    uint8_t calc_crc = calculate_crc8(rx_buf, 6);
    if (calc_crc != rx_buf[6]) {
        ESP_LOGE(TAG, "Незбіг CRC8: обчислено 0x%02X, отримано 0x%02X", calc_crc, rx_buf[6]);
        return ESP_ERR_INVALID_CRC;
    }

    // Розпакування 20-бітних даних
    uint32_t raw_hum = ((uint32_t)rx_buf[1] << 12) | ((uint32_t)rx_buf[2] << 4) | ((uint32_t)rx_buf[3] >> 4);
    uint32_t raw_temp = (((uint32_t)rx_buf[3] & 0x0F) << 16) | ((uint32_t)rx_buf[4] << 8) | (uint32_t)rx_buf[5];

    *humidity = ((float)raw_hum / 1048576.0f) * 100.0f;
    *temperature = ((float)raw_temp / 1048576.0f) * 200.0f - 50.0f;

    return ESP_OK;
}

static void init_esp_now(void) {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_start();

    if (esp_now_init() != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації ESP-NOW");
        return;
    }

    esp_now_peer_info_t peer_info = {0};
    memcpy(peer_info.peer_addr, receiver_mac, 6);
    peer_info.channel = 0;
    peer_info.encrypt = false;
    esp_now_add_peer(&peer_info);
}

void app_main(void) {
    boot_count++;
    ESP_LOGI(TAG, "Запуск вузла клімату C (Завантаження #%lu)", boot_count);

    // Подача живлення на AHT20 через GPIO
    gpio_config_t pwr_cfg = {
        .pin_bit_mask = (1ULL << SENSOR_POWER_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&pwr_cfg);
    gpio_set_level(SENSOR_POWER_PIN, 1);

    // Пауза 100 мс після подачі живлення
    vTaskDelay(pdMS_TO_TICKS(100));

    // Ініціалізація I2C
    if (i2c_master_init() == ESP_OK) {
        float hum = 0.0f, temp = 0.0f;
        if (aht20_read_sensor(&hum, &temp) == ESP_OK) {
            ESP_LOGI(TAG, "Виміряно: Вологість = %.2f %%, Температура = %.2f °C", hum, temp);

            init_esp_now();

            climate_packet_t packet = {
                .humidity = hum,
                .temperature = temp,
                .reading_id = boot_count
            };

            esp_now_send(receiver_mac, (uint8_t *)&packet, sizeof(packet));
            vTaskDelay(pdMS_TO_TICKS(50));
        }
        i2c_driver_delete(I2C_MASTER_NUM);
    }

    // Вимкнення живлення сенсора перед сном
    gpio_set_level(SENSOR_POWER_PIN, 0);

    // Конфігурація та перехід у Deep Sleep
    ESP_LOGI(TAG, "Перехід у Deep Sleep на %d секунд", SLEEP_DURATION_SEC);
    esp_sleep_enable_timer_wakeup(SLEEP_DURATION_SEC * 1000000ULL);
    esp_deep_sleep_start();
}
