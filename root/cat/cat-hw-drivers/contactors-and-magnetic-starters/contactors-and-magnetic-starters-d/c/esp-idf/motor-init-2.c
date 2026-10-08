#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define GPIO_FORWARD_COIL   GPIO_NUM_18
#define GPIO_REVERSE_COIL   GPIO_NUM_19
#define GPIO_FORWARD_SENSE  GPIO_NUM_21
#define GPIO_REVERSE_SENSE  GPIO_NUM_22

#define DEAD_TIME_MS        150

typedef enum {
    MOTOR_STOPPED,
    MOTOR_FORWARD,
    MOTOR_REVERSE
} motor_state_t;

static motor_state_t current_state = MOTOR_STOPPED;

void motor_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_FORWARD_COIL) | (1ULL << GPIO_REVERSE_COIL),
        .mode = GPIO_MODE_OUTPUT,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    
    gpio_set_level(GPIO_FORWARD_COIL, 0);
    gpio_set_level(GPIO_REVERSE_COIL, 0);

    gpio_config_t sense_conf = {
        .pin_bit_mask = (1ULL << GPIO_FORWARD_SENSE) | (1ULL << GPIO_REVERSE_SENSE),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&sense_conf);
}

bool set_motor_direction(motor_state_t target_state) {
    if (current_state == target_state) {
        return true;
    }

    // Знеструмлення обох котушок для безпечного розмикання
    gpio_set_level(GPIO_FORWARD_COIL, 0);
    gpio_set_level(GPIO_REVERSE_COIL, 0);
    current_state = MOTOR_STOPPED;

    // Пауза dead-time для гасіння дуги та механічного відпадання якоря
    vTaskDelay(pdMS_TO_TICKS(DEAD_TIME_MS));

    // Перевірка стану допоміжних NC-контактів (активний низький рівень)
    if (gpio_get_level(GPIO_FORWARD_SENSE) != 0 || gpio_get_level(GPIO_REVERSE_SENSE) != 0) {
        // Захисна відмова: один з контакторів не розімкнувся
        return false;
    }

    if (target_state == MOTOR_FORWARD) {
        gpio_set_level(GPIO_FORWARD_COIL, 1);
        current_state = MOTOR_FORWARD;
    } else if (target_state == MOTOR_REVERSE) {
        gpio_set_level(GPIO_REVERSE_COIL, 1);
        current_state = MOTOR_REVERSE;
    }

    return true;
}
