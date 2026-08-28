#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Обчислення найбільшого спільного дільника (алгоритм Евкліда) */
uint64_t gcd_u64(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

/* Швидке модульне піднесення до степеня: (base^exp) mod mod */
uint64_t mod_pow_u64(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = (uint64_t)((__int128)result * base % mod);
        }
        base = (uint64_t)((__int128)base * base % mod);
        exp >>= 1;
    }
    return result;
}

/* Відновлення періоду r та факторизація N за виміряною фазою y/Q */
bool shor_classical_postprocess(uint64_t N, uint64_t a, uint64_t y, uint64_t Q,
                                uint64_t *out_p, uint64_t *out_q) {
    if (y == 0) return false;

    uint64_t num = y;
    uint64_t den = Q;

    uint64_t p_prev2 = 0, p_prev1 = 1, p_curr = 0;
    uint64_t q_prev2 = 1, q_prev1 = 0, q_curr = 0;

    /* Покроковий розклад у неперервний дріб */
    while (den != 0) {
        uint64_t a_k = num / den;
        uint64_t rem = num % den;

        p_curr = a_k * p_prev1 + p_prev2;
        q_curr = a_k * q_prev1 + q_prev2;

        /* Оновлення чисельників та знаменників */
        p_prev2 = p_prev1; p_prev1 = p_curr;
        q_prev2 = q_prev1; q_prev1 = q_curr;

        num = den;
        den = rem;

        if (q_curr >= N) break;

        /* Тестуємо отриманий знаменник q_curr як період r */
        uint64_t r_candidate = q_curr;
        if (mod_pow_u64(a, r_candidate, N) == 1) {
            /* Період знайдено! Перевіряємо парність */
            if (r_candidate % 2 == 0) {
                uint64_t half_pow = mod_pow_u64(a, r_candidate / 2, N);
                if (half_pow != N - 1 && half_pow != 1) {
                    uint64_t factor1 = gcd_u64(half_pow - 1, N);
                    uint64_t factor2 = gcd_u64(half_pow + 1, N);

                    if (factor1 > 1 && factor1 < N) {
                        *out_p = factor1;
                        *out_q = N / factor1;
                        return true;
                    }
                    if (factor2 > 1 && factor2 < N) {
                        *out_p = factor2;
                        *out_q = N / factor2;
                        return true;
                    }
                }
            }
        }
    }
    return false;
}

int main(void) {
    uint64_t N = 15;
    uint64_t a = 7;
    uint64_t y = 192;
    uint64_t Q = 256;

    uint64_t p = 0, q = 0;
    if (shor_classical_postprocess(N, a, y, Q, &p, &q)) {
        printf("Успіх: %llu = %llu * %llu\n", (unsigned long long)N,
               (unsigned long long)p, (unsigned long long)q);
    } else {
        printf("Не вдалося розкласти модуль на множники.\n");
    }
    return 0;
}
