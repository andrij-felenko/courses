#include <driver/ledc.h>

#define SERVO_GPIO       18
#define LEDC_TIMER       LEDC_TIMER_0
#define LEDC_MODE        LEDC_LOW_SPEED_MODE
#define LEDC_CHANNEL     LEDC_CHANNEL_0
#define LEDC_DUTY_RES    LEDC_TIMER_14_BIT // Роздільна здатність 14 біт (0..16383)
#define SERVO_FREQ_HZ    50                // Частота 50 Гц (20000 мкс)

void esp32_servo_init() {
    // Конфігурація апаратного таймера LEDC
    ledc_timer_config_t timer_conf = {
        .speed_mode      = LEDC_MODE,
        .duty_resolution = LEDC_DUTY_RES,
        .timer_num       = LEDC_TIMER,
        .freq_hz         = SERVO_FREQ_HZ,
        .clk_cfg         = LEDC_AUTO_CLK
    };
    ledc_timer_config(&timer_conf);

    // Конфігурація ШІМ-каналу
    ledc_channel_config_t channel_conf = {
        .gpio_num   = SERVO_GPIO,
        .speed_mode = LEDC_MODE,
        .channel    = LEDC_CHANNEL,
        .intr_type  = LEDC_INTR_DISABLE,
        .timer_sel  = LEDC_TIMER,
        .duty       = 0,
        .hpoint     = 0
    };
    ledc_channel_config(&channel_conf);
}

void esp32_set_pulse_us(uint32_t pulse_us) {
    // Загальний період 20000 мкс відповідає (2^14 - 1) = 16383 відлікам
    // duty = pulse_us * 16383 / 20000
    uint32_t duty = (pulse_us * 16383) / 20000;
    ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, duty);
    ledc_update_duty(LEDC_MODE, LEDC_CHANNEL);
}
