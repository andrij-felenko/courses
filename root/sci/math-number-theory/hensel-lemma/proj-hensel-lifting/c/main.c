#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Обчислення модульного оберненого елемента за розширеним алгоритмом Евкліда */
static int64_t mod_inverse(int64_t a, int64_t m) {
    int64_t m0 = m;
    int64_t y = 0, x = 1;
    if (m == 1) return 0;
    
    a = (a % m + m) % m;
    while (a > 1) {
        int64_t q = a / m;
        int64_t t = m;
        m = a % m;
        a = t;
        t = y;
        y = x - q * y;
        x = t;
    }
    if (x < 0) x += m0;
    return x;
}

/* Обчислення значення багаточлена f(x) за допомогою схеми Горнера */
static int64_t eval_poly(const int64_t* poly, size_t deg, int64_t x, int64_t mod) {
    int64_t result = 0;
    for (ssize_t i = (ssize_t)deg; i >= 0; --i) {
        result = (result * x + poly[i]) % mod;
        if (result < 0) result += mod;
    }
    return result;
}

/* Обчислення значення похідної f'(x) за допомогою схеми Горнера */
static int64_t eval_derivative(const int64_t* poly, size_t deg, int64_t x, int64_t mod) {
    if (deg == 0) return 0;
    int64_t result = 0;
    for (ssize_t i = (ssize_t)deg; i >= 1; --i) {
        int64_t coeff = (poly[i] * i) % mod;
        result = (result * x + coeff) % mod;
        if (result < 0) result += mod;
    }
    return result;
}

/* Лінійний підйом Гензеля: збільшує степінь модулю на 1 на кожному кроці */
bool hensel_lift_linear(const int64_t* poly, size_t deg, int64_t p, int target_k, int64_t r1, int64_t* out_root) {
    int64_t current_root = r1 % p;
    if (current_root < 0) current_root += p;

    /* Перевірка умови звичайного підйому */
    int64_t f_prime = eval_derivative(poly, deg, current_root, p);
    if (f_prime % p == 0) {
        fprintf(stderr, "Error: f'(r1) = 0 (mod p). Root is singular.\n");
        return false;
    }

    int64_t p_pow = p;
    for (int step = 1; step < target_k; ++step) {
        /* Обчислюємо q = f(current_root) / p_pow */
        int64_t p_next = p_pow * p;
        int64_t f_val = eval_poly(poly, deg, current_root, p_next);
        int64_t q = f_val / p_pow;

        /* Знаходимо обернену похідну за модулем p */
        int64_t v = mod_inverse(f_prime, p);
        int64_t t = (-q * v) % p;
        if (t < 0) t += p;

        current_root = current_root + t * p_pow;
        p_pow = p_next;
    }

    *out_root = current_root;
    return true;
}

int main(void) {
    /* Приклад: f(x) = x^2 - 7 = 0 (mod 3^5) */
    int64_t poly[3] = {-7, 0, 1}; /* -7 + 0*x + 1*x^2 */
    size_t deg = 2;
    int64_t p = 3;
    int target_k = 5; /* 3^5 = 243 */
    int64_t root1 = 1; /* f(1) = -6 = 0 (mod 3) */

    int64_t lifted_root = 0;
    if (hensel_lift_linear(poly, deg, p, target_k, root1, &lifted_root)) {
        printf("Root mod %ld^%d (%ld): %ld\n", p, target_k, (long)(243), (long)lifted_root);
        int64_t check = eval_poly(poly, deg, lifted_root, 243);
        printf("Verification f(%ld) mod 243 = %ld\n", (long)lifted_root, (long)check);
    }
    return 0;
}
