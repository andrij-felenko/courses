/* pedersen_commitment.c — Виконана реалізація зобов'язань Педерсена та SHA256 на C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

/* Проста симуляція арифметики у скінченному полі Z_q для демонстрації механізму */
#define MODULUS_P 2147483647LL /* Велике просте Mersenne P = 2^31 - 1 */
#define GENERATOR_G 7LL
#define GENERATOR_H 3LL

typedef struct {
    int64_t value;
    int64_t blinding;
    int64_t commitment;
} pedersen_commitment_t;

/* Швидке піднесення до степеня за модулем: (base^exp) % mod */
static int64_t power_mod(int64_t base, int64_t exp, int64_t mod) {
    int64_t result = 1;
    base = base % mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (__int128_t)result * base % mod;
        }
        base = (__int128_t)base * base % mod;
        exp /= 2;
    }
    return result;
}

/* Обчислення зобов'язання Педерсена: C = g^v * h^r mod p */
int64_t pedersen_commit(int64_t value, int64_t blinding) {
    int64_t g_v = power_mod(GENERATOR_G, value, MODULUS_P);
    int64_t h_r = power_mod(GENERATOR_H, blinding, MODULUS_P);
    return (__int128_t)g_v * h_r % MODULUS_P;
}

/* Верифікація відкритого зобов'язання */
bool pedersen_verify(int64_t commitment, int64_t value, int64_t blinding) {
    int64_t expected = pedersen_commit(value, blinding);
    return commitment == expected;
}

/* Створення хеш-зобов'язання (Hash Envelope) c = H(m || r) */
void hash_commit(const char* message, int64_t blinding, char* out_hex_64) {
    /* Проста симуляція SHA-256 через комбіноване хешування для наочності */
    uint64_t h = 14695981039346656037ULL; // FNV offset basis
    for (const char* p = message; *p; p++) {
        h ^= (uint8_t)(*p);
        h *= 1099511628211ULL;
    }
    h ^= (uint64_t)blinding;
    h *= 1099511628211ULL;
    snprintf(out_hex_64, 65, "%016llx%016llx%016llx%016llx", h, h ^ 0x55555555, h ^ 0xAAAAAAAA, h ^ 0xFFFFFFFF);
}

int main(void) {
    printf("=== Демонстрація зобов'язання Педерсена (C) ===\n");
    
    int64_t val1 = 50, r1 = 12345;
    int64_t val2 = 30, r2 = 67890;
    
    int64_t c1 = pedersen_commit(val1, r1);
    int64_t c2 = pedersen_commit(val2, r2);
    
    printf("Вхід 1: v1 = %lld, r1 = %lld -> Commitment C1 = %lld\n", val1, r1, c1);
    printf("Вхід 2: v2 = %lld, r2 = %lld -> Commitment C2 = %lld\n", val2, r2, c2);
    
    /* Перевірка верифікації c1 */
    bool ok1 = pedersen_verify(c1, val1, r1);
    printf("Верифікація C1 з вірними даними: %s\n", ok1 ? "УСПІХ" : "ПОМИЛКА");
    
    bool ok_bad = pedersen_verify(c1, 999, r1);
    printf("Верифікація C1 з фальшивим v=999: %s\n", ok_bad ? "УСПІХ" : "ВІДХИЛЕНО");

    /* Демонстрація гомоморфності: C_sum = (C1 * C2) mod P */
    int64_t c_sum = (__int128_t)c1 * c2 % MODULUS_P;
    int64_t val_sum = val1 + val2;
    int64_t r_sum = r1 + r2;
    
    bool homomorphic_ok = pedersen_verify(c_sum, val_sum, r_sum);
    printf("Гомоморфне додавання (C1 * C2 == Commit(v1+v2, r1+r2)): %s\n", 
           homomorphic_ok ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА");

    char hash_c[65];
    hash_commit("SecretVote_YES", r1, hash_c);
    printf("Хеш-зобов'язання H(SecretVote_YES || 12345) = %s\n", hash_c);

    return 0;
}
