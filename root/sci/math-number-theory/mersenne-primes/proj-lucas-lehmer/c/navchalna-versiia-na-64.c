#include <stdint.h>

/* Зведення числа x за модулем Mp = 2ᵖ − 1 без використання ділення. */
static uint64_t reduce_small(unsigned __int128 x, int p) {
    uint64_t M = ((uint64_t)1 << p) - 1;       /* маска молодших p бітів */
    while (x >> p) {                            /* доки є біти вище p-го розряду */
        x = (x & M) + (x >> p);                 /* згортання: 2ᵖ ≡ 1 (mod Mp) */
    }
    return (x == M) ? 0 : (uint64_t)x;          /* якщо вийшло Mp (усі одиниці) — це 0 */
}

/* Тест для малих p: Mp = 2ᵖ−1 має влізти в 64 біти (p ≤ 61). */
int lucas_lehmer_small(int p) {
    if (p == 2) return 1;                      /* M₂ = 3 просте; рекурсія стартує з p ≥ 3 */
    if (p < 2 || p > 61) return 0;              /* межі діапазону для 64-бітного слова */
    uint64_t M = ((uint64_t)1 << p) - 1;       /* Mp = 2ᵖ − 1 */
    uint64_t s = 4;                             /* S₀ = 4 */
    for (int i = 0; i < p - 2; i++) {
        unsigned __int128 sq = (unsigned __int128)s * s;   /* проміжний квадрат до 2¹²² */
        uint64_t r = reduce_small(sq, p);                  /* зведення без ділення */
        s = (r >= 2) ? r - 2 : r + M - 2;                  /* s = (r − 2) за модулем Mp */
    }
    return s == 0;                              /* Sₚ₋₂ ≡ 0 ⇔ Mp просте */
}
