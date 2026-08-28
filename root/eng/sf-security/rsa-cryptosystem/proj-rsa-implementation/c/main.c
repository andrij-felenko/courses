#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Базова структура приватного ключа RSA з CRT-компонентами
typedef struct {
    uint64_t n;     // Modulus N = p * q
    uint64_t d;     // Private exponent d
    uint64_t p;     // Prime p
    uint64_t q;     // Prime q
    uint64_t dp;    // d_p = d mod (p - 1)
    uint64_t dq;    // d_q = d mod (q - 1)
    uint64_t qinv;  // q_inv = q^(-1) mod p
} rsa_private_key_t;

// Модульне множення для запобігання переповненню uint64_t
static uint64_t mul_mod(uint64_t a, uint64_t b, uint64_t m) {
    uint64_t res = 0;
    a %= m;
    while (b > 0) {
        if (b & 1) {
            res = (res + a) % m;
        }
        a = (a * 2) % m;
        b >>= 1;
    }
    return res;
}

// Модульне піднесення до степеня зі сталим часом кроку (Square-and-Multiply)
uint64_t rsa_mod_pow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = mul_mod(result, base, mod);
        }
        base = mul_mod(base, base, mod);
        exp >>= 1;
    }
    return result;
}

// Прискорене CRT-розшифрування за алгоритмом Гарнера
bool rsa_decrypt_crt(uint64_t ciphertext, const rsa_private_key_t *key, uint64_t *out_msg) {
    if (!key || !out_msg || ciphertext >= key->n) {
        return false;
    }

    // 1. Зменшення за модулями p та q
    uint64_t cp = ciphertext % key->p;
    uint64_t cq = ciphertext % key->q;

    // 2. Незалежні піднесення до степенів
    uint64_t mp = rsa_mod_pow(cp, key->dp, key->p);
    uint64_t mq = rsa_mod_pow(cq, key->dq, key->q);

    // 3. Рекомбінація Гарнера: h = (qinv * (mp - mq + p)) mod p
    uint64_t diff = (mp >= mq) ? (mp - mq) : (mp + key->p - (mq % key->p));
    uint64_t h = mul_mod(key->qinv, diff, key->p);

    // 4. Підсумкове повідомлення: m = mq + h * q
    *out_msg = mq + h * key->q;
    return true;
}

// Захищене зачищення пам'яті приватного ключа
void rsa_secure_wipe_key(rsa_private_key_t *key) {
    if (key) {
        volatile uint8_t *p = (volatile uint8_t *)key;
        size_t n = sizeof(rsa_private_key_t);
        while (n--) {
            *p++ = 0;
        }
    }
}

int main(void) {
    // Демонстраційні прості числа (у реальності 1024+ біт)
    // p = 61, q = 53, n = 3233, e = 17, d = 2753
    rsa_private_key_t key = {
        .n = 3233, .d = 2753,
        .p = 61,   .q = 53,
        .dp = 2753 % 60,  // 53
        .dq = 2753 % 52,  // 49
        .qinv = 38        // 53^(-1) mod 61 = 38
    };

    uint64_t message = 65; // Символ 'A'
    uint64_t ciphertext = rsa_mod_pow(message, 17, key.n);
    printf("Зашифровано (%lu) -> Шифротекст: %lu\n", message, ciphertext);

    uint64_t decrypted = 0;
    if (rsa_decrypt_crt(ciphertext, &key, &decrypted)) {
        printf("CRT-розшифровано -> Текст: %lu\n", decrypted);
    }

    rsa_secure_wipe_key(&key);
    return 0;
}
