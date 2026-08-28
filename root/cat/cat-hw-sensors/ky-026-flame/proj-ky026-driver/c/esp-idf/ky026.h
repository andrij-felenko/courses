// ── ky026.h ── ESP-IDF: DO — звичайний GPIO, AO — канал АЦП, час — esp_timer
#pragma once
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_timer.h"

typedef struct {
    gpio_num_t    pin_do;
    adc_channel_t ch_ao;        // AO живе на КАНАЛІ АЦП, а не просто «на піні»
    bool          inverted;     // спокій=1, вогонь=0 — як на більшості модулів
    uint32_t      debounce_us;  // витримка стану, мікросекунди
    adc_oneshot_unit_handle_t adc;
    bool     stable, last_raw;
    int64_t  changed_at;
} ky026_t;

// Сирий біт «поріг перейдено», уже розвернутий під інверсію.
static inline bool ky026_raw(const ky026_t *s) {
    int v = gpio_get_level(s->pin_do);
    return s->inverted ? (v == 0) : (v == 1);
}

static inline void ky026_begin(ky026_t *s) {
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << s->pin_do,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,   // модуль сам тягне лінію
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));

    adc_oneshot_chan_cfg_t ch = {
        .atten    = ADC_ATTEN_DB_12,           // послаблення: міряти майже до 3.3 В
        .bitwidth = ADC_BITWIDTH_DEFAULT,      // 12 біт → 0..4095
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(s->adc, s->ch_ao, &ch));

    s->stable = s->last_raw = ky026_raw(s);
    s->changed_at = esp_timer_get_time();      // мікросекунди від старту
}

// Кликати часто. Той самий секундомір, лише годинник у мікросекундах.
static inline bool ky026_update(ky026_t *s) {
    bool now = ky026_raw(s);
    int64_t t = esp_timer_get_time();
    if (now != s->last_raw) { s->last_raw = now; s->changed_at = t; }
    else if (now != s->stable && (t - s->changed_at) >= s->debounce_us) s->stable = now;
    return s->stable;
}

static inline int ky026_strength(const ky026_t *s) {
    int raw = 0;
    adc_oneshot_read(s->adc, s->ch_ao, &raw);  // сира сила жару, 0..4095
    return raw;
}
