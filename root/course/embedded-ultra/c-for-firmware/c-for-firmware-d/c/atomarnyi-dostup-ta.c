#include <stdint.h>

#define GPIOA_BSRR (*(volatile uint32_t *)0x40010810UL)

void led_on_atomic(void) {
    // Атомарне встановлення 5-го піна (1 такт запису, відсутність RMW)
    GPIOA_BSRR = (1U << 5);
}

void led_off_atomic(void) {
    // Атомарне скидання 5-го піна (запис у старшу половину регістра)
    GPIOA_BSRR = (1U << (5 + 16));
}
