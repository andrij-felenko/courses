#include <stdint.h>

#define DIV         10u
#define DEBOUNCE_MS 5u                // глухий проміжок після фронту

volatile uint32_t revolutions = 0;
volatile uint8_t  mod_cnt     = 0;

extern volatile uint32_t millis;      // системний лічильник мілісекунд

void on_hall_pulse(void) {
    static uint32_t last_ms = 0;
    uint32_t now = millis;

    if ((uint32_t)(now - last_ms) < DEBOUNCE_MS)
        return;                       // ще в «глухому» проміжку — це дребезг, ігноруємо
    last_ms = now;

    revolutions++;
    if (++mod_cnt >= DIV) {
        mod_cnt = 0;
        LED_PIN ^= 1u;
    }
}
