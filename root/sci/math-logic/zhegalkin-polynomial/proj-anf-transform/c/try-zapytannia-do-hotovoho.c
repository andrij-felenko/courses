#include <stdint.h>
#include <stddef.h>

// значення полінома на наборі x: ⊕ коефіцієнтів усіх підмножин x
uint8_t anf_eval(const uint8_t *coef, size_t x) {
    uint8_t acc = 0;
    for (size_t m = x; ; m = (m - 1) & x) {     // перебір підмножин маски x
        acc ^= coef[m];
        if (m == 0) break;
    }
    return acc;
}

// алгебричний степінь; -1 для тотожного нуля (живих доданків нема)
int anf_degree(const uint8_t *coef, int n) {
    int deg = -1;
    for (size_t m = 0; m < ((size_t)1 << n); ++m)
        if (coef[m]) {
            int d = __builtin_popcountll((unsigned long long)m);
            if (d > deg) deg = d;
        }
    return deg;
}

// лінійна (афінна) ⟺ немає доданка з двох і більше змінних
int is_affine(const uint8_t *coef, int n) {
    for (size_t m = 0; m < ((size_t)1 << n); ++m)
        if (coef[m] && __builtin_popcountll((unsigned long long)m) >= 2)
            return 0;
    return 1;
}
