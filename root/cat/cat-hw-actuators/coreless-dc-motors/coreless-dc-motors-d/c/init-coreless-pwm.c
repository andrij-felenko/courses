// Налаштування високочастотного ШІМ (80 кГц) для безсердечникового двигуна на ESP32 (LEDC)
#include "driver/ledc.h"

#define MOTOR_PWM_PIN       18
#define MOTOR_PWM_CHANNEL   LEDC_CHANNEL_0
#define MOTOR_PWM_FREQ_HZ   80000 // 80 кГц запобігають струмовим пульсаціям
#define MOTOR_PWM_RES       LEDC_TIMER_8_BIT // Роздільна здатність 8 біт (0-255)

void init_coreless_pwm(void) {
    ledc_timer_config_t timer_cfg = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .duty_resolution = MOTOR_PWM_RES,
        .timer_num       = LEDC_TIMER_0,
        .freq_hz         = MOTOR_PWM_FREQ_HZ,
        .clk_cfg         = LEDC_AUTO_CLK
    };
    ledc_timer_config(&timer_cfg);

    ledc_channel_config_t channel_cfg = {
        .gpio_num   = MOTOR_PWM_PIN,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = MOTOR_PWM_CHANNEL,
        .intr_type  = LEDC_INTR_DISABLE,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = 0,
        .hpoint     = 0
    };
    ledc_channel_config(&channel_cfg);
}

void set_motor_speed(uint8_t duty) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, MOTOR_PWM_CHANNEL, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, MOTOR_PWM_CHANNEL);
}
