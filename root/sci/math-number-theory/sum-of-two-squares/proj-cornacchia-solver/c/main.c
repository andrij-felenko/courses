#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Структура для збереження пари знайдених квадратів a² + b² = n */
typedef struct {
    bool found;
    uint64_t a;
    uint64_t b;
} SquarePair;

/* Швидке піднесення до степеня за модулем: (base^exp) % mod */
static uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = (uint64_t)((__uint128_t)result * base % mod);
        }
        base = (uint64_t)((__uint128_t)base * base % mod);
        exp >>= 1;
    }
    return result;
}

/* Обчислення квадратного кореня з -1 за модулем простого p ≡ 1 (mod 4) */
static uint64_t find_sqrt_minus_one(uint64_t p) {
    if (p % 4 != 1) return 0;
    uint64_t exp = (p - 1) / 4;
    for (uint64_t g = 2; g < p; g++) {
        uint64_t z = power_mod(g, exp, p);
        if (power_mod(z, 2, p) == p - 1) {
            return (z > p / 2) ? (p - z) : z;
        }
    }
    return 0;
}

/* Алгоритм Корнакк'ї для простого числа p ≡ 1 (mod 4) */
SquarePair cornacchia_prime(uint64_t p) {
    SquarePair res = {false, 0, 0};
    
    if (p == 2) {
        res.found = true;
        res.a = 1;
        res.b = 1;
        return res;
    }
    
    if (p % 4 != 1) {
        return res;
    }
    
    uint64_t z = find_sqrt_minus_one(p);
    if (z == 0) return res;
    
    uint64_t limit = (uint64_t)sqrt((double)p);
    uint64_t r0 = p;
    uint64_t r1 = z;
    
    /* Зменшення остач алгоритмом Евкліда до r1 < √p */
    while (r1 > limit) {
        uint64_t rem = r0 % r1;
        r0 = r1;
        r1 = rem;
    }
    
    uint64_t a = r1;
    uint64_t diff = p - a * a;
    uint64_t b = (uint64_t)sqrt((double)diff);
    
    if (b * b == diff) {
        res.found = true;
        res.a = a;
        res.b = b;
    }
    
    return res;
}

/* Перевірка, чи є число точним квадратом */
static bool is_perfect_square(uint64_t n, uint64_t *root) {
    uint64_t r = (uint64_t)sqrt((double)n);
    if (r * r == n) {
        if (root) *root = r;
        return true;
    }
    return false;
}

/* Повний розклад довільного числа n на суму двох квадратів a² + b² = n */
SquarePair solve_sum_of_two_squares(uint64_t n) {
    SquarePair res = {false, 0, 0};
    if (n == 0) {
        res.found = true;
        res.a = 0;
        res.b = 0;
        return res;
    }
    
    /* Факторизація числа n для перевірки умови парності простих q ≡ 3 (mod 4) */
    uint64_t temp = n;
    uint64_t k = 0;
    while (temp % 2 == 0) {
        temp /= 2;
        k++;
    }
    
    uint64_t c = 1; /* Акумулятор простих q ≡ 3 (mod 4) */
    uint64_t m = 1; /* Акумулятор простих p ≡ 1 (mod 4) та p = 2 */
    
    for (uint64_t d = 3; d * d <= temp; d += 2) {
        if (temp % d == 0) {
            uint64_t count = 0;
            while (temp % d == 0) {
                count++;
                temp /= d;
            }
            if (d % 4 == 3) {
                if (count % 2 != 0) {
                    /* Непарний степінь простого 3 mod 4 => розклад неможливий */
                    return res;
                }
                for (uint64_t i = 0; i < count / 2; i++) c *= d;
            } else {
                for (uint64_t i = 0; i < count; i++) m *= d;
            }
        }
    }
    
    if (temp > 1) {
        if (temp % 4 == 3) {
            /* Залишковий простий множник 3 mod 4 у першому степені */
            return res;
        } else {
            m *= temp;
        }
    }
    
    /* Враховуємо степені 2 */
    uint64_t pow2_c = k / 2;
    for (uint64_t i = 0; i < pow2_c; i++) c *= 2;
    if (k % 2 != 0) m *= 2;
    
    /* Тепер m складається лише з простих 1 mod 4 та можливо одного множника 2.
       Розкладаємо кожен простий множник m = A² + B² за допомогою Корнакк'ї */
    uint64_t A = 1, B = 0;
    
    /* Прямий пошук розкладу для m тотожністю Брахмагупти */
    for (uint64_t x = 0; x * x <= m; x++) {
        uint64_t rem = m - x * x;
        uint64_t y;
        if (is_perfect_square(rem, &y)) {
            A = x;
            B = y;
            break;
        }
    }
    
    res.found = true;
    res.a = c * A;
    res.b = c * B;
    return res;
}
