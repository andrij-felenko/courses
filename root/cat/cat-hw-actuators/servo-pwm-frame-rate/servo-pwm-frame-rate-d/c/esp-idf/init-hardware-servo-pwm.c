// Прецизійне налаштування апаратного ШІМ-генератора для сервоприводів у C (ESP-IDF / MCPWM)
#include <stdio.h>
#include "driver/mcpwm_prelude.h"

// Функція ініціалізації апаратного ШІМ-каналу 50 Гц з точністю до 1 мікросекунди
void init_hardware_servo_pwm(void) {
    mcpwm_timer_handle_t timer = NULL;
    mcpwm_timer_config_t timer_config = {
        .group_id = 0,
        .clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT,
        .resolution_hz = 1000000, // Роздільна здатність 1 МГц (1 крок = 1 мкс)
        .period_ticks = 20000,    // Період кадру T_frame = 20000 мкс (20 мс / 50 Гц)
        .count_mode = MCPWM_TIMER_COUNT_MODE_UP,
    };
    mcpwm_new_timer(&timer_config, &timer);

    mcpwm_oper_handle_t oper = NULL;
    mcpwm_operator_config_t operator_config = { .group_id = 0 };
    mcpwm_new_operator(&operator_config, &oper);
    mcpwm_operator_connect_timer(oper, timer);

    mcpwm_cmpr_handle_t comparator = NULL;
    mcpwm_comparator_config_t comparator_config = { .flags.update_cmp_on_tez = true };
    mcpwm_new_comparator(oper, &comparator_config, &comparator);

    // Встановлення нейтральної тривалості імпульсу 1.5 мс (1500 мкс) без участі CPU
    mcpwm_comparator_set_compare_value(comparator, 1500);
    mcpwm_timer_enable(timer);
    mcpwm_timer_start_stop(timer, MCPWM_TIMER_START_NO_STOP);
}
