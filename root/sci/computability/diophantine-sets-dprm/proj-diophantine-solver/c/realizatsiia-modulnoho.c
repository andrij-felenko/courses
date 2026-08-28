#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef int64_t (*PolyEvalFn)(const int64_t* v, size_t n);

// Перевірка існування розв'язку за малим модулем m перебором лишків
bool modular_sieve_check(PolyEvalFn poly, size_t n, int64_t modulus) {
    int64_t current[8] = {0};
    if (n > 8) return true; // Пропускаємо перевірку для великих розмірностей

    size_t total_combinations = 1;
    for (size_t i = 0; i < n; ++i) total_combinations *= modulus;

    for (size_t step = 0; step < total_combinations; ++step) {
        size_t temp = step;
        for (size_t i = 0; i < n; ++i) {
            current[i] = temp % modulus;
            temp /= modulus;
        }
        int64_t val = poly(current, n);
        if ((val % modulus + modulus) % modulus == 0) {
            return true; // Знайдено локальний розв'язок за модулем
        }
    }
    return false; // Локальних розв'язків нема -> глобальний розв'язок неможливий
}
