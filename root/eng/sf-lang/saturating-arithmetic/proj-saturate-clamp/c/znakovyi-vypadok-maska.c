#include <stdint.h>

int32_t add_sat_s32_bl(int32_t a, int32_t b) {
    // беззнакова сума — щоб саме додавання не було UB
    uint32_t ua = (uint32_t)a, ub = (uint32_t)b;
    uint32_t us = ua + ub;
    int32_t  s  = (int32_t)us;

    // межа за знаком доданків: a≥0 → INT_MAX, a<0 → INT_MIN
    int32_t m     = a >> 31;
    int32_t limit = (m & INT32_MIN) | (~m & INT32_MAX);

    // переповнення ⇔ доданки одного знаку, а сума — іншого
    // ((a ^ b) — знаки різні?) АБО-НІ з ((a ^ s) — сума зіпсувалась?)
    int32_t overflow = (int32_t)((ua ^ ub) | ~(ub ^ us));
    // overflow < 0  рівно тоді, коли переповнення НЕ сталося
    int32_t of_mask  = ~(overflow >> 31);   // сталось → усі 1; ні → усі 0

    return (int32_t)((limit & of_mask) | (s & ~of_mask));
}
