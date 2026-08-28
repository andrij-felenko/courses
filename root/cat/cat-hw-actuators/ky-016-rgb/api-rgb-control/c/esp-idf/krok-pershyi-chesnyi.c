// --- KY-016 на ESP-IDF: три канали апаратного модуля LEDC ---
#include "driver/ledc.h"
#include "esp_err.h"

#define PIN_R 25
#define PIN_G 26
#define PIN_B 27

// true — плата зі СПІЛЬНИМ АНОДОМ (колір вмикає низький рівень)
#define COMMON_ANODE 0

// один вихід каналу: тут і тільки тут живе інверсія для анода
// (LEDC уміє інвертувати й апаратно — flags.output_invert; лишаємо явно, щоб було видно)
static inline uint32_t level(uint8_t v) { return COMMON_ANODE ? 255u - v : v; }

static void rgb_init(void) {
    ledc_timer_config_t timer = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .timer_num       = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_8_BIT,   // шкала duty 0..255, як на Uno
        .freq_hz         = 5000,               // 5 кГц — без видимого мерехтіння
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&timer));

    const int pins[3] = { PIN_R, PIN_G, PIN_B };
    for (int i = 0; i < 3; i++) {
        ledc_channel_config_t ch = {
            .gpio_num   = pins[i],
            .speed_mode = LEDC_LOW_SPEED_MODE,
            .channel    = (ledc_channel_t)(LEDC_CHANNEL_0 + i),
            .timer_sel  = LEDC_TIMER_0,
            .duty       = 0,
            .hpoint     = 0,
        };
        ESP_ERROR_CHECK(ledc_channel_config(&ch));
    }
}

static void write_ch(ledc_channel_t ch, uint8_t v) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, ch, level(v));
    ledc_update_duty(LEDC_LOW_SPEED_MODE, ch);   // duty набирає сили лише тут
}

void set_color(uint8_t r, uint8_t g, uint8_t b) {
    write_ch(LEDC_CHANNEL_0, r);   // r,g,b — «людська» яскравість: 255 = яскраво
    write_ch(LEDC_CHANNEL_1, g);
    write_ch(LEDC_CHANNEL_2, b);
}

void app_main(void) {
    rgb_init();
    set_color(255, 90, 0);         // теплий помаранчевий
}
