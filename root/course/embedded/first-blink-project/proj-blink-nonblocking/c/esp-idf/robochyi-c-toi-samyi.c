#include <stdbool.h>
#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LED_PIN  GPIO_NUM_2          // той самий GPIO2
#define INTERVAL 200                 // період перемикання, мілісекунди

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << LED_PIN,
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&cfg);               // ніжка на вихід — один раз

    uint32_t lastToggle = 0;         // мітка часу останнього перемикання
    bool ledOn = false;              // нинішній стан світлодіода

    while (1) {
        // лічильник дає мікросекунди — переводимо в мілісекунди
        uint32_t now = (uint32_t)(esp_timer_get_time() / 1000);

        if (now - lastToggle >= INTERVAL) {
            lastToggle = now;        // ПЕРЕСУНУЛИ мітку на теперішній час
            ledOn = !ledOn;          // перемкнули логічний стан
            gpio_set_level(LED_PIN, ledOn ? 1 : 0);
        }

        // сюди керування доходить ЩОРАЗУ — і між перемиканнями теж.
        vTaskDelay(1);               // один такт іншим задачам, а не пауза «на 200 мс»
    }
}
