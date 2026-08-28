#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define AES_POLY 0x11B  /* x^8 + x^4 + x^3 + x + 1 */
#define GF8_POLY 0x0B   /* x^3 + x + 1 */

/* Додавання та віднімання в GF(2^n) */
static inline uint8_t gf_add(uint8_t a, uint8_t b) {
    return a ^ b;
}

/* Множення на x у полі GF(2^8) з редукцією за модулем AES */
static inline uint8_t gf256_xtime(uint8_t a) {
    return (a << 1) ^ ((a & 0x80) ? 0x1B : 0x00);
}

/* Постійночасове множення двох елементів у GF(2^8) (Russian Peasant) */
uint8_t gf256_mul(uint8_t a, uint8_t b) {
    uint8_t res = 0;
    while (b > 0) {
        if (b & 1) {
            res ^= a;
        }
        a = gf256_xtime(a);
        b >>= 1;
    }
    return res;
}

/* Швидке піднесення до степеня в GF(2^8) */
uint8_t gf256_pow(uint8_t base, uint8_t exp) {
    uint8_t res = 1;
    while (exp > 0) {
        if (exp & 1) {
            res = gf256_mul(res, base);
        }
        base = gf256_mul(base, base);
        exp >>= 1;
    }
    return res;
}

/* Мультиплікативне обернення через теорему Ферма: a^(-1) = a^254 */
uint8_t gf256_inv(uint8_t a) {
    if (a == 0) return 0; /* За угодою AES 0^(-1) = 0 */
    return gf256_pow(a, 254);
}

/* Афінне перетворення байта для побудови AES S-Box */
uint8_t aes_sbox_transform(uint8_t b) {
    uint8_t s = b;
    s ^= (b << 1) | (b >> 7);
    s ^= (b << 2) | (b >> 6);
    s ^= (b << 3) | (b >> 5);
    s ^= (b << 4) | (b >> 4);
    return s ^ 0x63;
}

/* Генерація вихідного байта AES S-Box */
uint8_t aes_sbox(uint8_t input) {
    uint8_t inv = gf256_inv(input);
    return aes_sbox_transform(inv);
}

/* Множення в GF(2^3) за модулем x^3 + x + 1 */
uint8_t gf8_mul(uint8_t a, uint8_t b) {
    uint8_t res = 0;
    for (int i = 0; i < 3; i++) {
        if (b & (1 << i)) {
            res ^= (a << i);
        }
    }
    /* Редукція за модулем x^3 + x + 1 (0x0B) */
    for (int i = 4; i >= 3; i--) {
        if (res & (1 << i)) {
            res ^= (GF8_POLY << (i - 3));
        }
    }
    return res & 0x07;
}

int main(void) {
    /* Перевірка GF(2^3): множення (x^2 + 1) * (x + 1) -> 5 * 3 */
    uint8_t a8 = 5; /* x^2 + 1 (101_2) */
    uint8_t b8 = 3; /* x + 1   (011_2) */
    uint8_t c8 = gf8_mul(a8, b8);
    printf("GF(2^3): %u * %u = %u (очікується 4 [x^2])\n", a8, b8, c8);

    /* Перевірка GF(2^8) AES: множення 0x57 * 0x83 */
    uint8_t a256 = 0x57;
    uint8_t b256 = 0x83;
    uint8_t c256 = gf256_mul(a256, b256);
    printf("GF(2^8): 0x%02X * 0x%02X = 0x%02X (очікується 0xC1)\n", a256, b256, c256);

    /* Перевірка обернення в AES */
    uint8_t inv = gf256_inv(a256);
    uint8_t one = gf256_mul(a256, inv);
    printf("GF(2^8): inv(0x%02X) = 0x%02X, перевірка a*a^(-1) = 0x%02X\n", a256, inv, one);

    /* Перевірка генерації S-Box для AES: S(0x53) = 0xED, S(0x00) = 0x63 */
    printf("AES S-Box: S(0x00) = 0x%02X (очікується 0x63)\n", aes_sbox(0x00));
    printf("AES S-Box: S(0x53) = 0x%02X (очікується 0xED)\n", aes_sbox(0x53));

    return 0;
}
