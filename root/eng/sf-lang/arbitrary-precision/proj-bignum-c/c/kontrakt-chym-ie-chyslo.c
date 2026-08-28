#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#if defined(__SIZEOF_INT128__)
typedef uint64_t          limb;    // «цифра» за основою B = 2⁶⁴
typedef unsigned __int128 dlimb;   // подвійне слово: сюди влазить добуток
  #define LIMB_BITS 64
#else
typedef uint32_t limb;
typedef uint64_t dlimb;
  #define LIMB_BITS 32
#endif

typedef struct {
    limb  *d;    // лімби, молодший — d[0]
    size_t n;    // скільки значущих: d[n−1] ≠ 0, або n = 0
    size_t cap;  // скільки лімбів виділено
    int    neg;  // 1 — від'ємне; для нуля завжди 0
} big;
