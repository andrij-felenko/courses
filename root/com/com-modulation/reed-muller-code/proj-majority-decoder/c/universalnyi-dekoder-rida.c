/* Універсальний мажоритарний декодер Ріда для RM(r,m).
   recv[] — прийняте слово (n бітів 0/1); msg[] — відновлені коефіцієнти. */
void rm_decode_reed(int m, int r, const int *recv, int *msg) {
    int n = 1 << m;
    int work[RM_MAXN];
    for (int t = 0; t < n; t++) work[t] = recv[t];      /* робочий залишок */
    for (int S = 0; S < n; S++) msg[S] = 0;

    for (int s = r; s >= 0; s--) {
        /* 1. голосуємо за кожен коефіцієнт степеня s */
        for (int S = 0; S < n; S++) {
            if (popcount((unsigned)S) != s) continue;
            int comp = (n - 1) ^ S;                     /* координати поза S */
            int ones = 0, total = 0, y = comp;
            for (;;) {                                  /* y — зсув підкуба */
                int parity = 0, z = S;
                for (;;) {                              /* z — точка підкуба */
                    parity ^= work[y | z];
                    if (z == 0) break;
                    z = (z - 1) & S;
                }
                ones += parity; total++;
                if (y == 0) break;
                y = (y - 1) & comp;
            }
            msg[S] = (2 * ones > total) ? 1 : 0;        /* строга більшість */
        }
        /* 2. віднімаємо знайдений шар степеня s із залишку */
        for (int t = 0; t < n; t++) {
            int contrib = 0;
            for (int S = 0; S < n; S++)
                if (popcount((unsigned)S) == s && msg[S] && ((t & S) == S))
                    contrib ^= 1;
            work[t] ^= contrib;
        }
    }
}
