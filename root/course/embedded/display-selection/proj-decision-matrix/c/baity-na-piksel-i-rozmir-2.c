#include <stdbool.h>
#include <stdint.h>

/* безпечне множення трьох uint32_t; повертає false при переповненні */
static bool safe_mul3(uint32_t a, uint32_t b, uint32_t c, uint32_t *out)
{
    uint64_t p = (uint64_t)a * b;          /* крок 1 у 64 бітах */
    if (p > UINT32_MAX) return false;
    p *= c;                                /* крок 2 у 64 бітах */
    if (p > UINT32_MAX) return false;
    *out = (uint32_t)p;
    return true;
}
