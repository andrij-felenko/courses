#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SOL_PIN   GPIO_NUM_5       // ніжка на затвор MOSFET (або на IN ULN2003)
#define PULSE_MS  60               // скільки тримати втягнутим на один клац

void solenoid_init(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << SOL_PIN,
        .mode         = GPIO_MODE_OUTPUT,
    };
    gpio_config(&cfg);
    gpio_set_level(SOL_PIN, 0);
}

void solenoid_fire(void) {
    gpio_set_level(SOL_PIN, 1);            // втягуємо осердя
    vTaskDelay(pdMS_TO_TICKS(PULSE_MS));   // тримаємо, поки шток дійде до упору
    gpio_set_level(SOL_PIN, 0);            // відпускаємо — пружина виштовхне назад
}
