/* Швидкий декодер першого порядку RM(1,m) — «зелена машина».
   Одне перетворення Адамара дає всі 2^m кореляцій; пік — це відповідь. */
void rm_decode_fht(int m, const int *recv, int *msg) {
    int n = 1 << m;
    int H[RM_MAXN];
    for (int t = 0; t < n; t++) H[t] = 1 - 2 * recv[t];     /* 0→+1, 1→−1 */

    for (int len = 1; len < n; len <<= 1)                   /* швидкий Адамар */
        for (int i = 0; i < n; i += len << 1)
            for (int j = i; j < i + len; j++) {
                int u = H[j], v = H[j + len];
                H[j]       = u + v;
                H[j + len] = u - v;
            }

    int best = 0;                                           /* argmax |H[a]| */
    for (int a = 1; a < n; a++)
        if (abs(H[a]) > abs(H[best])) best = a;

    for (int S = 0; S < n; S++) msg[S] = 0;
    msg[0] = (H[best] < 0) ? 1 : 0;                         /* a0 — зі знаку */
    for (int i = 0; i < m; i++)                             /* a_i — біти піку */
        if (best & (1 << i)) msg[1 << i] = 1;
}
