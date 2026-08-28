#include <stdint.h>
#include <stdbool.h>

#define PINS_COUNT 3
#define LEDS_COUNT (PINS_COUNT * (PINS_COUNT - 1))

typedef struct {
    uint8_t anode;
    uint8_t cathode;
} CharliePair;

static const CharliePair LED_MAP[LEDS_COUNT] = {
    {0, 1}, {1, 0}, {0, 2}, {2, 0}, {1, 2}, {2, 1}
};

static volatile bool frame_buffer[LEDS_COUNT];
static volatile uint8_t current_slot = 0;

/* Апаратні виклики (приклад для умовного МК) */
extern void mcu_gpio_set_hiz(uint8_t pin);
extern void mcu_gpio_set_high(uint8_t pin);
extern void mcu_gpio_set_low(uint8_t pin);

/* Обробник апаратного таймера (викликається кожні 500 мкс) */
void Charlieplex_Timer_ISR(void) {
    /* 1. Dead-time: гасимо всі лінії */
    for (uint8_t i = 0; i < PINS_COUNT; ++i) {
        mcu_gpio_set_hiz(i);
    }

    /* 2. Вмикаємо активний світлодіод поточного слота */
    if (frame_buffer[current_slot]) {
        uint8_t a = LED_MAP[current_slot].anode;
        uint8_t c = LED_MAP[current_slot].cathode;
        mcu_gpio_set_high(a);
        mcu_gpio_set_low(c);
    }

    /* 3. Крок до наступного слота */
    if (++current_slot >= LEDS_COUNT) {
        current_slot = 0;
    }
}
