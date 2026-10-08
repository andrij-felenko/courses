#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define ESP_AT_RST_PIN  GPIO_NUM_4
#define ESP_AT_EN_PIN   GPIO_NUM_5

void esp_at_hardware_reset(void) {
    // Налаштування напрямку виводів керування
    gpio_set_direction(ESP_AT_EN_PIN, GPIO_MODE_OUTPUT);
    gpio_set_direction(ESP_AT_RST_PIN, GPIO_MODE_OUTPUT);

    // Початкова подача живлення та активація chip enable
    gpio_set_level(ESP_AT_EN_PIN, 1);
    vTaskDelay(pdMS_TO_TICKS(20));

    // Генерація імпульсу апаратного скидання (LOW)
    gpio_set_level(ESP_AT_RST_PIN, 0);
    vTaskDelay(pdMS_TO_TICKS(50)); // тривалість імпульсу t_RST = 50 мс
    gpio_set_level(ESP_AT_RST_PIN, 1); // відпускання лінії RST

    // Пауза t_ready для стабілізації та ініціалізації AT-прошивки
    vTaskDelay(pdMS_TO_TICKS(500));
}
