#include "Ch340Bridge.hpp"

#if defined(ESP_PLATFORM)
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#elif defined(ARDUINO)
#include <Arduino.h>
#else
#include <thread>
#include <chrono>
#include <iostream>
#endif

// Конфігурація послідовного порту та індикатора для мосту CH340
static const ch340::UartConfig g_uart_config{
    .baud_rate = 115200,
    .rx_pin = 16,
    .tx_pin = 17,
    .uart_port = 1,
    .rx_buffer_size = 1024,
    .tx_buffer_size = 1024
};

static const ch340::IndicatorConfig g_indicator_config{
    .led_pin = 2,
    .active_high = true,
    .activity_timeout_ms = 150
};

// Екземпляр мосту CH340
static ch340::Ch340Bridge g_ch340_bridge(g_uart_config, g_indicator_config);

#if defined(ESP_PLATFORM)

extern "C" void app_main(void) {
    ESP_LOGI("MAIN", "Запуск прошивки перевірки CH340 USB-UART (ESP-IDF)...");

    if (!g_ch340_bridge.begin()) {
        ESP_LOGE("MAIN", "Критична помилка ініціалізації CH340 Bridge!");
        return;
    }

    ESP_LOGI("MAIN", "Міст CH340 успішно налаштовано на 115200 бод. Готовий до ретрансляції.");

    while (true) {
        g_ch340_bridge.update();
        vTaskDelay(pdMS_TO_TICKS(10)); // Пауза 10 мс для запобігання блокуванню планувальника
    }
}

#elif defined(ARDUINO)

void setup() {
    // Ініціалізація апаратного мосту CH340 у середовищі Arduino
    g_ch340_bridge.begin();
}

void loop() {
    // Обробка ехо-байтів та оновлення таймера індикації
    g_ch340_bridge.update();
    delay(5);
}

#else

int main() {
    std::cout << "Запуск тестового середовища CH340 USB-UART Bridge (Desktop Simulation)...\n";
    if (!g_ch340_bridge.begin()) {
        std::cerr << "Помилка ініціалізації мосту!\n";
        return 1;
    }

    std::cout << "Міст ініціалізовано. Запуск циклу перевірки...\n";
    for (int i = 0; i < 100; ++i) {
        g_ch340_bridge.update();
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    std::cout << "Тестовий цикл завершено. Оброблено байтів: "
              << g_ch340_bridge.getTotalBytesProcessed() << "\n";
    return 0;
}

#endif
