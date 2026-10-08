#include <stdio.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/ledc.h"

#define SERVO_LEDC_SPEED_MODE   LEDC_LOW_SPEED_MODE
#define SERVO_LEDC_CHANNEL      LEDC_CHANNEL_0
#define SERVO_LEDC_TIMER        LEDC_TIMER_0
#define SERVO_PWM_FREQ_HZ       (50)
#define SERVO_PWM_RESOLUTION    LEDC_TIMER_14_BIT

typedef struct {
    int gpio_num;
    int neutral_us;
    int deadband_us;
    int min_rev_us;
    int max_fwd_us;
} symmetric_servo_t;

static uint32_t us_to_duty(uint32_t us) {
    return (us * ((1 << 14) - 1)) / 20000;
}

void symmetric_servo_init(symmetric_servo_t *dev) {
    ledc_timer_config_t timer_conf = {
        .speed_mode = SERVO_LEDC_SPEED_MODE,
        .duty_resolution = SERVO_PWM_RESOLUTION,
        .timer_num = SERVO_LEDC_TIMER,
        .freq_hz = SERVO_PWM_FREQ_HZ,
        .clk_cfg = LEDC_AUTO_CLK
    };
    ledc_timer_config(&timer_conf);

    ledc_channel_config_t ch_conf = {
        .gpio_num = dev->gpio_num,
        .speed_mode = SERVO_LEDC_SPEED_MODE,
        .channel = SERVO_LEDC_CHANNEL,
        .intr_type = LEDC_INTR_DISABLE,
        .timer_sel = SERVO_LEDC_TIMER,
        .duty = 0,
        .hpoint = 0
    };
    ledc_channel_config(&ch_conf);
}

void symmetric_servo_set_speed(symmetric_servo_t *dev, float speed_norm) {
    if (speed_norm > 1.0f) speed_norm = 1.0f;
    if (speed_norm < -1.0f) speed_norm = -1.0f;

    int output_us = dev->neutral_us;

    if (speed_norm > 0.001f) {
        int active_start = dev->neutral_us + dev->deadband_us;
        output_us = active_start + (int)(speed_norm * (dev->max_fwd_us - active_start));
    } else if (speed_norm < -0.001f) {
        int active_start = dev->neutral_us - dev->deadband_us;
        output_us = active_start + (int)(speed_norm * (active_start - dev->min_rev_us));
    } else {
        output_us = dev->neutral_us;
    }

    uint32_t duty = us_to_duty(output_us);
    ledc_set_duty(SERVO_LEDC_SPEED_MODE, SERVO_LEDC_CHANNEL, duty);
    ledc_update_duty(SERVO_LEDC_SPEED_MODE, SERVO_LEDC_CHANNEL);
}
