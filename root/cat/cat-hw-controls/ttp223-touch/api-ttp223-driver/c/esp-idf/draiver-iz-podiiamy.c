// --- touch_button: драйвер миттєвого режиму TTP223 (ESP-IDF) ----------------
#include "driver/gpio.h"
#include "esp_timer.h"

#define TOUCH_GUARD_MS  5      // мс стійкості проти імпульсів-привидів

typedef struct {
    gpio_num_t pin;
    int        active;         // 1 (акт. у 1) або 0 (акт. у 0)
    bool       raw, stable, just_pressed, just_released;
    int64_t    last_edge, pressed_at;      // мс від старту
} touch_button_t;

static int64_t tb_now_ms(void) { return esp_timer_get_time() / 1000; }

static bool tb_read_active(const touch_button_t *b) {
    return gpio_get_level(b->pin) == b->active;
}

void tb_begin(touch_button_t *b, gpio_num_t pin, int active_level) {
    *b = (touch_button_t){ .pin = pin, .active = active_level };
    gpio_config_t cfg = {                 // двотактний вихід → без підтяжок
        .pin_bit_mask = 1ULL << pin,      .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
    b->stable = b->raw = tb_read_active(b);   // старт із поточного стану
    b->last_edge = tb_now_ms();
}

// Кликати щопроходу циклу; true рівно в момент активації (фронт).
bool tb_update(touch_button_t *b) {
    bool a = tb_read_active(b);
    int64_t now = tb_now_ms();

    if (a != b->raw) { b->raw = a; b->last_edge = now; }   // сирий рівень змінився

    if (now - b->last_edge >= TOUCH_GUARD_MS && b->stable != a) {
        b->stable = a;                    // рівень протримався GUARD мс → справжній
        if (a) { b->pressed_at = now; b->just_pressed = true; return true; }
        b->just_released = true;
    }
    return false;
}

bool tb_pressed(touch_button_t *b)  { bool r = b->just_pressed;  b->just_pressed  = false; return r; }
bool tb_released(touch_button_t *b) { bool r = b->just_released; b->just_released = false; return r; }
bool tb_held(const touch_button_t *b)     { return b->stable; }
int64_t tb_held_ms(const touch_button_t *b) { return b->stable ? tb_now_ms() - b->pressed_at : 0; }
