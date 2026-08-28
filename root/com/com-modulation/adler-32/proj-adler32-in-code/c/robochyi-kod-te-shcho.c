#include <stdint.h>
#include <stddef.h>

#define BASE 65521U   /* найбільше просте, менше за 2¹⁶ */
#define NMAX 5552U    /* найдовша серія без зведення — виведення вище */

uint32_t adler32_fast(const uint8_t *d, size_t n) {
    uint32_t a = 1, b = 0;

    while (n) {
        size_t k = n < NMAX ? n : NMAX;   /* серія, що гарантовано не переповнить */
        n -= k;
        while (k--) {
            a += *d++;     /* у гарячому циклі — жодного зведення */
            b += a;
        }
        a %= BASE;         /* два зведення на всю серію, а не на кожен байт */
        b %= BASE;
    }
    return (b << 16) | a;
}
