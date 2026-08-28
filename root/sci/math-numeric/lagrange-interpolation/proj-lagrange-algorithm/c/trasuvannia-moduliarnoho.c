#include <stdio.h>
#include <stdint.h>

// Просте число p для скінченного поля GF(p)
#define MOD_P 1000000007LL

// Обчислення a^b mod p
static int64_t power_mod(int64_t base, int64_t exp) {
    int64_t res = 1;
    base %= MOD_P;
    while (exp > 0) {
        if (exp % 2 == 1) res = (__int128)res * base % MOD_P;
        base = (__int128)base * base % MOD_P;
        exp /= 2;
    }
    return res;
}

// Обернений елемент a^-1 mod p за малою теоремою Ферма
static int64_t mod_inverse(int64_t n) {
    return power_mod(n, MOD_P - 2);
}

// Відновлення секрету P(0) над GF(p)
int64_t gf_lagrange_reconstruct_secret(const int64_t* x, const int64_t* y, size_t k) {
    int64_t secret = 0;

    for (size_t i = 0; i < k; ++i) {
        int64_t num = 1;
        int64_t den = 1;

        for (size_t j = 0; j < k; ++j) {
            if (i != j) {
                num = (__int128)num * (MOD_P - x[j]) % MOD_P;
                int64_t diff = (x[i] - x[j] + MOD_P) % MOD_P;
                den = (__int128)den * diff % MOD_P;
            }
        }

        int64_t term = (__int128)y[i] * num % MOD_P;
        term = (__int128)term * mod_inverse(den) % MOD_P;
        secret = (secret + term) % MOD_P;
    }

    return secret;
}

int main(void) {
    // 3 частки з 5 для відкриття секрету: (1, 12345), (2, 54321), (3, 98765)
    int64_t x_shares[3] = {1, 2, 3};
    int64_t y_shares[3] = {14892, 45293, 91216};

    int64_t secret = gf_lagrange_reconstruct_secret(x_shares, y_shares, 3);
    printf("Відновлений криптографічний секрет S = %lld\n", (long long)secret);
    return 0;
}
