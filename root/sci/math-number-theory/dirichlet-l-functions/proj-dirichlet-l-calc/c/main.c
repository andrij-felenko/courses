#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI 3.14159265358979323846

/* Обчислення найбільшого спільного дільника */
long long gcd(long long a, long long b) {
    while (b != 0) {
        long long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/* Знаходження первісного кореня g за модулем простого p */
int find_primitive_root(int p) {
    if (p == 2) return 1;
    int phi = p - 1;
    int fact[32];
    int fact_count = 0;
    int n = phi;
    
    for (int i = 2; i * i <= n; ++i) {
        if (n % i == 0) {
            fact[fact_count++] = i;
            while (n % i == 0) n /= i;
        }
    }
    if (n > 1) fact[fact_count++] = n;

    for (int res = 2; res < p; ++res) {
        int ok = 1;
        for (int i = 0; i < fact_count && ok; ++i) {
            long long val = 1;
            long long base = res;
            int exp = phi / fact[i];
            while (exp > 0) {
                if (exp % 2 == 1) val = (val * base) % p;
                base = (base * base) % p;
                exp /= 2;
            }
            if (val == 1) ok = 0;
        }
        if (ok) return res;
    }
    return -1;
}

/* Обчислення часткової суми L(s, character_m) */
double complex compute_dirichlet_l(int p, int char_m, int g, double complex s, int N) {
    /* Таблиця дискретних логарифмів ind_g(a) */
    int *ind = (int*)malloc(p * sizeof(int));
    for (int i = 0; i < p; ++i) ind[i] = -1;
    
    long long cur = 1;
    for (int k = 0; k < p - 1; ++k) {
        ind[cur] = k;
        cur = (cur * g) % p;
    }

    double complex l_val = 0.0 + 0.0 * I;
    
    for (int n = 1; n <= N; ++n) {
        int rem = n % p;
        if (rem == 0 || gcd(rem, p) > 1) continue;
        
        int k = ind[rem];
        double angle = 2.0 * PI * char_m * k / (p - 1);
        double complex chi_val = cos(angle) + I * sin(angle);
        
        /* n^(-s) = exp(-s * ln(n)) */
        double complex n_s = cexp(-s * clog(n));
        l_val += chi_val * n_s;
    }

    free(ind);
    return l_val;
}

int main(void) {
    int p = 5;
    int g = find_primitive_root(p);
    printf("Модуль p = %d, Первісний корінь g = %d\n\n", p, g);

    double complex s_point = 1.0 + 0.0 * I; /* Оцінка L(1, chi) */
    int N_terms = 100000;

    for (int m = 0; m < p - 1; ++m) {
        double complex l_res = compute_dirichlet_l(p, m, g, s_point, N_terms);
        printf("Характер chi_%d (m=%d): L(1, chi) = %.6f + %.6fi (модуль = %.6f)\n",
               m, m, creal(l_res), cimag(l_res), cabs(l_res));
    }

    return 0;
}
