#include "driver/gpio.h"
#include "esp_timer.h"

#define EN_ON_US   1000   // вікно несучої (≤2 мс!)
#define EN_OFF_US  1000   // пауза для розслаблення AGC

typedef struct {
    gpio_num_t out, en;       // en = GPIO_NUM_NC → піна нема, поведінка як FC-51
    uint32_t   debounce_ms;
    bool       raw_last, stable, en_high;
    int64_t    changed_at, phase_at;
} ir_en_t;

static bool has_en(const ir_en_t *s)    { return s->en != GPIO_NUM_NC; }
static bool en_read_raw(const ir_en_t *s) { return gpio_get_level(s->out) == 0; }

static gpio_config_t pin_cfg(gpio_num_t p, gpio_mode_t mode, gpio_pullup_t pu) {
    gpio_config_t c = { .pin_bit_mask = 1ULL << p, .mode = mode, .pull_up_en = pu,
                        .pull_down_en = GPIO_PULLDOWN_DISABLE,
                        .intr_type = GPIO_INTR_DISABLE };
    return c;
}

esp_err_t ir_en_begin(ir_en_t *s, gpio_num_t out, gpio_num_t en, uint32_t debounce_ms) {
    s->out = out;  s->en = en;  s->debounce_ms = debounce_ms;
    gpio_config_t in_cfg = pin_cfg(out, GPIO_MODE_INPUT, GPIO_PULLUP_ENABLE);
    ESP_ERROR_CHECK(gpio_config(&in_cfg));
    if (has_en(s)) {
        gpio_config_t en_cfg = pin_cfg(en, GPIO_MODE_OUTPUT, GPIO_PULLUP_DISABLE);
        ESP_ERROR_CHECK(gpio_config(&en_cfg));
        gpio_set_level(en, 0);             // старт із вимкненою несучою
    }
    s->raw_last = s->stable = en_read_raw(s);
    s->changed_at = s->phase_at = esp_timer_get_time();
    s->en_high = false;
    return ESP_OK;
}

// Придушення дрижання — те саме, що без EN.
static void debounce_only(ir_en_t *s, bool raw) {
    int64_t now = esp_timer_get_time();
    if (raw != s->raw_last) { s->raw_last = raw; s->changed_at = now; }
    if (raw != s->stable && (now - s->changed_at) >= (int64_t)s->debounce_ms * 1000)
        s->stable = raw;
}

// Неблокуюча машина станів для EN.
void ir_en_update(ir_en_t *s) {
    if (!has_en(s)) { debounce_only(s, en_read_raw(s)); return; }
    int64_t now = esp_timer_get_time();
    if (s->en_high) {
        if (now - s->phase_at >= EN_ON_US) {      // вікно скінчилось
            debounce_only(s, en_read_raw(s));     // читаємо ПОКИ несуча ще була
            gpio_set_level(s->en, 0);             // гасимо несучу
            s->en_high = false;  s->phase_at = now;
        }
    } else {
        if (now - s->phase_at >= EN_OFF_US) {     // пауза скінчилась
            gpio_set_level(s->en, 1);             // пускаємо несучу знову
            s->en_high = true;   s->phase_at = now;
        }
    }
}

bool ir_en_obstacle(const ir_en_t *s) { return s->stable; }
