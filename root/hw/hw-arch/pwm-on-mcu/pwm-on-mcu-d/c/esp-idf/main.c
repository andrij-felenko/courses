#include "driver/ledc.h"

#define LED_GPIO 18

void led_pwm_start(void)
{
    ledc_timer_config_t tim = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_8_BIT,   // шкала 0…255
        .timer_num       = LEDC_TIMER_0,
        .freq_hz         = 1000,               // 1 кГц — око не ловить
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&tim));

    ledc_channel_config_t ch = {
        .gpio_num   = LED_GPIO,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = LEDC_CHANNEL_0,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = 77,                      // 77/255 ≈ 30%
        .hpoint     = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ch));
}

// яскравіше — новий поріг і підтвердження:
//   ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 191);
//   ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
