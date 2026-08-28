#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CHARLIE_PINS_COUNT 4
#define CHARLIE_LEDS_COUNT (CHARLIE_PINS_COUNT * (CHARLIE_PINS_COUNT - 1))
#define CHARLIE_PWM_LEVELS 8

typedef struct {
    uint8_t anode_pin;
    uint8_t cathode_pin;
} CharlieLed;

/* Статична таблиця відповідності індексів світлодіодів і пар виводів */
static const CharlieLed LED_MAP[CHARLIE_LEDS_COUNT] = {
    {0, 1}, {1, 0}, {0, 2}, {2, 0},
    {0, 3}, {3, 0}, {1, 2}, {2, 1},
    {1, 3}, {3, 1}, {2, 3}, {3, 2}
};

/* Таблиця апаратних функцій зворотного виклику */
typedef struct {
    void (*set_output_high)(uint8_t pin_idx);
    void (*set_output_low)(uint8_t pin_idx);
    void (*set_input_hiz)(uint8_t pin_idx);
} CharlieHal;

typedef struct {
    uint8_t brightness[CHARLIE_LEDS_COUNT];
    uint8_t current_led;
    uint8_t pwm_cycle;
    const CharlieHal *hal;
} CharlieDriver;

void charlie_init(CharlieDriver *drv, const CharlieHal *hal) {
    drv->hal = hal;
    drv->current_led = 0;
    drv->pwm_cycle = 0;
    memset(drv->brightness, 0, sizeof(drv->brightness));
    
    /* Усі лінії за замовчуванням переводимо у безпечний стан Hi-Z */
    for (uint8_t i = 0; i < CHARLIE_PINS_COUNT; ++i) {
        drv->hal->set_input_hiz(i);
    }
}

void charlie_set_brightness(CharlieDriver *drv, uint8_t led_idx, uint8_t val) {
    if (led_idx < CHARLIE_LEDS_COUNT) {
        if (val >= CHARLIE_PWM_LEVELS) val = CHARLIE_PWM_LEVELS - 1;
        drv->brightness[led_idx] = val;
    }
}

/* Обробник кроку сканування (викликається в перериванні таймера з частотою 5–10 кГц) */
void charlie_step(CharlieDriver *drv) {
    /* 1. Фаза мертвого часу (Dead-time): гасимо всі лінії перед новою комутацією */
    for (uint8_t i = 0; i < CHARLIE_PINS_COUNT; ++i) {
        drv->hal->set_input_hiz(i);
    }

    uint8_t led = drv->current_led;
    
    /* 2. Порівняння з порогом ШІМ: запалюємо діод лише при перевищенні лічильника */
    if (drv->brightness[led] > drv->pwm_cycle) {
        const CharlieLed *pair = &LED_MAP[led];
        drv->hal->set_output_high(pair->anode_pin);
        drv->hal->set_output_low(pair->cathode_pin);
    }

    /* 3. Циклічний інкремент індексу світлодіода та фази ШІМ */
    drv->current_led++;
    if (drv->current_led >= CHARLIE_LEDS_COUNT) {
        drv->current_led = 0;
        drv->pwm_cycle = (drv->pwm_cycle + 1) % CHARLIE_PWM_LEVELS;
    }
}
