#include <stdint.h>

// Повний двоточковий зв'язок «кожен з кожним», кожен канал — W ліній даних.
// Рахуємо не лінії, а САМЕ НІЖКИ (кожна лінія займає ніжку на обох кінцях).
static uint32_t naive_pins_total(uint32_t n_chips, uint32_t width) {
    uint32_t links = n_chips * (n_chips - 1u) / 2u;   // N·(N−1)/2 каналів
    return width * links * 2u;                         // ×W ліній ×2 кінці
}

// А тепер полічимо максимум ніжок, потрібних ОДНОМУ чипові в такій схемі:
// він тягне канал до кожного з решти, кожен канал — W ліній.
static uint32_t naive_pins_per_chip(uint32_t n_chips, uint32_t width) {
    return width * (n_chips - 1u);
}
