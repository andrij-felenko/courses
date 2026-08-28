#include <stdint.h>
#include <string.h>

// Грубе (truncating) перетворення float32 → bfloat16.
// bfloat16 = старші 16 бітів бітового образу float.
uint16_t float_to_bf16_truncate(float x) {
    uint32_t bits;
    memcpy(&bits, &x, sizeof bits);   // безпечно дістати біти float
    return (uint16_t)(bits >> 16);    // просто верхня половина слова
}

float bf16_to_float(uint16_t b) {
    uint32_t bits = (uint32_t)b << 16;   // дописати 16 молодших нулів
    float x;
    memcpy(&x, &bits, sizeof x);
    return x;
}
