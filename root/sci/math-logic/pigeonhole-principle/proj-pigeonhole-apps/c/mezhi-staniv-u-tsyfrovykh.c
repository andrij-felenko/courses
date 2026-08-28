#include <stdio.h>
#include <stdlib.h>

typedef struct {
    unsigned int period;
    unsigned int pre_period;
} LcgAnalysis;

LcgAnalysis analyze_lcg_period(unsigned int a, unsigned int c, unsigned int m, unsigned int seed) {
    LcgAnalysis res = { 0, 0 };
    if (m == 0) return res;

    // Масив для фіксації кроку, на якому стан зустрічається вперше (-1 = не зустрічався)
    int* visited_at = (int*)malloc(m * sizeof(int));
    if (!visited_at) return res;

    for (unsigned int i = 0; i < m; ++i) {
        visited_at[i] = -1;
    }

    unsigned int current = seed % m;
    int step = 0;

    while (visited_at[current] == -1) {
        visited_at[current] = step;
        current = (unsigned int)(((unsigned long long)a * current + c) % m);
        step++;
    }

    // За принципом Діріхле колізія настає не пізніше m кроків!
    res.pre_period = (unsigned int)visited_at[current];
    res.period = (unsigned int)step - res.pre_period;

    free(visited_at);
    return res;
}

int main(void) {
    // Приклад LCG: a=5, c=3, m=16, seed=1
    unsigned int a = 5, c = 3, m = 16, seed = 1;
    LcgAnalysis res = analyze_lcg_period(a, c, m, seed);

    printf("LCG (a=%u, c=%u, m=%u, seed=%u):\n", a, c, m, seed);
    printf("  Додовжина хвоста (pre-period): %u\n", res.pre_period);
    printf("  Період зациклення P (≤ m):      %u\n", res.period);

    return 0;
}
