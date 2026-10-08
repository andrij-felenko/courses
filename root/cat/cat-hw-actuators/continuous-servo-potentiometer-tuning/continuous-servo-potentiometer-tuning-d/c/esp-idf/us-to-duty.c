#include <stdio.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/ledc.h"
#include "esp_err.h"

#define SERVO_LEDC_SPEED_MODE   LEDC_LOW_SPEED_MODE
#define SERVO_LEDC_CHANNEL      LEDC_CHANNEL_0
#define SERVO_LEDC_TIMER        LEDC_TIMER_0
#define SERVO_PWM_FREQ_HZ       (50)
#define SERVO_PWM_RESOLUTION    LEDC_TIMER_14_BIT

typedef struct {
    int gpio_num;
    int neutral_offset_us;
    int deadband_us;
} calibrated_servo_t;

static uint32_t us_to_duty(uint32_t us) {
    return (us * ((1 << 14) - 1)) / 20000;
}

void calibrated_servo_init(calibrated_servo_t *dev) {
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

void calibrated_servo_write_us(calibrated_servo_t *dev, int target_us) {
    int effective_neutral = 1500 + dev->neutral_offset_us;
    int delta = target_us - 1500;
    int final_us;

    if (abs(delta) <= dev->deadband_us) {
        final_us = effective_neutral;
    } else {
        final_us = target_us + dev->neutral_offset_us;
    }

    uint32_t duty = us_to_duty(final_us);
    ledc_set_duty(SERVO_LEDC_SPEED_MODE, SERVO_LEDC_CHANNEL, duty);
    ledc_update_duty(SERVO_LEDC_SPEED_MODE, SERVO_LEDC_CHANNEL);
}
