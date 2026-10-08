#include "driver/ledc.h"
#include "esp_err.h"

#define PUMP_PWM_GPIO       18
#define LEDC_TIMER          LEDC_TIMER_0
#define LEDC_MODE           LEDC_LOW_SPEED_MODE
#define LEDC_CHANNEL        LEDC_CHANNEL_0
#define LEDC_DUTY_RES       LEDC_TIMER_10_BIT // Роздільна здатність 0..1023
#define PWM_FREQ_HZ         15000              // Частота 15 кГц

void init_pump_pwm(void) {
    ledc_timer_config_t timer_conf = {
        .speed_mode      = LEDC_MODE,
        .duty_resolution = LEDC_DUTY_RES,
        .timer_num       = LEDC_TIMER,
        .freq_hz         = PWM_FREQ_HZ,
        .clk_cfg         = LEDC_AUTO_CLK
    };
    ledc_timer_config(&timer_conf);

    ledc_channel_config_t channel_conf = {
        .gpio_num   = PUMP_PWM_GPIO,
        .speed_mode = LEDC_MODE,
        .channel    = LEDC_CHANNEL,
        .intr_type  = LEDC_INTR_DISABLE,
        .timer_sel  = LEDC_TIMER,
        .duty       = 0,
        .hpoint     = 0
    };
    ledc_channel_config(&channel_conf);
    ledc_fade_func_install(0);
}

void set_pump_flow_smooth(uint32_t target_duty_10bit, uint32_t ramp_time_ms) {
    ledc_set_fade_with_time(LEDC_MODE, LEDC_CHANNEL, target_duty_10bit, ramp_time_ms);
    ledc_fade_start(LEDC_MODE, LEDC_CHANNEL, LEDC_FADE_NO_WAIT);
}
