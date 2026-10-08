/* 
 * ESP-IDF приклад керування кроковим приводом перистальтичного дозатора.
 * Забезпечує генерування імпульсів STEP/DIR із розгоном для запобігання пропуску кроків.
 */

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "rom/ets_sys.h"

#define GPIO_STEP_PIN  GPIO_NUM_18
#define GPIO_DIR_PIN   GPIO_NUM_19
#define GPIO_EN_PIN    GPIO_NUM_5

// Калібрувальний коефіцієнт: кількість мікрокроків на 1 мл рідини
#define STEPS_PER_ML   3200ULL 

void peristaltic_dosing_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_STEP_PIN) | (1ULL << GPIO_DIR_PIN) | (1ULL << GPIO_EN_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    
    // Деактивуємо драйвер (активний 0)
    gpio_set_level(GPIO_EN_PIN, 1);
}

void peristaltic_dose_volume(float volume_ml, bool direction) {
    uint64_t total_steps = (uint64_t)(volume_ml * STEPS_PER_ML);
    gpio_set_level(GPIO_DIR_PIN, direction ? 1 : 0);
    gpio_set_level(GPIO_EN_PIN, 0); // Увімкнути драйвер

    uint32_t delay_us = 500; // Початкова затримка між імпульсами (розгін)
    uint32_t min_delay_us = 100; // Мінімальна затримка на робочій швидкості

    for (uint64_t step = 0; step < total_steps; step++) {
        gpio_set_level(GPIO_STEP_PIN, 1);
        ets_delay_us(2);
        gpio_set_level(GPIO_STEP_PIN, 0);

        // Лінійний профіль розгону та гальмування
        if (step < 200 && delay_us > min_delay_us) {
            delay_us -= 2;
        } else if (step > (total_steps - 200) && delay_us < 500) {
            delay_us += 2;
        }

        ets_delay_us(delay_us);
    }

    gpio_set_level(GPIO_EN_PIN, 1); // Вимкнути драйвер після завершення
}
