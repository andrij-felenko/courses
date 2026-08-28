#include <stdint.h>

// Таблиця «скільки одиниць у байті» — 256 записів, будується один раз.
static uint8_t popcnt8[256];

void popcount_init(void) {
    for (int i = 0; i < 256; i++) {
        uint8_t c = 0, v = (uint8_t)i;
        while (v) { c += v & 1u; v >>= 1; }   // рахуємо встановлені біти
        popcnt8[i] = c;
    }
}

// R = 64: один відлік звуку = 8 вхідних байтів PDM (8 × 8 = 64 біти).
#define PDM_BYTES_PER_SAMPLE  8

// Перетворити блок PDM-байтів на один 16-бітний відлік звуку.
// pdm — вказівник на 8 сирих байтів; повертає центрований відлік.
int16_t pdm_block_to_sample(const uint8_t *pdm) {
    uint32_t ones = 0;
    for (int i = 0; i < PDM_BYTES_PER_SAMPLE; i++)
        ones += popcnt8[pdm[i]];              // 0…64 одиниць у блоці

    // ones ∈ [0, 64]; середина шкали (тиша) — 32.
    // Центруємо: віднімаємо половину, множимо, щоб зайняти діапазон int16.
    int32_t centered = (int32_t)ones - 32;    // ∈ [−32, +32]
    return (int16_t)(centered * 1000);        // грубе масштабування у int16
}
