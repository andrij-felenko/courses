#include <string>
#include "esp_sleep.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sx1262.hpp"

namespace {
    constexpr char TAG[] = "MAIN";
    constexpr uint64_t SLEEP_TIME_SEC = 60;
    
    constexpr int PIN_MISO = 13;
    constexpr int PIN_MOSI = 11;
    constexpr int PIN_CLK  = 12;
    constexpr int PIN_CS   = 10;
    constexpr int PIN_BUSY = 9;

    float readTemperatureSensor() {
        return 24.5f; 
    }
}

extern "C" void app_main() {
    ESP_LOGI(TAG, "Wake up! Initiating node work cycle.");

    {
        // Конструктор ініціалізує SPI шину, деструктор - звільнить при виході з області
        SX1262 radio(PIN_MISO, PIN_MOSI, PIN_CLK, PIN_CS, PIN_BUSY);

        if (!radio.init()) {
            ESP_LOGE(TAG, "SX1262 initialization failed");
        } else {
            float temp = readTemperatureSensor();
            
            std::string payload = R"({"t": )" + std::to_string(temp) + "}";
            ESP_LOGI(TAG, "Sending data: %s", payload.c_str());
            
            std::span<const uint8_t> data(
                reinterpret_cast<const uint8_t*>(payload.data()), 
                payload.size()
            );
            
            radio.transmit(data);
            vTaskDelay(pdMS_TO_TICKS(500));
        }
    }

    ESP_LOGI(TAG, "Entering deep sleep for %llu seconds...", SLEEP_TIME_SEC);
    esp_sleep_enable_timer_wakeup(SLEEP_TIME_SEC * 1'000'000ULL);
    esp_deep_sleep_start();
}
