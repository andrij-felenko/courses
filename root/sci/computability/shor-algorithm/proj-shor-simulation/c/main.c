#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <complex.h>

#define M_PI_VAL 3.14159265358979323846

// Швидке модульне піднесення до степеня (a^exp mod n)
uint64_t mod_exp(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) res = ((unsigned __int128)res * base) % mod;
        base = ((unsigned __int128)base * base) % mod;
        exp >>= 1;
    }
    return res;
}

// Обчислення найбільшого спільного дільника (алгоритм Евкліда)
uint64_t gcd_u64(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

// Обернене QFT над вектором амплітуд
void apply_inverse_qft_c(double complex *state, size_t q) {
    double complex *out = (double complex *)malloc(q * sizeof(double complex));
    if (!out) return;

    double inv_sqrt_q = 1.0 / sqrt((double)q);
    double two_pi = 2.0 * M_PI_VAL;

    for (size_t y = 0; y < q; ++y) {
        double complex sum = 0.0 + 0.0 * I;
        for (size_t x = 0; x < q; ++x) {
            double angle = -two_pi * ((double)(x * y)) / ((double)q);
            sum += state[x] * (cos(angle) + sin(angle) * I);
        }
        out[y] = sum * inv_sqrt_q;
    }

    for (size_t i = 0; i < q; ++i) {
        state[i] = out[i];
    }
    free(out);
}

// Знаходження періоду методом неперервних дробів
uint64_t extract_period_c(uint64_t y, uint64_t q, uint64_t a, uint64_t n) {
    uint64_t a_num = y, a_den = q;
    int64_t p_prev2 = 0, p_prev1 = 1;
    int64_t q_prev2 = 1, q_prev1 = 0;

    while (a_den != 0) {
        uint64_t quot = a_num / a_den;
        uint64_t rem = a_num % a_den;

        int64_t q_curr = quot * q_prev1 + q_prev2;
        int64_t p_curr = quot * p_prev1 + p_prev2;

        if (q_curr >= (int64_t)n) break;
        if (q_curr > 1) {
            uint64_t cand_r = (uint64_t)q_curr;
            if (mod_exp(a, cand_r, n) == 1) {
                return cand_r;
            }
        }

        p_prev2 = p_prev1;
        p_prev1 = p_curr;
        q_prev2 = q_prev1;
        q_prev1 = q_curr;

        a_num = a_den;
        a_den = rem;
    }
    return 0;
}

// Емуляція квантового пошуку періоду
uint64_t quantum_find_period_c(uint64_t a, uint64_t n) {
    size_t m = 1;
    while ((1ULL << m) < n * n) ++m;
    size_t q = 1ULL << m;

    double complex *state = (double complex *)calloc(q, sizeof(double complex));
    if (!state) return 0;

    size_t x0 = rand() % n;
    uint64_t target_val = mod_exp(a, x0, n);

    size_t count = 0;
    for (size_t x = 0; x < q; ++x) {
        if (mod_exp(a, x, n) == target_val) {
            state[x] = 1.0 + 0.0 * I;
            ++count;
        }
    }
    if (count == 0) {
        free(state);
        return 0;
    }

    double norm = 1.0 / sqrt((double)count);
    for (size_t x = 0; x < q; ++x) {
        state[x] *= norm;
    }

    apply_inverse_qft_c(state, q);

    // Семплінг вимірювання
    double r_val = (double)rand() / (double)RAND_MAX;
    double cum_prob = 0.0;
    size_t measured_y = 0;

    for (size_t y = 0; y < q; ++y) {
        double p = cabs(state[y]) * cabs(state[y]);
        cum_prob += p;
        if (r_val <= cum_prob) {
            measured_y = y;
            break;
        }
    }

    free(state);
    if (measured_y == 0) return 0;

    return extract_period_c(measured_y, q, a, n);
}

int main(void) {
    uint64_t n = 15;
    uint64_t p = 0, q_fact = 0;

    for (int attempt = 0; attempt < 50; ++attempt) {
        uint64_t a = 2 + (rand() % (n - 3));
        uint64_t g = gcd_u64(a, n);
        if (g > 1) {
            p = g;
            q_fact = n / g;
            break;
        }

        uint64_t r = quantum_find_period_c(a, n);
        if (r > 0 && r % 2 == 0) {
            uint64_t half_pow = mod_exp(a, r / 2, n);
            if (half_pow != n - 1) {
                uint64_t f1 = gcd_u64(half_pow - 1, n);
                uint64_t f2 = gcd_u64(half_pow + 1, n);
                if (f1 > 1 && f1 < n) { p = f1; q_fact = n / f1; break; }
                if (f2 > 1 && f2 < n) { p = f2; q_fact = n / f2; break; }
            }
        }
    }

    printf("Факторизація N = %llu -> %llu * %llu\n", n, p, q_fact);
    return 0;
}
