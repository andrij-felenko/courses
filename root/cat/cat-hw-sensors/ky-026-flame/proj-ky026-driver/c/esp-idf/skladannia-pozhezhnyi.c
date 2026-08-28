// ── Пожежний робот на ESP-IDF: напрямок — GPIO, швидкість — блок LEDC ──────
// AO лівого давача — ADC1_CH6 (GPIO34), правого — ADC1_CH7 (GPIO35).
#include "driver/ledc.h"
#include <stdlib.h>

#define AO_L_CH  ADC_CHANNEL_6
#define AO_R_CH  ADC_CHANNEL_7
#define FAN      GPIO_NUM_23            // ключ вентилятора-гасія
#define L_DIR    GPIO_NUM_25
#define R_DIR    GPIO_NUM_26
#define L_PWM_IO 14
#define R_PWM_IO 27

static void motors_init(void) {
    gpio_config_t io = { .pin_bit_mask = (1ULL << L_DIR) | (1ULL << R_DIR) | (1ULL << FAN),
                         .mode = GPIO_MODE_OUTPUT };
    ESP_ERROR_CHECK(gpio_config(&io));

    ledc_timer_config_t tm = { .speed_mode = LEDC_LOW_SPEED_MODE,
                               .duty_resolution = LEDC_TIMER_8_BIT,   // duty 0..255
                               .timer_num = LEDC_TIMER_0,
                               .freq_hz = 20000,                      // за межею чутності
                               .clk_cfg = LEDC_AUTO_CLK };
    ESP_ERROR_CHECK(ledc_timer_config(&tm));

    const int io_pwm[2] = { L_PWM_IO, R_PWM_IO };
    for (int c = 0; c < 2; c++) {
        ledc_channel_config_t ch = { .gpio_num = io_pwm[c], .speed_mode = LEDC_LOW_SPEED_MODE,
                                     .channel = c, .timer_sel = LEDC_TIMER_0, .duty = 0 };
        ESP_ERROR_CHECK(ledc_channel_config(&ch));
    }
}

static void set_duty(ledc_channel_t ch, int v) {
    if (v > 255) v = 255;
    ledc_set_duty(LEDC_LOW_SPEED_MODE, ch, v);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, ch);
}

static void drive(int left, int right) {   // швидкості −255..+255 (знак = напрямок)
    gpio_set_level(L_DIR, left  >= 0);
    gpio_set_level(R_DIR, right >= 0);
    set_duty(LEDC_CHANNEL_0, abs(left));
    set_duty(LEDC_CHANNEL_1, abs(right));
}
