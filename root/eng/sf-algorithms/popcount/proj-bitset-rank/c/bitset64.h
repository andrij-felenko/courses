/* bitset64.h — множина сталого розміру поверх масиву слів */
#ifndef BITSET64_H
#define BITSET64_H
#include <stddef.h>
#include "pc64.h"

#define BS_WORDS(n)  (((n) + 63u) / 64u)

static inline void bs_add(uint64_t *w, size_t i) { w[i >> 6] |=  (uint64_t)1 << (i & 63); }
static inline void bs_del(uint64_t *w, size_t i) { w[i >> 6] &= ~((uint64_t)1 << (i & 63)); }
static inline int  bs_has(const uint64_t *w, size_t i) {
    return (int)((w[i >> 6] >> (i & 63)) & 1u);
}
