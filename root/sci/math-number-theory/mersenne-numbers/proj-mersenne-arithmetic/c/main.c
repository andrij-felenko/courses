#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>

// Швидке безділильне приведення 64-бітного числа x за модулем M_n = 2^n - 1.
// Параметри:
//   x — вхідне беззнакове 64-бітне ціле число;
//   n — ширина модуля в бітах (1 <= n <= 31).
// Повертає:
//   x mod (2^n - 1) у канонічному діапазоні [0, 2^n - 2].
uint64_t mersenne_mod64(uint64_t x, uint32_t n) {
    const uint64_t mask = (1ULL << n) - 1ULL;
    while (x > mask) {
        uint64_t high = x >> n;
        uint64_t low = x & mask;
        x = high + low;
    }
    // Граничний випадок: якщо x == mask (тобто 2^n - 1), залишок дорівнює 0
    if (x == mask) {
        return 0ULL;
    }
    return x;
}

// Швидке множення двох чисел за модулем M_n = 2^n - 1 без апаратного ділення.
// Використовує 128-бітний проміжний добуток та двохетапне бітове згортання.
uint64_t mersenne_mul64(uint64_t a, uint64_t b, uint32_t n) {
    const uint64_t mask = (1ULL << n) - 1ULL;
    unsigned __int128 prod = (unsigned __int128)a * (unsigned __int128)b;
    
    while (prod > (unsigned __int128)mask) {
        unsigned __int128 high = prod >> n;
        unsigned __int128 low = prod & (unsigned __int128)mask;
        prod = high + low;
    }
    
    uint64_t res = (uint64_t)prod;
    if (res == mask) {
        return 0ULL;
    }
    return res;
}

// Швидке модульне піднесення до степеня base^exp mod (2^n - 1).
uint64_t mersenne_pow64(uint64_t base, uint64_t exp, uint32_t n) {
    uint64_t result = 1ULL;
    base = mersenne_mod64(base, n);
    
    while (exp > 0ULL) {
        if (exp & 1ULL) {
            result = mersenne_mul64(result, base, n);
        }
        base = mersenne_mul64(base, base, n);
        exp >>= 1ULL;
    }
    return result;
}

// Загальне бінарне піднесення до степеня 2^p mod q для довільного модуля q.
static uint64_t mod_exp_2_pow(uint32_t p, uint64_t q) {
    uint64_t base = 2ULL % q;
    uint64_t exp = (uint64_t)p;
    uint64_t rem = 1ULL;
    
    while (exp > 0ULL) {
        if (exp & 1ULL) {
            rem = (uint64_t)(((unsigned __int128)rem * base) % q);
        }
        base = (uint64_t)(((unsigned __int128)base * base) % q);
        exp >>= 1ULL;
    }
    return rem;
}

// Оптимізований пошук найменшого простого дільника для M_p = 2^p - 1.
// Параметри:
//   p — простий показник числа Мерсенна;
//   limit_k — максимальна кількість кроків k у прогресії q = 2*k*p + 1.
// Повертає:
//   знайдений простий дільник q або 0, якщо дільник не знайдено в межах limit_k.
uint64_t find_mersenne_factor(uint32_t p, uint64_t limit_k) {
    const uint64_t m_val = (p < 63) ? ((1ULL << p) - 1ULL) : 0ULL;

    for (uint64_t k = 1ULL; k <= limit_k; ++k) {
        uint64_t q = 2ULL * k * (uint64_t)p + 1ULL;
        
        // Перевірка межі квадратного кореня (якщо M_p вміщується в 64 біти)
        if (p < 63 && m_val > 0ULL) {
            if (q > m_val / q) {
                break;
            }
        }

        // Перша фільтрація: перевірка квадратичної умови q ≡ ±1 (mod 8)
        uint64_t mod8 = q & 7ULL; // q % 8
        if (mod8 != 1ULL && mod8 != 7ULL) {
            continue;
        }

        // Друга фільтрація: бінарне піднесення 2^p mod q == 1
        uint64_t rem = mod_exp_2_pow(p, q);
        if (rem == 1ULL) {
            return q; // Дільник знайдено
        }
    }

    return 0ULL; // Дільник у заданій межі k не знайдено
}

// Функція верифікації правильності дільника числа Мерсенна.
bool verify_mersenne_factor(uint32_t p, uint64_t factor) {
    if (factor == 0ULL) {
        return false;
    }
    return (mod_exp_2_pow(p, factor) == 1ULL);
}

int main(void) {
    printf("=== Демонстрація модульної арифметики Мерсенна (C99) ===\n\n");

    // Тест 1: Перевірка безділильного зведення за модулем M_13 = 8191
    uint64_t x = 123456789ULL;
    uint32_t n = 13;
    uint64_t fast_res = mersenne_mod64(x, n);
    uint64_t slow_res = x % ((1ULL << n) - 1ULL);
    printf("Тест 1: Безділильне зведення (x = %" PRIu64 ", n = %" PRIu32 "):\n", x, n);
    printf("  Швидке зведення (mersenne_mod64): %" PRIu64 "\n", fast_res);
    printf("  Еталонне ділення (x %% M_n):        %" PRIu64 "\n", slow_res);
    printf("  Статус: %s\n\n", (fast_res == slow_res) ? "УСПІШНО" : "ПОМИЛКА");

    // Тест 2: Модульне множення та степінь за модулем M_7 = 127
    uint64_t a = 45ULL, b = 80ULL;
    uint64_t mul_fast = mersenne_mul64(a, b, 7);
    uint64_t mul_slow = (a * b) % 127ULL;
    uint64_t pow_fast = mersenne_pow64(2ULL, 10ULL, 7); // 2^10 = 1024 = 8*127 + 8 -> 8
    printf("Тест 2: Модульне множення та степінь (модуль M_7 = 127):\n");
    printf("  (45 * 80) mod 127: швидке = %" PRIu64 ", еталон = %" PRIu64 "\n", mul_fast, mul_slow);
    printf("  (2^10) mod 127:    швидке = %" PRIu64 " (очікується 8)\n\n", pow_fast);

    // Тест 3: Факторизація M_11 = 2047 (p = 11)
    uint64_t f11 = find_mersenne_factor(11, 100);
    printf("Тест 3: Факторизація M_11 = 2^11 - 1 = 2047:\n");
    printf("  Знайдений дільник: %" PRIu64 " (очікується 23)\n", f11);
    printf("  Верифікація: %s\n\n", verify_mersenne_factor(11, f11) ? "ДІЙСНИЙ" : "НЕВІРНИЙ");

    // Тест 4: Факторизація M_23 = 8388607 (p = 23)
    uint64_t f23 = find_mersenne_factor(23, 100);
    printf("Тест 4: Факторизація M_23 = 2^23 - 1 = 8388607:\n");
    printf("  Знайдений дільник: %" PRIu64 " (очікується 47)\n", f23);
    printf("  Верифікація: %s\n\n", verify_mersenne_factor(23, f23) ? "ДІЙСНИЙ" : "НЕВІРНИЙ");

    // Тест 5: Факторизація M_29 = 536870911 (p = 29)
    uint64_t f29 = find_mersenne_factor(29, 1000);
    printf("Тест 5: Факторизація M_29 = 2^29 - 1 = 536870911:\n");
    printf("  Знайдений дільник: %" PRIu64 " (очікується 233)\n", f29);
    printf("  Верифікація: %s\n\n", verify_mersenne_factor(29, f29) ? "ДІЙСНИЙ" : "НЕВІРНИЙ");

    return 0;
}
