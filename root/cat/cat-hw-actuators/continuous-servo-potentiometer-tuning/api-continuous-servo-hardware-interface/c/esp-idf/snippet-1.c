#include "driver/mcpwm_prelude.h"

// Налаштування таймера та оператора MCPWM для генерації ШІМ-сигналу 50 Гц
mcpwm_timer_handle_t timer = NULL;
mcpwm_timer_config_t timer_config = {
    .group_id = 0,
    .clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT,
    .resolution_hz = 1000000, // Роздільна здатність 1 мкс
    .period_ticks = 20000,    // Період 20000 мкс (20 мс = 50 Гц)
    .count_mode = MCPWM_TIMER_COUNT_MODE_UP,
};
ESP_ERROR_CHECK(mcpwm_new_timer(&timer_config, &timer));

mcpwm_oper_handle_t oper = NULL;
mcpwm_operator_config_t oper_config = { .group_id = 0 };
ESP_ERROR_CHECK(mcpwm_new_operator(&oper_config, &oper));
ESP_ERROR_CHECK(mcpwm_operator_connect_timer(oper, timer));

mcpwm_cmpr_handle_t cmpr = NULL;
mcpwm_comparator_config_t cmpr_config = { .flags.update_cmp_on_tez = true };
ESP_ERROR_CHECK(mcpwm_new_comparator(oper, &cmpr_config, &cmpr));

mcpwm_gen_handle_t gen = NULL;
mcpwm_generator_config_t gen_config = { .gen_gpio_num = 18 };
ESP_ERROR_CHECK(mcpwm_new_generator(oper, &gen_config, &gen));

// Події генератора: високий рівень при обнуленні, низький при збігу компаратора
ESP_ERROR_CHECK(mcpwm_generator_set_actions_on_timer_event(gen,
    MCPWM_GEN_TIMER_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, MCPWM_TIMER_EVENT_EMPTY, MCPWM_GEN_ACTION_HIGH),
    MCPWM_GEN_TIMER_EVENT_ACTION_END()));
ESP_ERROR_CHECK(mcpwm_generator_set_actions_on_compare_event(gen,
    MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, cmpr, MCPWM_GEN_ACTION_LOW),
    MCPWM_GEN_COMPARE_EVENT_ACTION_END()));

ESP_ERROR_CHECK(mcpwm_timer_enable(timer));
ESP_ERROR_CHECK(mcpwm_timer_start_stop(timer, MCPWM_TIMER_START_NO_STOP));

// Встановлення тривалості імпульсу 1500 мкс (нейтраль, зупинка)
mcpwm_comparator_set_compare_value(cmpr, 1500);
