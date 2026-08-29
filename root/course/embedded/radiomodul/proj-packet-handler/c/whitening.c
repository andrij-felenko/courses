#include "whitening.h"

void whitening_init(whitening_t *w)
{
    w->lfsr = LFSR_SEED;
}

uint8_t whitening_byte(whitening_t *w, uint8_t byte)
{
    uint8_t out = 0;

    /* Біти йдуть у ефір старшим першим, тому й маска накладається
       в тому ж порядку: вісім тактів регістра на один байт. */
    for (int bit = 7; bit >= 0; bit--) {
        const uint8_t mask_bit = (uint8_t)((w->lfsr >> 6) & 1u);                    /* вихід зі старшого розряду */
        const uint8_t feedback = (uint8_t)(((w->lfsr >> 6) ^ (w->lfsr >> 3)) & 1u); /* bit6 ^ bit3 */

        w->lfsr = (uint8_t)(((w->lfsr << 1) | feedback) & 0x7Fu);

        const uint8_t in_bit = (uint8_t)((byte >> bit) & 1u);
        out = (uint8_t)(out | (uint8_t)((in_bit ^ mask_bit) << bit));
    }
    return out;
}

void whitening_block(uint8_t *data, size_t len)
{
    whitening_t w;
    whitening_init(&w);

    for (size_t i = 0; i < len; i++) {
        data[i] = whitening_byte(&w, data[i]);
    }
}
