#include <stdint.h>
#include <stddef.h>

// t — 2^n байтів-бітів; після виклику t[m] — коефіцієнт при мономі-підмножині m
void anf_transform(uint8_t *t, int n) {
    for (size_t step = 1; step < ((size_t)1 << n); step <<= 1)
        for (size_t j = 0; j < ((size_t)1 << n); j += step << 1)
            for (size_t k = j; k < j + step; ++k)
                t[k + step] ^= t[k];        // рядку-з-одиницею ⊕ рядок-з-нулем
}
