#include <stdint.h>
#include <stdbool.h>
#include "driver/gptimer.h"
#include "driver/gpio.h"

#define STEP_GPIO_PIN GPIO_NUM_18
#define DIR_GPIO_PIN  GPIO_NUM_19
#define DDA_SHIFT     16

typedef struct {
    uint32_t step_ratio_fp; // Дробовий крок DDA у форматі Q16.16
    uint32_t accumulator;   // Акумулятор похибки DDA
    uint32_t base_period;   // Базовий період таймера в тактах
    gptimer_handle_t timer; // Хендл апаратного таймера
} dda_axis_t;

static dda_axis_t g_axis;

// Обробник переривання таймера з мінімальним часом виконання
static bool IRAM_ATTR dda_timer_isr_callback(gptimer_handle_t timer, 
                                             const gptimer_alarm_event_data_t *edata, 
                                             void *user_ctx) {
    dda_axis_t *axis = (dda_axis_t *)user_ctx;
    
    // Перемикаємо імпульс кроку на виході GPIO
    gpio_set_level(STEP_GPIO_PIN, 1);
    
    // Обчислення наступного інтервалу за алгоритмом DDA
    axis->accumulator += axis->step_ratio_fp;
    uint32_t period_correction = axis->accumulator >> DDA_SHIFT;
    axis->accumulator &= ((1U << DDA_SHIFT) - 1);
    
    uint32_t next_period = axis->base_period + period_correction;
    
    // Оновлюємо поріг спрацьовування таймера для наступного кроку
    gptimer_alarm_config_t alarm_config = {
        .alarm_count = edata->alarm_value + next_period,
        .reload_count = 0,
        .flags.auto_reload_on_alarm = false,
    };
    gptimer_set_alarm_action(timer, &alarm_config);
    
    // Скидаємо рівень імпульсу (формування короткого стробу)
    gpio_set_level(STEP_GPIO_PIN, 0);
    
    return false;
}
