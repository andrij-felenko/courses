#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/mcpwm_prelude.h"
#include "esp_log.h"

#define SERVO_MIN_PULSE_US       1000
#define SERVO_MAX_PULSE_US       2000
#define SERVO_BASE_NEUTRAL_US    1500
#define SERVO_DEADBAND_US        10
#define SERVO_PWM_GPIO           18

static const char *TAG = "SERVO_CTRL";
static mcpwm_gen_handle_t generator = NULL;

// Зсув нейтралі у мікросекундах, визначений під час калібрування
static int32_t s_neutral_offset_us = 12;

void continuous_servo_init(void) {
    mcpwm_timer_handle_t timer = NULL;
    mcpwm_timer_config_t timer_config = {
        .group_id = 0,
        .clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT,
        .resolution_hz = 1000000, // 1 мкс на такт
        .period_ticks = 20000,    // 20 мс (50 Гц)
        .count_mode = MCPWM_TIMER_COUNT_MODE_UP,
    };
    ESP_ERROR_CHECK(mcpwm_new_timer(&timer_config, &timer));

    mcpwm_oper_handle_t oper = NULL;
    mcpwm_operator_config_t oper_config = { .group_id = 0 };
    ESP_ERROR_CHECK(mcpwm_new_operator(&oper_config, &oper));
    ESP_ERROR_CHECK(mcpwm_operator_connect_timer(oper, timer));

    mcpwm_comparator_handle_t comparator = NULL;
    mcpwm_comparator_config_t cmpr_config = { .flags.update_cmp_on_tez = true };
    ESP_ERROR_CHECK(mcpwm_new_comparator(oper, &cmpr_config, &comparator));

    mcpwm_generator_config_t gen_config = { .gen_gpio_num = SERVO_PWM_GPIO };
    ESP_ERROR_CHECK(mcpwm_new_generator(oper, &gen_config, &generator));

    mcpwm_gen_timer_event_action_t action_on_tez = {
        .direction = MCPWM_TIMER_DIRECTION_UP,
        .action = MCPWM_GEN_ACTION_HIGH,
    };
    mcpwm_generator_set_action_on_timer_event(generator, action_on_tez);

    mcpwm_gen_compare_event_action_t action_on_cmp = {
        .direction = MCPWM_TIMER_DIRECTION_UP,
        .comparator = comparator,
        .action = MCPWM_GEN_ACTION_LOW,
    };
    mcpwm_generator_set_action_on_compare_event(generator, action_on_cmp);

    ESP_ERROR_CHECK(mcpwm_timer_enable(timer));
    ESP_ERROR_CHECK(mcpwm_timer_start_stop(timer, MCPWM_TIMER_START_NO_STOP));

    // Встановлення початкової нейтралі з урахуванням зсуву
    mcpwm_comparator_set_compare_value(comparator, SERVO_BASE_NEUTRAL_US + s_neutral_offset_us);
    ESP_LOGI(TAG, "Сервопривід ініціалізовано. Зсув нейтралі: %ld мкс", s_neutral_offset_us);
}

void continuous_servo_set_speed(mcpwm_comparator_handle_t cmpr, float speed_pct) {
    if (speed_pct > 100.0f) speed_pct = 100.0f;
    if (speed_pct < -100.0f) speed_pct = -100.0f;

    uint32_t calibrated_neutral = SERVO_BASE_NEUTRAL_US + s_neutral_offset_us;
    uint32_t pulse_us = calibrated_neutral;

    if (speed_pct > 0.0f) {
        uint32_t range = SERVO_MAX_PULSE_US - calibrated_neutral;
        pulse_us = calibrated_neutral + (uint32_t)((speed_pct / 100.0f) * range);
    } else if (speed_pct < 0.0f) {
        uint32_t range = calibrated_neutral - SERVO_MIN_PULSE_US;
        pulse_us = calibrated_neutral - (uint32_t)((-speed_pct / 100.0f) * range);
    }

    // Захист від паразитарного повзання в зоні нечутливості
    if (abs((int32_t)pulse_us - (int32_t)calibrated_neutral) < SERVO_DEADBAND_US) {
        pulse_us = calibrated_neutral;
    }

    mcpwm_comparator_set_compare_value(cmpr, pulse_us);
}
