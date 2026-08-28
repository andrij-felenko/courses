#include <stdint.h>
#include <string.h>

// Грубе (truncating) float32 -> bfloat16: узяти старші 16 бітів.
// ПРАВИЛЬНО дістаємо біти через memcpy (не *(uint32_t*)&x — strict aliasing!).
uint16_t f32_to_bf16_truncate(float x) {
    uint32_t bits;
    memcpy(&bits, &x, sizeof bits);   // безпечно й безкоштовно
    return (uint16_t)(bits >> 16);    // верхня половина слова
}
