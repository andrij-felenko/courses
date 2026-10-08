#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define PIN_KM1_FORWARD  GPIO_NUM_18
#define PIN_KM2_REVERSE  GPIO_NUM_19
#define DEAD_TIME_MS     500

typedef enum {
    MOTOR_STOP = 0,
    MOTOR_FORWARD,
    MOTOR_REVERSE
} motor_state_t;

static motor_state_t current_state = MOTOR_STOP;

void motor_init(void) {
    gpio_reset_pin(PIN_KM1_FORWARD);
    gpio_reset_pin(PIN_KM2_REVERSE);
    gpio_set_direction(PIN_KM1_FORWARD, GPIO_MODE_OUTPUT);
    gpio_set_direction(PIN_KM2_REVERSE, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_KM1_FORWARD, 0);
    gpio_set_level(PIN_KM2_REVERSE, 0);
}

bool motor_set_direction(motor_state_t new_state) {
    if (current_state == new_state) {
        return true;
    }

    // Знімаємо напругу з обох котушок керування
    gpio_set_level(PIN_KM1_FORWARD, 0);
    gpio_set_level(PIN_KM2_REVERSE, 0);

    // Обов'язкова пауза для гасіння дуги та розмикання контактів
    vTaskDelay(pdMS_TO_TICKS(DEAD_TIME_MS));

    if (new_state == MOTOR_FORWARD) {
        gpio_set_level(PIN_KM1_FORWARD, 1);
    } else if (new_state == MOTOR_REVERSE) {
        gpio_set_level(PIN_KM2_REVERSE, 1);
    }

    current_state = new_state;
    return true;
}
