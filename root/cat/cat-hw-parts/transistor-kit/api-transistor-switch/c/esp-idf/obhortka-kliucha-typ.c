// Те саме на ESP-IDF. Мова тут C, тож замість класу — структура плюс функції;
// полярність так само живе в даних, а не в кожному виклику.
#include "driver/gpio.h"
#include "esp_err.h"

typedef struct {
    gpio_num_t pin;
    bool       active_low;   // true → PNP верхом: рівень «0» вмикає навантаження
    bool       on;
} sw_t;

static void sw_on (sw_t *s) { gpio_set_level(s->pin, s->active_low ? 0 : 1); s->on = true;  }
static void sw_off(sw_t *s) { gpio_set_level(s->pin, s->active_low ? 1 : 0); s->on = false; }

static esp_err_t sw_begin(sw_t *s) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << s->pin,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    esp_err_t err = gpio_config(&cfg);
    if (err == ESP_OK) sw_off(s);   // ГАРАНТОВАНИЙ старт: навантаження вимкнене
    return err;
}

static void sw_set(sw_t *s, bool state) { state ? sw_on(s) : sw_off(s); }
static void sw_toggle(sw_t *s) { sw_set(s, !s->on); }
