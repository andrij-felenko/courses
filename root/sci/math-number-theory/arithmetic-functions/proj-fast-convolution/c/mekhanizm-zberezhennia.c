#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int size;
    int *primes;
    int *mu;
    int *phi;
} SieveResult;

SieveResult init_sieve(int n) {
    SieveResult res;
    res.size = n;
    res.primes = (int *)malloc((n + 1) * sizeof(int));
    res.mu = (int *)malloc((n + 1) * sizeof(int));
    res.phi = (int *)malloc((n + 1) * sizeof(int));
    
    int *min_pow = (int *)malloc((n + 1) * sizeof(int));
    int prime_count = 0;

    res.mu[1] = 1;
    res.phi[1] = 1;

    for (int i = 2; i <= n; ++i) {
        if (min_pow[i] == 0) {
            res.primes[prime_count++] = i;
            res.mu[i] = -1;
            res.phi[i] = i - 1;
            min_pow[i] = i;
        }
        for (int j = 0; j < prime_count && res.primes[j] * i <= n; ++j) {
            int p = res.primes[j];
            int next = i * p;
            if (i % p == 0) {
                /* p є найменшим множником i; квадратичний дільник */
                res.mu[next] = 0;
                res.phi[next] = res.phi[i] * p;
                min_pow[next] = min_pow[i] * p;
                break;
            } else {
                /* p взаємно просте з i; використовуємо мультиплікативність */
                res.mu[next] = res.mu[i] * res.mu[p];
                res.phi[next] = res.phi[i] * res.phi[p];
                min_pow[next] = p;
            }
        }
    }

    free(min_pow);
    return res;
}

void free_sieve(SieveResult *res) {
    free(res->primes);
    free(res->mu);
    free(res->phi);
}

int main(void) {
    int n = 20;
    SieveResult sieve = init_sieve(n);

    printf("n\tmu(n)\tphi(n)\n");
    for (int i = 1; i <= n; ++i) {
        printf("%d\t%d\t%d\n", i, sieve.mu[i], sieve.phi[i]);
    }

    free_sieve(&sieve);
    return 0;
}
