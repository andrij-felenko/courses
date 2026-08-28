#include <stdio.h>
#include <stdlib.h>

#define RM_MAXN 4096            /* вистачає до m = 12 (n = 4096) */

/* popcount = степінь монома (число змінних у добутку) */
static int popcount(unsigned x) {
    int c = 0;
    while (x) { c += (int)(x & 1u); x >>= 1; }
    return c;
}

/* Кодер RM(r,m): msg[] містить коефіцієнти (ненульові лише при popcount<=r).
   Один subset-sum-метелик перетворює коефіцієнти на таблицю значень. */
void rm_encode(int m, const int *msg, int *code) {
    int n = 1 << m;
    for (int t = 0; t < n; t++) code[t] = msg[t];
    for (int i = 0; i < m; i++)
        for (int t = 0; t < n; t++)
            if (t & (1 << i)) code[t] ^= code[t ^ (1 << i)];
}
