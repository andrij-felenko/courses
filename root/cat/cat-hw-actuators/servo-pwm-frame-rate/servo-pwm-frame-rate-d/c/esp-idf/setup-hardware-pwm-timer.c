// Налаштування прецизійного апаратного таймера STM32 / ESP32 для усунення дрижання ШІМ-кадру в C
#include <stdio.h>
#include "driver/gptimer.h"
#include "driver/gpio.h"

// Структура конфігурації апаратного таймера з точністю 1 мкс
void setup_hardware_pwm_timer(void) {
    gptimer_handle_t gptimer = NULL;
    gptimer_config_t timer_config = {
        .clk_src = GPTIMER_CLK_SRC_DEFAULT,
        .direction = GPTIMER_COUNT_UP,
        .resolution_hz = 1000000, // 1 МГц (1 крок = 1 мкс)
    };
    gptimer_new_timer(&timer_config, &gptimer);

    gptimer_alarm_config_t alarm_config = {
        .alarm_count = 20000, // Період кадру T_frame = 20000 мкс (50 Гц)
        .reload_count = 0,
        .flags.auto_reload_on_alarm = true,
    };
    gptimer_set_alarm_action(gptimer, &alarm_config);
    gptimer_enable(gptimer);
    gptimer_start(gptimer);
}
