#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* Прості параметри для демонстрації арифметики у групі Z_p */
#define GROUP_P 23  /* Простий модуль групи */
#define GROUP_Q 11  /* Порядок підгрупи (q = (p - 1) / 2) */
#define GROUP_G 4   /* Генератор підгрупи порядку q */

typedef struct {
    uint8_t alpha; /* Комітмент α = g^r mod p */
    uint8_t gamma; /* Відповідь γ = (r + β * x) mod q */
} schnorr_signature_t;

/* Проста хеш-функція H(m || alpha) mod q для навчальної реалізації */
static uint8_t crypto_hash_challenge(const uint8_t *msg, size_t len, uint8_t alpha) {
    uint32_t hash_val = 5381;
    for (size_t i = 0; i < len; ++i) {
        hash_val = ((hash_val << 5) + hash_val) ^ msg[i];
    }
    hash_val = ((hash_val << 5) + hash_val) ^ alpha;
    return (uint8_t)(hash_val % GROUP_Q);
}

/* Швидке піднесення до степеня за модулем */
static uint8_t mod_pow(uint32_t base, uint32_t exp, uint32_t mod) {
    uint32_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }
    return (uint8_t)result;
}

/* Генерація ключової пари: sk = x ∈ Z_q, pk = y = g^x mod p */
bool schnorr_key_gen(uint8_t *sk, uint8_t *pk) {
    if (!sk || !pk) return false;
    *sk = 7; /* Приклад секретного ключа (x < q) */
    *pk = mod_pow(GROUP_G, *sk, GROUP_P);
    return true;
}

/* Створення підпису Фіата — Шаміра: σ = (α, γ) */
bool schnorr_sign(const uint8_t *msg, size_t msg_len, uint8_t sk, schnorr_signature_t *sig) {
    if (!msg || !sig) return false;

    /* 1. Випадковий одноразовий елемент r ∈ Z_q */
    uint8_t r = 5; /* Випадкова величина r (у продакшн — CSPRNG) */

    /* 2. Обчислення зобов'язання (Commitment) α = g^r mod p */
    sig->alpha = mod_pow(GROUP_G, r, GROUP_P);

    /* 3. Евристика Фіата — Шаміра: β = H(m || α) mod q */
    uint8_t beta = crypto_hash_challenge(msg, msg_len, sig->alpha);

    /* 4. Обчислення відповіді (Response) γ = (r + β * sk) mod q */
    sig->gamma = (r + beta * sk) % GROUP_Q;

    return true;
}

/* Перевірка підпису Фіата — Шаміра: g^γ =?= α * y^β mod p */
bool schnorr_verify(const uint8_t *msg, size_t msg_len, uint8_t pk, const schnorr_signature_t *sig) {
    if (!msg || !sig) return false;

    /* 1. Реконструкція виклику: β' = H(m || α) mod q */
    uint8_t beta_prime = crypto_hash_challenge(msg, msg_len, sig->alpha);

    /* 2. Обчислення LHS = g^γ mod p */
    uint8_t lhs = mod_pow(GROUP_G, sig->gamma, GROUP_P);

    /* 3. Обчислення RHS = (α * y^β') mod p */
    uint8_t y_to_beta = mod_pow(pk, beta_prime, GROUP_P);
    uint8_t rhs = (sig->alpha * y_to_beta) % GROUP_P;

    return (lhs == rhs);
}

int main(void) {
    uint8_t sk = 0, pk = 0;
    schnorr_key_gen(&sk, &pk);

    const uint8_t message[] = "Fiat-Shamir Transformation";
    size_t msg_len = sizeof(message) - 1;

    schnorr_signature_t sig;
    if (!schnorr_sign(message, msg_len, sk, &sig)) {
        fprintf(stderr, "Помилка створення підпису\n");
        return EXIT_FAILURE;
    }

    printf("Сформовано підпис Фіата — Шаміра:\n");
    printf("  Комітмент α = %u\n", sig.alpha);
    printf("  Відповідь  γ = %u\n", sig.gamma);

    bool is_valid = schnorr_verify(message, msg_len, pk, &sig);
    printf("Результат перевірки підпису: %s\n", is_valid ? "УСПІХ (Дійсний)" : "ПОМИЛКА (Недійсний)");

    return is_valid ? EXIT_SUCCESS : EXIT_FAILURE;
}
