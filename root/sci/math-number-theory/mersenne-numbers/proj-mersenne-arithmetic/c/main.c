#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Швидке безділильне приведення 64-бітного числа x за модулем (2^n - 1).
// Параметри:
//   x — вхідне беззнакове 64-бітне ціле число;
//   n — ширина модуля в бітах (1 <= n <= 31).
// Повертає:
//   x mod (2^n - 1) у діапазоні [0, 2^n - 2].
uint64_t mersenne_mod64(uint64_t x, uint32_t n) {
    uint64_t mask = (1ULL << n) - 1ULL;
    while (x > mask) {
        uint64_t high = x >> n;
        uint64_t low = x & mask;
        x = high + low;
    }
    // Граничний випадок: якщо x == mask (тобто 2^n - 1), за модулем це 0
    if (x == mask) {
        return 0;
    }
    return x;
}

// Оптимізований пошук найменшого простого дільника для M_p = 2^p - 1.
// Параметри:
//   p — простий показник числа Мерсенна;
//   limit_k — максимальна кількість кроків k у прогресії q = 2*k*p + 1.
// Повертає:
//   знайдений простий дільник q або 0, якщо дільник не знайдено.
uint64_t find_mersenne_factor(uint32_t p, uint64_t limit_k) {
    uint64_t m_val = (p < 63) ? ((1ULL << p) - 1ULL) : 0;

    for (uint64_t k = 1; k <= limit_k; ++k) {
        uint64_t q = 2 * k * p + 1;
        
        // Перевірка межі квадратного кореня (якщо p вміщується в 64 біти)
        if (p < 63 && q * q > m_val) {
            break;
        }

        // Перша фільтрація: перевірка квадратичної умови q ≡ 1 або 7 (mod 8)
        uint64_t mod8 = q % 8;
        if (mod8 != 1 && mod8 != 7) {
            continue;
        }

        // Друга фільтрація: бінарне піднесення 2^p mod q
        uint64_t base = 2;
        uint64_t exp = p;
        uint64_t rem = 1;
        while (exp > 0) {
            if (exp & 1) {
                rem = (unsigned __int128)rem * base % q;
            }
            base = (unsigned __int128)base * base % q;
            exp >>= 1;
        }

        // Якщо 2^p mod q == 1, дільник знайдено!
        if (rem == 1) {
            return q;
        }
    }

    return 0; // Дільник у заданій межі не знайдено
}

int main(void) {
    printf("=== Демонстрація модульної арифметики Мерсенна (C99) ===\n\n");

    // Тест 1: Перевірка безділильного зведення
    uint64_t x = 123456789ULL;
    uint32_t n = 13; // Modulo M_13 = 8191
    uint64_t fast_res = mersenne_mod64(x, n);
    uint64_t slow_res = x % ((1ULL << n) - 1ULL);
    printf("Тест 1 (x = %glu, n = %u):\n", (unsigned long)x, n);
    printf("  Швидке безділильне зведення: %glu\n", (unsigned long)fast_res);
    printf("  Стандартне ділення (%s):      %glu\n\n", "%", (unsigned long)slow_res);

    // Тест 2: Пошук дільника для M_11 = 2047 (p = 11)
    uint64_t f11 = find_mersenne_factor(11, 100);
    printf("Тест 2 (M_11 = 2047):\n");
    printf("  Знайдений найменший простий дільник: %glu (очікується 23)\n\n", (unsigned long)f11);

    // Тест 3: Пошук дільника для M_23 = 8388607 (p = 23)
    uint64_t f23 = find_mersenne_factor(23, 100);
    printf("Тест 3 (M_23 = 8388607):\n");
    printf("  Знайдений найменший простий дільник: %glu (очікується 47)\n\n", (unsigned long)f23);

    // Тест 4: Пошук дільника для M_29 = 536870911 (p = 29)
    uint64_t f29 = find_mersenne_factor(29, 1000);
    printf("Тест 4 (M_29 = 536870911):\n");
    printf("  Знайдений найменший простий дільник: %glu (очікується 233)\n\n", (unsigned long)f29);

    return 0;
}
