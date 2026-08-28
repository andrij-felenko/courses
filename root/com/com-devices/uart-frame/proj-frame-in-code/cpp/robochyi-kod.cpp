#include <cstdint>

// Парність байта: XOR усіх 8 біт. Повертає 1, якщо одиниць непарно.
static uint8_t parity_xor(uint8_t b) {
    b ^= b >> 4;          // згортаємо half-байти
    b ^= b >> 2;
    b ^= b >> 1;
    return b & 1u;        // лишився XOR усіх вихідних біт
}

// Біт парності під обрану схему. even: щоб разом стало парно; odd: навпаки.
enum parity_t { PAR_NONE, PAR_EVEN, PAR_ODD };

static uint8_t parity_bit(uint8_t data, parity_t mode) {
    uint8_t p = parity_xor(data);          // =1, якщо одиниць у даних непарно
    if (mode == PAR_EVEN) return p;        // even: P доповнює до парного
    if (mode == PAR_ODD)  return p ^ 1u;   // odd: дзеркально
    return 0;                              // none: біта нема
}

// Зібрати кадр 8N1 у 16-бітне слово; нульовий біт слова виходить у лінію першим.
uint16_t build_frame_8N1(uint8_t data) {
    uint16_t frame = 0;
    frame |= 0u << 0;                 // старт «0» (позиція 0)
    frame |= (uint16_t)data << 1;     // 8 біт даних (позиції 1..8), LSB-first задарма
    frame |= 1u << 9;                 // стоп «1» (позиція 9)
    return frame;                     // напр. 0x41 → 0x282
}
