#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef double complex Complex;

/* Швидке піднесення до степеня за модулем */
static long long power_mod(long long base, long long exp, long long mod) {
    long long res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

/* Перевірка, чи є g первісним коренем mod p */
static bool is_primitive_root(long long g, long long p) {
    long long phi = p - 1;
    long long n = phi;
    for (long long i = 2; i * i <= n; i++) {
        if (n % i == 0) {
            if (power_mod(g, phi / i, p) == 1) return false;
            while (n % i == 0) n /= i;
        }
    }
    if (n > 1) {
        if (power_mod(g, phi / n, p) == 1) return false;
    }
    return true;
}

/* Пошук найменшого первісного кореня mod p */
static long long find_primitive_root(long long p) {
    for (long long g = 2; g < p; g++) {
        if (is_primitive_root(g, p)) return g;
    }
    return -1;
}

/* Побудова таблиці дискретних логарифмів ind_g(x) */
static int* build_log_table(long long p, long long g) {
    int* log_table = (int*)malloc(sizeof(int) * p);
    if (!log_table) return NULL;
    
    long long cur = 1;
    for (int exp = 0; exp < p - 1; exp++) {
        log_table[cur] = exp;
        cur = (cur * g) % p;
    }
    log_table[0] = -1; /* χ(0) = 0 */
    return log_table;
}

/* Обчислення характеру χ_k(x) = exp(2π i · k · ind_g(x) / (p - 1)) */
static Complex eval_character(int x, int k, long long p, const int* log_table) {
    if (x == 0) return 0.0 + 0.0 * I;
    int idx = log_table[x];
    double angle = 2.0 * M_PI * ((double)(k * idx) / (double)(p - 1));
    return cos(angle) + sin(angle) * I;
}

/* Обчислення суми Якобі J(χ_a, χ_b) над F_p */
Complex compute_jacobi_sum(int a, int b, long long p, const int* log_table) {
    Complex sum = 0.0 + 0.0 * I;
    for (int t = 0; t < p; t++) {
        int t2 = (1 - t + p) % p;
        Complex c1 = eval_character(t, a, p, log_table);
        Complex c2 = eval_character(t2, b, p, log_table);
        sum += c1 * c2;
    }
    return sum;
}

/* Підрахунок кількості розв'язків x^n + y^n = 1 mod p через суми Якобі */
long long count_fermat_points_jacobi(int n, long long p, const int* log_table) {
    long long phi = p - 1;
    if (phi % n != 0) return -1;
    
    int step = (int)(phi / n);
    Complex total_jacobi_sum = 0.0 + 0.0 * I;
    
    for (int i = 1; i < n; i++) {
        for (int j = 1; j < n; j++) {
            total_jacobi_sum += compute_jacobi_sum(i * step, j * step, p, log_table);
        }
    }
    
    /* N = p + ∑ J(χ^i, χ^j) */
    double real_part = creal(total_jacobi_sum);
    return p + (long long)round(real_part);
}

int main(void) {
    long long p = 13;
    int n = 4; /* Квартична крива x^4 + y^4 = 1 mod 13 */
    
    long long g = find_primitive_root(p);
    printf("Поле F_%lld, первісний корінь g = %lld\n", p, g);
    
    int* log_table = build_log_table(p, g);
    if (!log_table) return 1;
    
    Complex j11 = compute_jacobi_sum(3, 3, p, log_table);
    printf("Сума Якобі J(χ³, χ³) = %.4f + %.4fi\n", creal(j11), cimag(j11));
    printf("Модуль |J(χ³, χ³)| = %.4f (Очікується √13 ≈ %.4f)\n", cabs(j11), sqrt((double)p));
    
    long long points = count_fermat_points_jacobi(n, p, log_table);
    printf("Кількість точок на x^%d + y^%d = 1 (mod %lld) дорівнює: %lld\n", n, n, p, points);
    
    free(log_table);
    return 0;
}
