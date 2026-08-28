#include <stdint.h>

// База периферії на шині — така сама адреса, яку бачить канал адрес AXI.
#define TIMER_BASE  0x40001000u
#define TIMER_CTRL  (*(volatile uint32_t *)(TIMER_BASE + 0x00))
#define TIMER_COUNT (*(volatile uint32_t *)(TIMER_BASE + 0x04))

void timer_start(void) {
    // Запис слова: процесор жене адресу по AW, дані по W, чекає B.
    TIMER_CTRL = 0x1u;            // біт 0 = 1 → лічити
}

uint32_t timer_read(void) {
    // Читання слова: адреса по AR, дані повертаються по R.
    return TIMER_COUNT;           // одне звернення — одне слово
}
