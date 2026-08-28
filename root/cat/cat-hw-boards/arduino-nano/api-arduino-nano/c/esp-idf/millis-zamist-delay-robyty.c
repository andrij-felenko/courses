#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_LED GPIO_NUM_2
#define PIN_BTN GPIO_NUM_4
static const char *TAG = "app";

// задача 1: блимати раз на секунду, нікого не блокуючи
static void led_task(void *arg) {
    bool on = false;
    while (1) {
        on = !on;
        gpio_set_level(PIN_LED, on);
        vTaskDelay(pdMS_TO_TICKS(1000));   // спить ЦЯ задача, не весь чип
    }
}

// задача 2: слати число щопівсекунди
static void log_task(void *arg) {
    while (1) {
        ESP_LOGI(TAG, "%d", (int)xTaskGetTickCount());
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

void app_main(void) {
    gpio_set_direction(PIN_LED, GPIO_MODE_OUTPUT);
    gpio_set_direction(PIN_BTN, GPIO_MODE_INPUT);
    gpio_set_pull_mode(PIN_BTN, GPIO_PULLUP_ONLY);

    xTaskCreate(led_task, "led", 2048, NULL, 5, NULL);
    xTaskCreate(log_task, "log", 2048, NULL, 5, NULL);

    while (1) {   // задача 3: кнопка реагує МИТТЄВО — сусіди її не глушать
        if (gpio_get_level(PIN_BTN) == 0) {
            // тут дія на натискання
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
