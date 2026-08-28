#include <stdio.h>

void powerset(const char *xs[], int n) {
    for (unsigned mask = 0; mask < (1u << n); mask++) {  /* 0 … 2ⁿ−1 */
        printf("{");
        for (int i = 0; i < n; i++)
            if (mask >> i & 1)         /* біт i стоїть? → беремо xs[i] */
                printf(" %s", xs[i]);
        printf(" }\n");
    }
}

int main(void) {
    const char *xs[] = { "a", "b", "c" };
    powerset(xs, 3);                   /* 2³ = 8 рядків */
    return 0;
}
