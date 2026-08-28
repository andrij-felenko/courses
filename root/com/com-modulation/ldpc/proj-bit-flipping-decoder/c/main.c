/* Жорсткий декодер LDPC: перевертання бітів.
 * H живе як два пласкі CSR-списки суміжності — жодного нуля матриці. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int n, m;                   /* бітів, перевірок */
    int *chk_ptr, *chk_bit;     /* перевірка -> її біти  */
    int *bit_ptr, *bit_chk;     /* біт -> його перевірки */
} ldpc_t;

/* checks[j] — індекси бітів перевірки j, deg[j] — скільки їх. */
ldpc_t *ldpc_build(int n, int m, const int *const *checks, const int *deg)
{
    ldpc_t *h = calloc(1, sizeof *h);
    h->n = n;
    h->m = m;
    h->chk_ptr = malloc((size_t)(m + 1) * sizeof(int));
    h->bit_ptr = calloc((size_t)(n + 1), sizeof(int));

    int edges = 0;
    h->chk_ptr[0] = 0;
    for (int j = 0; j < m; j++) {
        edges += deg[j];
        h->chk_ptr[j + 1] = edges;
    }
    h->chk_bit = malloc((size_t)edges * sizeof(int));
    h->bit_chk = malloc((size_t)edges * sizeof(int));

    for (int j = 0; j < m; j++)
        for (int k = 0; k < deg[j]; k++) {
            h->chk_bit[h->chk_ptr[j] + k] = checks[j][k];
            h->bit_ptr[checks[j][k] + 1]++;         /* ступені бітів */
        }
    for (int i = 0; i < n; i++)                     /* префіксна сума -> зсуви */
        h->bit_ptr[i + 1] += h->bit_ptr[i];

    int *fill = malloc((size_t)n * sizeof(int));
    memcpy(fill, h->bit_ptr, (size_t)n * sizeof(int));
    for (int j = 0; j < m; j++)
        for (int k = 0; k < deg[j]; k++)
            h->bit_chk[fill[checks[j][k]]++] = j;
    free(fill);
    return h;
}

static void syndrome(const ldpc_t *h, const uint8_t *w, uint8_t *s)
{
    for (int j = 0; j < h->m; j++) {
        uint8_t acc = 0;
        for (int t = h->chk_ptr[j]; t < h->chk_ptr[j + 1]; t++)
            acc ^= w[h->chk_bit[t]];
        s[j] = acc;
    }
}

static int syndrome_zero(const uint8_t *s, int m)
{
    for (int j = 0; j < m; j++)
        if (s[j])
            return 0;
    return 1;
}

/* Править w на місці. Повертає число ітерацій; *ok = 1, якщо H·ŵᵀ = 0. */
int ldpc_bitflip(const ldpc_t *h, uint8_t *w, int max_iter, int *ok)
{
    uint8_t *s = malloc((size_t)h->m);
    if (!s) { *ok = 0; return 0; }
    syndrome(h, w, s);

    int it = 0;
    for (; it < max_iter; it++) {
        if (syndrome_zero(s, h->m)) {
            *ok = 1;
            free(s);
            return it;
        }

        int worst = -1, worst_score = 0;
        for (int i = 0; i < h->n; i++) {
            int score = 0;
            for (int t = h->bit_ptr[i]; t < h->bit_ptr[i + 1]; t++)
                score += s[h->bit_chk[t]];
            if (score > worst_score) {      /* строге > : за нічиєї виграє менший індекс */
                worst_score = score;
                worst = i;
            }
        }
        if (worst < 0)
            break;                          /* звинуватити нікого — глухий кут */

        w[worst] ^= 1;
        for (int t = h->bit_ptr[worst]; t < h->bit_ptr[worst + 1]; t++)
            s[h->bit_chk[t]] ^= 1;          /* інкрементно */
    }

    *ok = syndrome_zero(s, h->m);
    free(s);
    return it;
}
