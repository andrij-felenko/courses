#include <cstdio>
#include "esp_log.h"
#include "esp_sleep.h"
#include "nvs_flash.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "sensor_node.hpp"
#include "network_node.hpp"

static const char* TAG = "MainApp";

// Інтервал режиму глибокого сну у секундах
constexpr uint64_t SLEEP_INTERVAL_SEC = 30;

// Змінна RTC для збереження лічильника пробуджень між сесіями сну
RTC_DATA_ATTR static uint32_t g_boot_sequence = 0;

extern "C" void app_main(void) {
    g_boot_sequence++;
    ESP_LOGI(TAG, "=== Запуск WeAct ESP32-C6-Mini (Цикл #%lu) ===", g_boot_sequence);

    // Визначення джерела пробудження
    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
    switch (wakeup_reason) {
        case ESP_SLEEP_WAKEUP_TIMER:
            ESP_LOGI(TAG, "Пробудження за таймером RTC");
            break;
        case ESP_SLEEP_WAKEUP_UNDEFINED:
        default:
            ESP_LOGI(TAG, "Початковий запуск (Power-on Reset)");
            break;
    }

    // Ініціалізація енергонезалежного сховища NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // 1. Зчитування вимірювань із сенсорної периферії
    iot::SensorNode sensor_node(GPIO_NUM_6, GPIO_NUM_7, ADC_CHANNEL_2);
    if (sensor_node.initialize() == ESP_OK) {
        auto measurements = sensor_node.read_measurements(g_boot_sequence);

        if (measurements.has_value()) {
            auto payload_buffer = iot::SensorNode::encode_payload(measurements.value());

            // 2. Ініціалізація 802.15.4 та відправка пакета даних
            iot::NetworkConfig net_cfg{
                .channel = 15,
                .pan_id = 0x1234,
                .short_addr = 0x0002,
                .dest_addr = 0x0001,
                .tx_power_dbm = 20
            };

            iot::NetworkNode network_node(net_cfg);
            if (network_node.initialize() == ESP_OK) {
                esp_err_t tx_err = network_node.transmit_data(payload_buffer);
                if (tx_err != ESP_OK) {
                    ESP_LOGE(TAG, "Помилка передачі корисного навантаження");
                }

                // Вимкнення радіомодуля перед переходом у сон
                network_node.disable_radio();
            } else {
                ESP_LOGE(TAG, "Помилка відкриття бездротового стеку 802.15.4");
            }
        } else {
            ESP_LOGE(TAG, "Не вдалося отримати вимірювання від сенсора");
        }
    } else {
        ESP_LOGE(TAG, "Помилка ініціалізації периферійних модулів сенсора");
    }

    // 3. Налаштування таймера RTC та вхід у Deep Sleep
    ESP_LOGI(TAG, "Заплановано Deep Sleep на %llu сек...", SLEEP_INTERVAL_SEC);
    ESP_ERROR_CHECK(esp_sleep_enable_timer_wakeup(SLEEP_INTERVAL_SEC * 1000000ULL));

    esp_deep_sleep_start();
}
