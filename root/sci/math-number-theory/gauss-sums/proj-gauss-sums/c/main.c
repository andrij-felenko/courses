#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Обчислення символу Лежандра (a/p) через критерій Ейлера a^((p-1)/2) mod p */
int legendre_symbol(long long a, long long p) {
    a = (a % p + p) % p;
    if (a == 0) return 0;
    
    long long result = 1;
    long long base = a;
    long long exp = (p - 1) / 2;
    
    while (exp > 0) {
        if (exp & 1) {
            result = (result * base) % p;
        }
        base = (base * base) % p;
        exp >>= 1;
    }
    
    return (result == 1) ? 1 : -1;
}

/* Розширений алгоритм Евкліда для пошуку оберненого елемента x^-1 mod m */
long long mod_inverse(long long a, long long m) {
    long long m0 = m, t, q;
    long long x0 = 0, x1 = 1;
    if (m == 1) return 0;
    while (a > 1) {
        q = a / m;
        t = m;
        m = a % m;
        a = t;
        t = x0;
        x0 = x1 - q * x0;
        x1 = t;
    }
    if (x1 < 0) x1 += m0;
    return x1;
}

/* 1. Обчислення квадратичної суми Гаусса g(1, p) = sum_{n=0}^{p-1} exp(2*pi*i*n^2 / p) */
double complex compute_quadratic_gauss_sum(long long p) {
    double complex sum = 0.0 + 0.0 * I;
    double angle_step = 2.0 * M_PI / (double)p;
    
    for (long long n = 0; n < p; n++) {
        long long n_sq_mod = (n * n) % p;
        double angle = angle_step * (double)n_sq_mod;
        sum += cos(angle) + I * sin(angle);
    }
    
    return sum;
}

/* 2. Обчислення суми Гаусса через символ Лежандра */
double complex compute_legendre_gauss_sum(long long p) {
    double complex sum = 0.0 + 0.0 * I;
    double angle_step = 2.0 * M_PI / (double)p;
    
    for (long long a = 1; a < p; a++) {
        int chi = legendre_symbol(a, p);
        double angle = angle_step * (double)a;
        sum += (double)chi * (cos(angle) + I * sin(angle));
    }
    
    return sum;
}

/* 3. Обчислення суми Клоостермана K(a, b; p) */
double complex compute_kloosterman_sum(long long a, long long b, long long p) {
    double complex sum = 0.0 + 0.0 * I;
    double angle_step = 2.0 * M_PI / (double)p;
    
    for (long long x = 1; x < p; x++) {
        long long x_inv = mod_inverse(x, p);
        long long arg = (a * x + b * x_inv) % p;
        double angle = angle_step * (double)arg;
        sum += cos(angle) + I * sin(angle);
    }
    
    return sum;
}

int main(void) {
    long long primes[] = {3, 5, 7, 11, 13, 17, 19, 23, 29, 31};
    size_t num_primes = sizeof(primes) / sizeof(primes[0]);
    
    printf("=== Перевірка квадратичних сум Гаусса g(1, p) (Мова C) ===\n");
    printf("%-5s | %-6s | %-20s | %-12s | %-12s\n", "p", "p mod4", "g(1, p)", "|g(1, p)|", "Теор. sqrt(p)");
    printf("----------------------------------------------------------------------\n");
    
    for (size_t i = 0; i < num_primes; i++) {
        long long p = primes[i];
        double complex g = compute_quadratic_gauss_sum(p);
        double mod_g = cabs(g);
        double expected_mod = sqrt((double)p);
        
        printf("%-5lld | %-6lld | %8.4f + %8.4fi | %-12.6f | %-12.6f\n",
               p, p % 4, creal(g), cimag(g), mod_g, expected_mod);
    }
    
    printf("\n=== Перевірка сум Клоостермана K(1, 1; p) та межі Вейля 2*sqrt(p) ===\n");
    printf("%-5s | %-20s | %-12s | %-12s\n", "p", "K(1, 1; p)", "|K(1, 1; p)|", "Межа 2*sqrt(p)");
    printf("----------------------------------------------------------------------\n");
    
    for (size_t i = 0; i < num_primes; i++) {
        long long p = primes[i];
        double complex k_sum = compute_kloosterman_sum(1, 1, p);
        double mod_k = cabs(k_sum);
        double weil_bound = 2.0 * sqrt((double)p);
        
        printf("%-5lld | %8.4f + %8.4fi | %-12.6f | %-12.6f\n",
               p, creal(k_sum), cimag(k_sum), mod_k, weil_bound);
    }
    
    return 0;
}
