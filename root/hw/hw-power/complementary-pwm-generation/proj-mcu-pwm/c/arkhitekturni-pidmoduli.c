#include "driver/mcpwm_prelude.h"
#include "esp_log.h"

static const char *TAG = "MCPWM_HALF_BRIDGE";

void esp32_mcpwm_half_bridge_init(int high_side_gpio, int low_side_gpio, uint32_t dead_time_ns) {
    // 1. Створення таймера MCPWM (тактування 10 МГц, період 50 кГц у симетричному режимі)
    mcpwm_timer_handle_t timer = NULL;
    mcpwm_timer_config_t timer_config = {
        .group_id = 0,
        .clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT,
        .resolution_hz = 10000000, // 10 МГц (1 такт = 100 нс)
        .period_ticks = 100,       // 100 тактів вгору + 100 вниз = 200 тактів (50 кГц)
        .count_mode = MCPWM_TIMER_COUNT_MODE_UP_DOWN,
    };
    ESP_ERROR_CHECK(mcpwm_new_timer(&timer_config, &timer));

    // 2. Створення оператора (Operator) та прив'язка до таймера
    mcpwm_oper_handle_t oper = NULL;
    mcpwm_operator_config_t operator_config = {
        .group_id = 0,
    };
    ESP_ERROR_CHECK(mcpwm_new_operator(&operator_config, &oper));
    ESP_ERROR_CHECK(mcpwm_operator_connect_timer(oper, timer));

    // 3. Створення компаратора (Comparator) з оновленням за нульовим лічильником
    mcpwm_cmpr_handle_t comparator = NULL;
    mcpwm_comparator_config_t comparator_config = {
        .flags.update_cmp_on_tez = true,
    };
    ESP_ERROR_CHECK(mcpwm_new_comparator(oper, &comparator_config, &comparator));

    // 4. Створення генераторів для High-Side та Low-Side виводів
    mcpwm_gen_handle_t gen_high = NULL;
    mcpwm_generator_config_t gen_h_config = {.gen_gpio_num = high_side_gpio};
    ESP_ERROR_CHECK(mcpwm_new_generator(oper, &gen_h_config, &gen_high));

    mcpwm_gen_handle_t gen_low = NULL;
    mcpwm_generator_config_t gen_l_config = {.gen_gpio_num = low_side_gpio};
    ESP_ERROR_CHECK(mcpwm_new_generator(oper, &gen_l_config, &gen_low));

    // 5. Конфігурація подій виходу генератора PWM_H (високий рівень на початку, низький при співпадінні)
    ESP_ERROR_CHECK(mcpwm_generator_set_action_on_timer_event(
        gen_high,
        MCPWM_GEN_TIMER_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, MCPWM_TIMER_EVENT_EMPTY, MCPWM_GEN_ACTION_HIGH)));
    ESP_ERROR_CHECK(mcpwm_generator_set_action_on_compare_event(
        gen_high,
        MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, comparator, MCPWM_GEN_ACTION_LOW)));

    // 6. Активація блоку мертвого часу (Dead-Time Insertion)
    // 10 МГц -> 1 такт = 100 нс; перетворення наносекунд у такти таймера
    uint32_t dt_ticks = (dead_time_ns + 50) / 100;
    if (dt_ticks == 0) dt_ticks = 1;

    mcpwm_dead_time_config_t dt_config = {
        .posedge_path = MCPWM_DEAD_TIME_PATH_ACTIVE,
        .negedge_path = MCPWM_DEAD_TIME_PATH_INVERT, // Інверсія для створення комплементарного каналу
    };
    ESP_ERROR_CHECK(mcpwm_generator_set_dead_time(gen_high, gen_high, &dt_config));
    ESP_ERROR_CHECK(mcpwm_generator_set_dead_time(gen_high, gen_low, &dt_config));

    // 7. Увімкнення та запуск таймера
    ESP_ERROR_CHECK(mcpwm_timer_enable(timer));
    ESP_ERROR_CHECK(mcpwm_timer_start_stop(timer, MCPWM_TIMER_START_NO_STOP));
    ESP_LOGI(TAG, "ESP32 MCPWM Complementary pair initialized, DeadTime=%u ns", (unsigned)dead_time_ns);
}
