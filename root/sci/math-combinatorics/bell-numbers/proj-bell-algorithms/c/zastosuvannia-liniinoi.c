#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* Обчислення B_n mod p для простого p за допомогою рекурентності Тушара.
   Часова складність: O(p^2 + n), пам'ять O(p) */
uint64_t bell_mod_p(uint64_t n, uint64_t p) {
    if (p <= 1) return 0;
    if (n == 0 || n == 1) return 1 % p;

    /* Базовий масив розміром p + 1 для зсуву Тушара */
    uint64_t *b = (uint64_t *)calloc(p + 1, sizeof(uint64_t));
    if (!b) return 0;

    /* Крок 1. Обчислюємо перші p + 1 чисел Белла за модулем p через трикутник */
    uint64_t *row = (uint64_t *)calloc(p + 1, sizeof(uint64_t));
    if (!row) { free(b); return 0; }

    row[0] = 1;
    b[0] = 1 % p;

    for (uint64_t i = 1; i <= p; ++i) {
        uint64_t prev = row[i - 1];
        row[0] = prev;
        for (uint64_t j = 1; j <= i; ++j) {
            uint64_t temp = row[j];
            row[j] = (row[j - 1] + prev) % p;
            prev = temp;
        }
        b[i] = row[i];
    }
    free(row);

    /* Крок 2. Якщо n <= p, повертаємо готовий результат */
    if (n <= p) {
        uint64_t res = b[n];
        free(b);
        return res;
    }

    /* Крок 3. Використовуємо порівняння Тушара: B_{k+p} = (B_{k+1} + B_k) mod p */
    size_t cap = (size_t)(p + 1);
    for (uint64_t k = 1; k <= n - p; ++k) {
        size_t idx_kp = (size_t)((k + p) % cap);
        size_t idx_k1 = (size_t)((k + 1) % cap);
        size_t idx_k  = (size_t)(k % cap);

        b[idx_kp] = (b[idx_k1] + b[idx_k]) % p;
    }

    uint64_t result = b[n % cap];
    free(b);
    return result;
}

int main(void) {
    uint64_t n = 100;
    uint64_t p = 7;
    printf("B_%llu mod %llu = %llu\n", (unsigned long long)n, (unsigned long long)p,
           (unsigned long long)bell_mod_p(n, p));
    return 0;
}
