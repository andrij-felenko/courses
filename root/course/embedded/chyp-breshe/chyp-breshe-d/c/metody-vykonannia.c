#include <stdint.h>
#include <stdbool.h>

// Метод 1: Знакове розширення 12-бітного числа через арифметичні зсуви
int16_t sign_extend_12bit_shift(uint16_t raw_12bit) {
    // Зсуваємо вліво на 4 біти, роблячи біт 11 бітом 15
    // Потім арифметично зсуваємо вправо на 4 біти
    int16_t val = (int16_t)(raw_12bit << 4);
    return val >> 4;
}

// Метод 2: Знакове розширення довільної розрядності BITS через маску
int32_t sign_extend_generic(uint32_t raw_val, uint8_t bits) {
    uint32_t sign_mask = 1UL << (bits - 1);
    if (raw_val & sign_mask) {
        // Число від'ємне: заповнюємо всі старші біти одиницями
        uint32_t extension_mask = ~((1UL << bits) - 1UL);
        return (int32_t)(raw_val | extension_mask);
    }
    // Число додатне
    return (int32_t)raw_val;
}

// Розпакування ліво-вирівняного 12-бітного значення (наприклад, ST LIS3DH)
int16_t parse_left_aligned_12bit(const uint8_t bytes[2]) {
    // Вхід: 16-бітне Little-Endian слово, де дані сидять у бітах [15:4]
    int16_t raw_16 = (int16_t)(((uint16_t)bytes[1] << 8) | (uint16_t)bytes[0]);
    // Арифметичний зсув вправо на 4 позиції автоматично зберігає знак
    return raw_16 >> 4;
}
