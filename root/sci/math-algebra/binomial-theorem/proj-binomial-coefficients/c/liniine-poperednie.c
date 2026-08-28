#include <stdint.h>
#include <stdlib.h>

#define MOD 1000000007ULL

// Швидке модулярне піднесення до степеня O(log exp)
static uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

typedef struct {
    uint64_t *fact;
    uint64_t *inv_fact;
    uint32_t max_n;
} CombMod;

CombMod *comb_mod_init(uint32_t max_n) {
    CombMod *cm = (CombMod *)malloc(sizeof(CombMod));
    if (!cm) return NULL;
    cm->max_n = max_n;
    cm->fact = (uint64_t *)malloc((max_n + 1) * sizeof(uint64_t));
    cm->inv_fact = (uint64_t *)malloc((max_n + 1) * sizeof(uint64_t));
    if (!cm->fact || !cm->inv_fact) {
        free(cm->fact);
        free(cm->inv_fact);
        free(cm);
        return NULL;
    }

    cm->fact[0] = 1;
    for (uint32_t i = 1; i <= max_n; ++i) {
        cm->fact[i] = (cm->fact[i - 1] * i) % MOD;
    }

    cm->inv_fact[max_n] = power_mod(cm->fact[max_n], MOD - 2, MOD);
    for (int32_t i = (int32_t)max_n - 1; i >= 0; --i) {
        cm->inv_fact[i] = (cm->inv_fact[i + 1] * (i + 1)) % MOD;
    }
    return cm;
}

uint64_t ncr_mod(const CombMod *cm, uint32_t n, uint32_t k) {
    if (!cm || k > n) return 0;
    return (cm->fact[n] * cm->inv_fact[k] % MOD) * cm->inv_fact[n - k] % MOD;
}

void comb_mod_free(CombMod *cm) {
    if (cm) {
        free(cm->fact);
        free(cm->inv_fact);
        free(cm);
    }
}
