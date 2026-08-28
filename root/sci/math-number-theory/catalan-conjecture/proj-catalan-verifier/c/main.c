#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint64_t val;
    uint32_t base;
    uint32_t exp;
} PowerItem;

// 128-бітна арифметика для піднесення до степеня за модулем (base^exp % mod)
uint64_t mod_pow128(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (unsigned __int128)result * base % mod;
        }
        base = (unsigned __int128)base * base % mod;
        exp /= 2;
    }
    return result;
}

// Перевірка умови Віферіха для пари простих чисел (p, q)
bool check_wieferich_pair(uint64_t p, uint64_t q) {
    if (p <= 1 || q <= 1 || p == q) return false;
    uint64_t q2 = q * q;
    uint64_t p2 = p * p;
    
    bool cond1 = (mod_pow128(p, q - 1, q2) == 1);
    bool cond2 = (mod_pow128(q, p - 1, p2) == 1);
    
    return cond1 && cond2;
}

int compare_powers(const void *a, const void *b) {
    uint64_t v1 = ((const PowerItem *)a)->val;
    uint64_t v2 = ((const PowerItem *)b)->val;
    if (v1 < v2) return -1;
    if (v1 > v2) return 1;
    return 0;
}

void search_consecutive_powers(uint64_t limit) {
    size_t capacity = 1024;
    size_t count = 0;
    PowerItem *powers = malloc(capacity * sizeof(PowerItem));
    if (!powers) return;

    for (uint64_t u = 2; u * u <= limit; u++) {
        uint64_t val = u * u;
        uint32_t v = 2;
        while (val <= limit) {
            if (count >= capacity) {
                capacity *= 2;
                PowerItem *temp = realloc(powers, capacity * sizeof(PowerItem));
                if (!temp) {
                    free(powers);
                    return;
                }
                powers = temp;
            }
            powers[count].val = val;
            powers[count].base = (uint32_t)u;
            powers[count].exp = v;
            count++;
            
            if (limit / u < val) break; // Захист від переповнення при множенні
            val *= u;
            v++;
        }
    }

    qsort(powers, count, sizeof(PowerItem), compare_powers);

    // Пошук елементів із різницею 1
    for (size_t i = 0; i + 1 < count; i++) {
        if (powers[i + 1].val - powers[i].val == 1) {
            printf("Знайдено розв'язок: %u^%u - %u^%u = %glu - %glu = 1\n",
                   powers[i + 1].base, powers[i + 1].exp,
                   powers[i].base, powers[i].exp,
                   (unsigned long)powers[i + 1].val, (unsigned long)powers[i].val);
        }
    }

    free(powers);
}

int main(void) {
    uint64_t limit = 100000ULL;
    printf("Пошук сусідніх степенів (C) до N = %llu...\n", (unsigned long long)limit);
    search_consecutive_powers(limit);
    
    uint64_t p = 3, q = 2;
    printf("Пара Віферіха (%llu, %llu): %s\n",
           (unsigned long long)p, (unsigned long long)q,
           check_wieferich_pair(p, q) ? "так" : "ні");
    return 0;
}
