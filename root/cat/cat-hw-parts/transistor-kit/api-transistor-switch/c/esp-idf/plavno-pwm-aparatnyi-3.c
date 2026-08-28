// Те саме на чистому ESP-IDF: те, що ledcAttach() ховає, тут стоїть окремо —
// спершу ТАЙМЕР (частота й розрядність), потім КАНАЛ (прив'язка до виводу).
#include "driver/ledc.h"

esp_err_t sw_begin_pwm(sw_t *s, ledc_channel_t ch, uint32_t freq_hz) {
    ledc_timer_config_t timer = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_8_BIT,   // 8 біт → шпаруватість 0…255
        .timer_num       = LEDC_TIMER_0,
        .freq_hz         = freq_hz,            // 5000 — вище звукового діапазону
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&timer));

    ledc_channel_config_t chan = {
        .gpio_num   = s->pin,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = ch,
        .intr_type  = LEDC_INTR_DISABLE,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = s->active_low ? 255 : 0,  // старт: вимкнено
        .hpoint     = 0,
    };
    return ledc_channel_config(&chan);
}
