#include "driver/ledc.h"

void pwm_start(void) {
  ledc_timer_config_t tcfg = {
    .speed_mode      = LEDC_LOW_SPEED_MODE,
    .timer_num       = LEDC_TIMER_0,
    .duty_resolution = LEDC_TIMER_10_BIT,   // 10 біт → діапазон 0..1023
    .freq_hz         = 1000,                // Гц
    .clk_cfg         = LEDC_AUTO_CLK,
  };
  ledc_timer_config(&tcfg);

  ledc_channel_config_t ccfg = {
    .gpio_num   = 18,
    .speed_mode = LEDC_LOW_SPEED_MODE,
    .channel    = LEDC_CHANNEL_0,
    .timer_sel  = LEDC_TIMER_0,
    .duty       = 512,                      // 512/1023 ≈ 50 % — і все
    .hpoint     = 0,
  };
  ledc_channel_config(&ccfg);
}
// далі задача app_main() вільна: сигнал іде сам
