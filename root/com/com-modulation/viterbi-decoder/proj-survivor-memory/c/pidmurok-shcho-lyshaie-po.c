#include <limits.h>
#include <string.h>

#define K    3
#define NU   (K - 1)              /* біти пам'яті коду: тут 2 */
#define S    (1u << NU)           /* число станів: 4 */
#define LOW  ((1u << (NU-1)) - 1) /* маска молодших ν−1 бітів стану */
#define D    10                   /* глибина вікна ≈ 5·(K−1) */

/* Ґратка коду (7,5): наступний стан і пакована пара виходів (v1<<1)|v2. */
static const int NXT[S][2] = {{0,2},{0,2},{1,3},{1,3}};
static const int OUT[S][2] = {{0,3},{3,0},{2,1},{1,2}};

static inline int hamm(int o, int r0, int r1) {
    return ((o >> 1) ^ r0) + ((o & 1) ^ r1);          /* відстань Геммінга пари */
}

/* Один такт ACS: нові метрики nm[] і один БІТ рішення на стан dec[] —
   молодший біт переможного попередника (його досить, щоб попередника відновити). */
static void acs(const int pm[S], int nm[S], unsigned dec[S], int r0, int r1) {
    for (unsigned d = 0; d < S; d++) { nm[d] = INT_MAX; dec[d] = 0; }
    for (unsigned s = 0; s < S; s++) {
        if (pm[s] == INT_MAX) continue;               /* у цей стан ще не дійшли */
        for (int u = 0; u < 2; u++) {
            int ns   = NXT[s][u];
            int cand = pm[s] + hamm(OUT[s][u], r0, r1);
            if (cand < nm[ns]) { nm[ns] = cand; dec[ns] = s & 1u; }  /* переможець */
        }
    }
}

static int best(const int m[S]) {                     /* стан із найменшою метрикою */
    int b = 0;
    for (unsigned s = 1; s < S; s++) if (m[s] < m[b]) b = s;
    return b;
}
