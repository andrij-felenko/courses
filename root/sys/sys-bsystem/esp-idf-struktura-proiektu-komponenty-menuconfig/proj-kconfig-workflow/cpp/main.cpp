// Приклад споживання в main/main.cpp (C++)
#include <iostream>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sensor_driver.hpp"

static const char *TAG = "main_app";

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "Запуск C++ вузла моніторингу...");

    // Створення RAII-екземпляра сенсора
    sensors::EnvironmentSensor sensor;

    if (!sensor.is_ready()) {
        ESP_LOGE(TAG, "Помилка: не вдалося ініціалізувати апаратний сенсор");
        return;
    }

    for (int i = 0; i < 3; ++i) {
        auto result = sensor.read();
        if (result.has_value()) {
            const auto& data = result.value();
            std::cout << "[Вимір #" << (i + 1) << " | " << data.timestamp_ms << " мс] "
                      << "Температура: " << data.temperature_celsius << " °C, "
                      << "Вологість: " << data.humidity_percent << " %\n";
        } else {
            ESP_LOGW(TAG, "Збій опитування датчика, помилка: %d", result.error());
        }
        vTaskDelay(pdMS_TO_TICKS(1000));
    }

    ESP_LOGI(TAG, "Завершення сесії: деініціалізація відбудеться автоматично через деструктор RAII.");
}
