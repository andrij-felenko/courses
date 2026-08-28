#include "driver/gpio.h"
#include "esp_timer.h"

typedef struct {
    gpio_num_t pin;
    uint32_t   debounce_ms;   // скільки стан має протриматись, щоб його прийняти
    bool       raw_last, stable;
    int64_t    changed_at;    // мкс від старту (лічильник 64-бітний — не перекрутиться)
} ir_obstacle_t;

// Сирий біт → логічна «перешкода»: активний нуль, тож 0 = true.
static bool ir_read_raw(const ir_obstacle_t *s) {
    return gpio_get_level(s->pin) == 0;
}

esp_err_t ir_obstacle_begin(ir_obstacle_t *s, gpio_num_t pin,
                            uint32_t debounce_ms, bool use_pullup) {
    s->pin = pin;
    s->debounce_ms = debounce_ms;
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << pin,
        .mode         = GPIO_MODE_INPUT,
        // внутрішня підтяжка лікує «плаваючу» лінію
        .pull_up_en   = use_pullup ? GPIO_PULLUP_ENABLE : GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    esp_err_t err = gpio_config(&cfg);
    if (err != ESP_OK) return err;
    // початковий стан читаємо одразу, щоб не «клацнути» на старті
    s->raw_last = s->stable = ir_read_raw(s);
    s->changed_at = esp_timer_get_time();
    return ESP_OK;
}

// Викликати часто — із задачі опитування. Оновлює підтверджений стан.
void ir_obstacle_update(ir_obstacle_t *s) {
    bool    raw = ir_read_raw(s);
    int64_t now = esp_timer_get_time();
    if (raw != s->raw_last) {              // сирий стан щойно смикнувся
        s->raw_last   = raw;
        s->changed_at = now;               // перезапускаємо відлік стабільності
    }
    // прийняти новий стан лише коли він протримався досить довго
    if (raw != s->stable && (now - s->changed_at) >= (int64_t)s->debounce_ms * 1000)
        s->stable = raw;
}

// Чесна подія: true = перешкода поруч (інверсію вже враховано).
bool ir_obstacle(const ir_obstacle_t *s) { return s->stable; }
