#include <cstdio>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "ClimateNode.hpp"

static const char* TAG = "CLIMATE_NODE_CPP";
constexpr uint32_t SLEEP_TIME_SECONDS = 60;

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "Запуск вузла клімату C++");

    ClimateNode node(GPIO_NUM_4, I2C_NUM_0);

    // 1. Подача живлення на давач AHT20
    node.powerOn();
    vTaskDelay(pdMS_TO_TICKS(100));

    // 2. Ініціалізація шини I2C та зчитування даних
    if (node.initI2C(21, 22, 100000)) {
        auto readingOpt = node.readSensor();
        if (readingOpt.has_value()) {
            const auto& reading = readingOpt.value();
            ESP_LOGI(TAG, "Успішне вимірювання C++: Вологість = %.2f %%, Температура = %.2f °C",
                     reading.humidity, reading.temperature);
        } else {
            ESP_LOGE(TAG, "Помилка вимірювання з сенсора AHT20");
        }
    } else {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати I2C");
    }

    // 3. Завершення роботи та перехід у Deep Sleep
    ESP_LOGI(TAG, "Вимкнення живлення й перехід у сон на %lu с", SLEEP_TIME_SECONDS);
    node.enterDeepSleep(SLEEP_TIME_SECONDS);
}
