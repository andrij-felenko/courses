#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"
#include "esp_attr.h"

#define STEP_PIN_AXIS_X  GPIO_NUM_21
#define DIR_PIN_AXIS_X   GPIO_NUM_22
#define ISR_FREQ_HZ      100000ULL // 100 кГц (10 мкс)

// Структура стану DDA-генератора для однієї осі
typedef struct {
    uint32_t accumulator; // 32-бітовий акумулятор дробової частини
    uint32_t increment;   // Приріст фази за один такт ISR (delta_A)
    uint32_t step_count;  // Загальний лічильник виконаних кроків
    bool step_active;     // Прапор активного стану імпульсу STEP
} dda_axis_state_t;

static volatile dda_axis_state_t g_axis_x = {
    .accumulator = 0,
    .increment = 0,
    .step_count = 0,
    .step_active = false
};

// Функція розрахунку приросту акумулятора для заданої частоти кроків
uint32_t dda_calculate_increment(uint32_t target_step_freq_hz) {
    if (target_step_freq_hz >= ISR_FREQ_HZ) {
        return 0xFFFFFFFF; // Обмеження за частотою Найквіста/квантування
    }
    uint64_t calc = ((uint64_t)target_step_freq_hz << 32) / ISR_FREQ_HZ;
    return (uint32_t)calc;
}

// Високочастотний обробник переривань таймера (викликається кожні 10 мкс)
void IRAM_ATTR dda_timer_isr_step_handler(void* arg) {
    dda_axis_state_t* axis = (dda_axis_state_t*)arg;

    // 1. Атомарне зняття імпульсу STEP з попереднього такту
    if (axis->step_active) {
        gpio_set_level(STEP_PIN_AXIS_X, 0);
        axis->step_active = false;
    }

    // 2. Якщо приріст дорівнює 0, вісь не рухається
    if (axis->increment == 0) {
        return;
    }

    // 3. Накопичення цілочисельного приросту з фіксованою комою
    uint32_t prev_acc = axis->accumulator;
    axis->accumulator += axis->increment;

    // 4. Детекція переповнення розрядної сітки 32-бітного акумулятора
    if (axis->accumulator < prev_acc) { // Виникло переповнення (acc >= 2^32)
        gpio_set_level(STEP_PIN_AXIS_X, 1);
        axis->step_active = true;
        axis->step_count++;
    }
}
