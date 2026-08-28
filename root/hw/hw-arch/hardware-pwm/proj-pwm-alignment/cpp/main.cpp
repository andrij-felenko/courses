#include <stdio.h>
#include "driver/mcpwm_prelude.h"

#define CLK_HZ       80000000   // такт MCPWM, Гц
#define PERIOD_TICKS 1000       // ВЕРХ; f_center = 80e6 / (2*1000) = 40 кГц
#define CMP_TICKS    400        // поріг → duty ≈ 40% (400/1000)
#define DEAD_TICKS   16         // t_dead = 16 × 12.5 нс = 200 нс

// ніжки GPIO (змінити під свою плату)
#define GPIO_HIGH_SIDE  18
#define GPIO_LOW_SIDE   19

void app_main(void)
{
    // ── 1. Таймер: режим UP_DOWN, resolution = 80 МГц, ВЕРХ = 1000 ──────────
    mcpwm_timer_handle_t timer = NULL;
    mcpwm_timer_config_t timer_cfg = {
        .group_id       = 0,
        .clk_src        = MCPWM_TIMER_CLK_SRC_DEFAULT,   // 80 МГц
        .resolution_hz  = CLK_HZ,
        .count_mode     = MCPWM_TIMER_COUNT_MODE_UP_DOWN, // центрований ШІМ
        .period_ticks   = PERIOD_TICKS,                   // ВЕРХ = 1000
    };
    mcpwm_new_timer(&timer_cfg, &timer);

    // ── 2. Оператор: зв'язує timer із парою ніжок ────────────────────────────
    mcpwm_oper_handle_t oper = NULL;
    mcpwm_operator_config_t oper_cfg = { .group_id = 0 };
    mcpwm_new_operator(&oper_cfg, &oper);
    mcpwm_operator_connect_timer(oper, timer);

    // ── 3. Компаратор: поріг = 400 тіків ─────────────────────────────────────
    mcpwm_cmpr_handle_t cmpr = NULL;
    mcpwm_comparator_config_t cmpr_cfg = {
        .flags.update_cmp_on_tez = true,  // оновлення на межі (тіньовий регістр)
    };
    mcpwm_new_comparator(oper, &cmpr_cfg, &cmpr);
    mcpwm_comparator_set_compare_value(cmpr, CMP_TICKS);

    // ── 4. Генератори: прямий і комплементарний (дзеркальні дії) ─────────────
    mcpwm_gen_handle_t gen_high = NULL, gen_low = NULL;
    mcpwm_generator_config_t gen_high_cfg = { .gen_gpio_num = GPIO_HIGH_SIDE };
    mcpwm_generator_config_t gen_low_cfg  = { .gen_gpio_num = GPIO_LOW_SIDE  };
    mcpwm_new_generator(oper, &gen_high_cfg, &gen_high);
    mcpwm_new_generator(oper, &gen_low_cfg,  &gen_low);

    // gen_high: HIGH при порозі на підйомі, LOW при порозі на спуску
    mcpwm_generator_set_actions_on_compare_event(gen_high,
        MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP,   cmpr, MCPWM_GEN_ACTION_HIGH),
        MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_DOWN, cmpr, MCPWM_GEN_ACTION_LOW),
        MCPWM_GEN_COMPARE_EVENT_ACTION_END());

    // gen_low: дзеркально — LOW при підйомі, HIGH при спуску
    mcpwm_generator_set_actions_on_compare_event(gen_low,
        MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP,   cmpr, MCPWM_GEN_ACTION_LOW),
        MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_DOWN, cmpr, MCPWM_GEN_ACTION_HIGH),
        MCPWM_GEN_COMPARE_EVENT_ACTION_END());

    // ── 5. Dead-time: 16 тіків (= 200 нс) між Q_high і Q_low ────────────────
    mcpwm_dead_time_config_t dt_cfg = {
        .posedge_delay_ticks = DEAD_TICKS,  // пауза перед наростаючим фронтом
        .negedge_delay_ticks = DEAD_TICKS,  // пауза перед спадаючим фронтом
    };
    mcpwm_generator_set_dead_time(gen_high, gen_low, &dt_cfg); // застосувати до пари

    // ── 6. Запуск ─────────────────────────────────────────────────────────────
    mcpwm_timer_enable(timer);
    mcpwm_timer_start_stop(timer, MCPWM_TIMER_START_NO_STOP);

    printf("MCPWM center-aligned + dead-time запущено\n");
}
