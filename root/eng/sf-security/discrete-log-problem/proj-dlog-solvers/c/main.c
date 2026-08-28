#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>

// Модульне множення 64-бітних чисел через __int128_t
static inline uint64_t mod_mul(uint64_t a, uint64_t b, uint64_t mod) {
    return (uint64_t)(((__int128_t)a * b) % mod);
}

// Модульне піднесення до степеня
static uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) res = mod_mul(res, base, mod);
        base = mod_mul(base, base, mod);
        exp >>= 1;
    }
    return res;
}

// Розширений алгоритм Евкліда для обчислення оберненого елемента
static bool mod_inverse(uint64_t a, uint64_t mod, uint64_t *out_inv) {
    int64_t t = 0, newt = 1;
    int64_t r = (int64_t)mod, newr = (int64_t)a;

    while (newr != 0) {
        int64_t q = r / newr;
        int64_t temp_t = t - q * newt;
        t = newt;
        newt = temp_t;

        int64_t temp_r = r - q * newr;
        r = newr;
        newr = temp_r;
    }

    if (r > 1) return false;
    if (t < 0) t += (int64_t)mod;
    *out_inv = (uint64_t)t;
    return true;
}

// Структура запису для BSGS хеш-таблиці
typedef struct {
    uint64_t key;
    uint64_t val;
} bsgs_entry_t;

// Просте порівняння для qsort
static int compare_entries(const void *a, const void *b) {
    uint64_t k1 = ((const bsgs_entry_t*)a)->key;
    uint64_t k2 = ((const bsgs_entry_t*)a)->key;
    if (k1 < k2) return -1;
    if (k1 > k2) return 1;
    return 0;
}

// Пошук BSGS у впорядкованому масиві через бінарний пошук
static int64_t binary_search_entry(const bsgs_entry_t *arr, size_t size, uint64_t key) {
    size_t left = 0, right = size;
    while (left < right) {
        size_t mid = left + (right - left) / 2;
        if (arr[mid].key == key) return (int64_t)arr[mid].val;
        if (arr[mid].key < key) left = mid + 1;
        else right = mid;
    }
    return -1;
}

// Алгоритм BSGS мовою C
bool solve_dlog_bsgs(uint64_t g, uint64_t y, uint64_t p, uint64_t N, uint64_t *out_x, uint64_t *out_steps) {
    uint64_t m = (uint64_t)ceil(sqrt((double)N));
    bsgs_entry_t *table = (bsgs_entry_t*)malloc(m * sizeof(bsgs_entry_t));
    if (!table) return false;

    uint64_t cur = y % p;
    uint64_t steps = 0;

    // Заповнення baby steps
    for (uint64_t j = 0; j < m; ++j) {
        table[j].key = cur;
        table[j].val = j;
        cur = mod_mul(cur, g, p);
        steps++;
    }

    // Сортування масиву для бінарного пошуку O(m log m)
    qsort(table, m, sizeof(bsgs_entry_t), compare_entries);

    // Giant steps
    uint64_t factor = mod_pow(g, m, p);
    cur = factor;

    for (uint64_t i = 1; i <= m; ++i) {
        steps++;
        int64_t j = binary_search_entry(table, m, cur);
        if (j != -1) {
            *out_x = (i * m - (uint64_t)j) % N;
            *out_steps = steps;
            free(table);
            return true;
        }
        cur = mod_mul(cur, factor, p);
    }

    free(table);
    return false;
}

int main(void) {
    uint64_t p = 10007;
    uint64_t g = 5;
    uint64_t N = p - 1;
    uint64_t secret_x = 1234;
    uint64_t y = mod_pow(g, secret_x, p);

    uint64_t found_x = 0;
    uint64_t steps = 0;

    printf("[C implementation] Target secret x = %glu, y = %glu\n", secret_x, y);

    if (solve_dlog_bsgs(g, y, p, N, &found_x, &steps)) {
        printf("[C BSGS] Found x = %glu in %glu steps!\n", found_x, steps);
    } else {
        printf("[C BSGS] Failed to find discrete log.\n");
    }

    return 0;
}
