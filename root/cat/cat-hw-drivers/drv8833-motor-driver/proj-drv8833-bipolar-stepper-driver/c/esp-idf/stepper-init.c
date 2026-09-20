// Керування кроковим мотором через DRV8833 для ESP-IDF (C)
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define PIN_IN1        GPIO_NUM_18
#define PIN_IN2        GPIO_NUM_19
#define PIN_IN3        GPIO_NUM_21
#define PIN_IN4        GPIO_NUM_22
#define PIN_NSLEEP     GPIO_NUM_23

static const uint8_t half_step_table[8][4] = {
    {1, 0, 0, 0},
    {1, 0, 1, 0},
    {0, 0, 1, 0},
    {0, 1, 1, 0},
    {0, 1, 0, 0},
    {0, 1, 0, 1},
    {0, 0, 0, 1},
    {1, 0, 0, 1}
};

void stepper_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIN_IN1) | (1ULL << PIN_IN2) | 
                        (1ULL << PIN_IN3) | (1ULL << PIN_IN4) | 
                        (1ULL << PIN_NSLEEP),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    gpio_set_level(PIN_NSLEEP, 1); // Активація драйвера
}

void stepper_step(int steps, bool dir, uint32_t delay_ms) {
    static int step_idx = 0;
    for (int i = 0; i < steps; i++) {
        if (dir) {
            step_idx = (step_idx + 1) % 8;
        } else {
            step_idx = (step_idx + 7) % 8;
        }
        
        gpio_set_level(PIN_IN1, half_step_table[step_idx][0]);
        gpio_set_level(PIN_IN2, half_step_table[step_idx][1]);
        gpio_set_level(PIN_IN3, half_step_table[step_idx][2]);
        gpio_set_level(PIN_IN4, half_step_table[step_idx][3]);
        
        vTaskDelay(pdMS_TO_TICKS(delay_ms));
    }
}
