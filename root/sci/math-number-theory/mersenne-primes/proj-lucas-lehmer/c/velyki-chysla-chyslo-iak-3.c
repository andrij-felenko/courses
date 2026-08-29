#include <stdint.h>
#include <string.h>

typedef uint32_t limb;

/* s = (s − 2) mod Mp, вхід s ∈ [0, Mp) */
static void sub2_mod_mp(limb *s, int p, int n) {
    int R = p % 32;
    int above = 0;
    for (int i = 1; i < n; i++) {
        if (s[i]) above = 1;
    }
    if (!(s[0] >= 2 || above)) {               /* s дорівнює 0 або 1: спершу + Mp */
        limb d = 2 - s[0];
        for (int i = 0; i < n; i++) s[i] = 0xFFFFFFFFu;
        s[n - 1] = (1u << R) - 1;               /* s = Mp */
        limb b = d;                             /* далі відняти d ∈ {1,2} */
        for (int i = 0; i < n && b; i++) {
            limb o = s[i];
            s[i] = o - b;
            b = (o < b);
        }
        return;
    }
    limb b = 2;                                 /* s ≥ 2: проста позика двійки */
    for (int i = 0; i < n && b; i++) {
        limb o = s[i];
        s[i] = o - b;
        b = (o < b);
    }
}

/* Повний тест Люка–Лемера для довільного непарного простого p */
int lucas_lehmer(int p) {
    if (p == 2) return 1;                      /* M₂ = 3 просте */
    if (p < 2) return 0;
    int n = (p + 31) / 32;                      /* кількість 32-бітних слів */
    limb s[n], prod[2 * n];                     /* робочі буфери великого числа */
    memset(s, 0, n * sizeof(limb));
    s[0] = 4;                                   /* стартове значення S₀ = 4 */
    for (int k = 0; k < p - 2; k++) {
        square(s, n, prod);                    /* prod = s²          (2n лімбів) */
        reduce_mod_mp(prod, p, s, n);          /* s = prod mod Mp    (n лімбів)  */
        sub2_mod_mp(s, p, n);                  /* s = (s − 2) mod Mp             */
    }
    for (int i = 0; i < n; i++) {
        if (s[i]) return 0;                     /* якщо бодай один біт ненульовий */
    }
    return 1;                                   /* Sₚ₋₂ ≡ 0 (mod Mp) ⇒ Mp просте */
}
