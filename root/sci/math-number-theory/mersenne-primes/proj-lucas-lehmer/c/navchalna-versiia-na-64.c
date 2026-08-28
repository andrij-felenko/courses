#include <stdint.h>

/* Тест для малих p: Mp = 2ᵖ−1 має влізти в 64 біти (p ≤ 61). */
int lucas_lehmer_small(int p) {
    if (p == 2) return 1;                      /* M₂ = 3 просте; рекурсія стартує з p ≥ 3 */
    uint64_t M = ((uint64_t)1 << p) - 1;       /* Mp = 2ᵖ − 1 */
    uint64_t s = 4;
    for (int i = 0; i < p - 2; i++) {
        unsigned __int128 sq = (unsigned __int128)s * s;   /* до 2¹²² — треба 128 біт! */
        uint64_t r = (uint64_t)(sq % M);                   /* остача діленням */
        s = (r >= 2) ? r - 2 : r + M - 2;                  /* s = (r − 2) за модулем M */
    }
    return s == 0;
}
