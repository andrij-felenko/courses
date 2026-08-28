// ESP-IDF, блок MCPWM: лічильник ставимо на 1 МГц, тож тік = 1 мкс.
#include "driver/mcpwm_prelude.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SERVO_GPIO 18

static mcpwm_cmpr_handle_t cmpr;      // регістр порівняння = ширина імпульсу

static void servo_init(void) {
  mcpwm_timer_config_t tcfg = {
    .group_id      = 0,
    .clk_src       = MCPWM_TIMER_CLK_SRC_DEFAULT,
    .resolution_hz = 1000000,         // 1 тік = 1 мкс
    .period_ticks  = 20000,           // кадр 20 000 мкс = 50 Гц
    .count_mode    = MCPWM_TIMER_COUNT_MODE_UP,
  };
  mcpwm_timer_handle_t timer;
  ESP_ERROR_CHECK(mcpwm_new_timer(&tcfg, &timer));

  mcpwm_operator_config_t ocfg = { .group_id = 0 };
  mcpwm_oper_handle_t oper;
  ESP_ERROR_CHECK(mcpwm_new_operator(&ocfg, &oper));
  ESP_ERROR_CHECK(mcpwm_operator_connect_timer(oper, timer));

  mcpwm_comparator_config_t ccfg = { .flags.update_cmp_on_tez = true };
  ESP_ERROR_CHECK(mcpwm_new_comparator(oper, &ccfg, &cmpr));

  mcpwm_generator_config_t gcfg = { .gen_gpio_num = SERVO_GPIO };
  mcpwm_gen_handle_t gen;
  ESP_ERROR_CHECK(mcpwm_new_generator(oper, &gcfg, &gen));

  // на початку кадру — високий рівень, на збігу з порівнянням — низький
  ESP_ERROR_CHECK(mcpwm_generator_set_action_on_timer_event(gen,
      MCPWM_GEN_TIMER_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP,
                                   MCPWM_TIMER_EVENT_EMPTY, MCPWM_GEN_ACTION_HIGH)));
  ESP_ERROR_CHECK(mcpwm_generator_set_action_on_compare_event(gen,
      MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP,
                                     cmpr, MCPWM_GEN_ACTION_LOW)));

  ESP_ERROR_CHECK(mcpwm_timer_enable(timer));
  ESP_ERROR_CHECK(mcpwm_timer_start_stop(timer, MCPWM_TIMER_START_NO_STOP));
}

static void servo_write_us(int us) {
  if (us < 1000) us = 1000;           // не гнати за реальні межі!
  if (us > 2000) us = 2000;
  ESP_ERROR_CHECK(mcpwm_comparator_set_compare_value(cmpr, us));  // мкс напряму
}

void app_main(void) {
  servo_init();
  servo_write_us(1500);                                      // нейтраль
  while (1) {
    servo_write_us(1000); vTaskDelay(pdMS_TO_TICKS(1000));   // 0°
    servo_write_us(1500); vTaskDelay(pdMS_TO_TICKS(1000));   // 90°
    servo_write_us(2000); vTaskDelay(pdMS_TO_TICKS(1000));   // 180°
  }
}
