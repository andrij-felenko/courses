// ── «Магічна чаша» на парі KY-027, ESP-IDF (ШІМ — периферія LEDC) ──
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_S_A  GPIO_NUM_4    // вихід вимикача чаші A (цифровий вхід)
#define PIN_L_A  GPIO_NUM_18   // світлодіод чаші A — канал LEDC 0
#define PIN_S_B  GPIO_NUM_5    // вихід вимикача чаші B (цифровий вхід)
#define PIN_L_B  GPIO_NUM_19   // світлодіод чаші B — канал LEDC 1

// Який рівень на піні S означає «нахилено»: замкнений вимикач тягне S до землі.
#define TILTED   0

// ── згасання брязкоту (див. вище) ──
typedef struct { gpio_num_t pin; bool stable; bool last_raw; int64_t changed_us; } debounced_t;
#define DEBOUNCE_US 25000

static void debounce_begin(debounced_t *d, gpio_num_t pin) {
    gpio_config_t cfg = { .pin_bit_mask = 1ULL << pin, .mode = GPIO_MODE_INPUT,
                          .pull_up_en = GPIO_PULLUP_DISABLE,
                          .pull_down_en = GPIO_PULLDOWN_DISABLE,
                          .intr_type = GPIO_INTR_DISABLE };
    ESP_ERROR_CHECK(gpio_config(&cfg));
    d->pin = pin; d->stable = gpio_get_level(pin);
    d->last_raw = d->stable; d->changed_us = esp_timer_get_time();
}
static bool debounce_read(debounced_t *d) {
    bool raw = gpio_get_level(d->pin);
    if (raw != d->last_raw) { d->last_raw = raw; d->changed_us = esp_timer_get_time(); }
    if (raw != d->stable && esp_timer_get_time() - d->changed_us >= DEBOUNCE_US) d->stable = raw;
    return d->stable;
}

// ── ШІМ: один таймер на 5 кГц / 8 бітів, два канали з нього ──
static void pwm_begin(ledc_channel_t ch, gpio_num_t pin) {
    ledc_channel_config_t c = { .gpio_num = pin, .speed_mode = LEDC_LOW_SPEED_MODE,
                                .channel = ch, .timer_sel = LEDC_TIMER_0,
                                .intr_type = LEDC_INTR_DISABLE, .duty = 0, .hpoint = 0 };
    ESP_ERROR_CHECK(ledc_channel_config(&c));
}
static void pwm_write(ledc_channel_t ch, uint32_t duty) {
    ESP_ERROR_CHECK(ledc_set_duty(LEDC_LOW_SPEED_MODE, ch, duty));
    ESP_ERROR_CHECK(ledc_update_duty(LEDC_LOW_SPEED_MODE, ch));
}

// ── спільний рівень переливу ──
static uint8_t level = 128;
#define STEP 3
static void nudge(int dir) {
    int next = (int)level + dir * STEP;
    if (next < 0) next = 0;
    if (next > 255) next = 255;
    level = (uint8_t)next;
}

void app_main(void) {
    static debounced_t sw_a, sw_b;
    debounce_begin(&sw_a, PIN_S_A);
    debounce_begin(&sw_b, PIN_S_B);

    ledc_timer_config_t t = { .speed_mode = LEDC_LOW_SPEED_MODE, .timer_num = LEDC_TIMER_0,
                              .duty_resolution = LEDC_TIMER_8_BIT,   // шпаруватість 0..255
                              .freq_hz = 5000, .clk_cfg = LEDC_AUTO_CLK };
    ESP_ERROR_CHECK(ledc_timer_config(&t));
    pwm_begin(LEDC_CHANNEL_0, PIN_L_A);
    pwm_begin(LEDC_CHANNEL_1, PIN_L_B);

    while (1) {
        // 1. Чисті стани обох вимикачів (уже без брязкоту).
        bool tilt_a = (debounce_read(&sw_a) == TILTED);
        bool tilt_b = (debounce_read(&sw_b) == TILTED);

        // 2. Посунути спільний рівень за нахилом; обидві або жодна → стоїмо.
        if (tilt_a && !tilt_b)      nudge(+1);
        else if (tilt_b && !tilt_a) nudge(-1);

        // 3. Вивести рівень: сума яскравостей завжди 255.
        pwm_write(LEDC_CHANNEL_0, level);
        pwm_write(LEDC_CHANNEL_1, 255 - level);

        vTaskDelay(pdMS_TO_TICKS(4));   // такт ≈4 мс → повний перелив за ~340 мс
    }
}
