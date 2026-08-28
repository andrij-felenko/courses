#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

long long count_coprime_pairs(int n) {
    mobius_sieve_t sieve = create_mobius_sieve(n);
    long long* pref_m = (long long*)malloc((n + 1) * sizeof(long long));
    pref_m[0] = 0;
    for (int i = 1; i <= n; i++) {
        pref_m[i] = pref_m[i - 1] + sieve.mu[i];
    }

    long long total_pairs = 0;
    int l = 1;

    while (l <= n) {
        int k = n / l;
        int r = n / k;
        long long block_sum_mu = pref_m[r] - pref_m[l - 1];
        total_pairs += block_sum_mu * ((long long)k * k);
        l = r + 1;
    }

    free(pref_m);
    free_mobius_sieve(&sieve);
    return total_pairs;
}
