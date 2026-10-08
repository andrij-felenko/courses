#include <stdio.h>
#include "driver/ledc.h"
#include "driver/adc.h"
#include "esp_err.h"

#define PUMP_PWM_GPIO        18
#define ADC_CURRENT_CHANNEL  ADC1_CHANNEL_6 // GPIO 34
#define ADC_PRESSURE_CHANNEL ADC1_CHANNEL_7 // GPIO 35
#define CURRENT_LIMIT_RAW    3000           // Поріг струму захисту

void init_pump_control(void) {
    // Налаштування таймера ШІМ (LEDC)
    ledc_timer_config_t timer_conf = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_10_BIT,
        .timer_num = LEDC_TIMER_0,
        .freq_hz = 10000, // 10 кГц ШІМ
        .clk_cfg = LEDC_AUTO_CLK
    };
    ledc_timer_config(&timer_conf);

    // Налаштування каналу ШІМ
    ledc_channel_config_t chan_conf = {
        .gpio_num = PUMP_PWM_GPIO,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0,
        .intr_type = LEDC_INTR_DISABLE,
        .timer_sel = LEDC_TIMER_0,
        .duty = 0,
        .hpoint = 0
    };
    ledc_channel_config(&chan_conf);

    // Налаштування АЦП для зворотного зв'язку
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(ADC_CURRENT_CHANNEL, ADC_ATTEN_DB_12);
    adc1_config_channel_atten(ADC_PRESSURE_CHANNEL, ADC_ATTEN_DB_12);
}

void set_pump_speed(uint32_t duty_percent) {
    uint32_t max_duty = (1 << 10) - 1;
    uint32_t duty = (max_duty * duty_percent) / 100;
    
    // Перевірка захисту за струмом перед встановленням швидкості
    int raw_current = adc1_get_raw(ADC_CURRENT_CHANNEL);
    if (raw_current > CURRENT_LIMIT_RAW) {
        // Аварійне вимкнення помпи при перевищенні струму
        ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
        return;
    }

    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}
