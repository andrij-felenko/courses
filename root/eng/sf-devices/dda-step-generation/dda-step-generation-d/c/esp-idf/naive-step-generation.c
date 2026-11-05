#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/gptimer.h"

#define STEP_GPIO   GPIO_NUM_18
#define DIR_GPIO    GPIO_NUM_19

// --- Наївна реалізація (блокуюча) ---
void naive_step_generation(uint32_t total_steps, uint32_t delay_us) {
    gpio_set_level(DIR_GPIO, 1);
    for (uint32_t i = 0; i < total_steps; i++) {
        gpio_set_level(STEP_GPIO, 1);
        esp_rom_delay_us(2); // Мінімальна тривалість імпульсу
        gpio_set_level(STEP_GPIO, 0);
        esp_rom_delay_us(delay_us - 2); // Блокуюче очікування періоду
    }
}

// --- Детермінована реалізація через таймерне переривання ---
typedef struct {
    uint32_t step_period_ticks;
    uint32_t tick_counter;
    uint32_t target_steps;
    uint32_t current_steps;
    bool step_active;
} timer_step_config_t;

static volatile timer_step_config_t g_step_cfg = {
    .step_period_ticks = 12, // Крок кожні 12 тактів ISR (наприклад, 120 мкс при 100 кГц)
    .tick_counter = 0,
    .target_steps = 1000,
    .current_steps = 0,
    .step_active = false
};

static bool IRAM_ATTR on_timer_alarm_cb(gptimer_handle_t timer, const gptimer_alarm_event_data_t *edata, void *user_data) {
    // Скидання імпульсу STEP, якщо він був встановлений на попередньому такті
    if (g_step_cfg.step_active) {
        gpio_set_level(STEP_GPIO, 0);
        g_step_cfg.step_active = false;
    }

    if (g_step_cfg.current_steps < g_step_cfg.target_steps) {
        g_step_cfg.tick_counter++;
        if (g_step_cfg.tick_counter >= g_step_cfg.step_period_ticks) {
            g_step_cfg.tick_counter = 0;
            gpio_set_level(STEP_GPIO, 1);
            g_step_cfg.step_active = true;
            g_step_cfg.current_steps++;
        }
    }
    return false;
}
