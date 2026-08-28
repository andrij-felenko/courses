#include <stdint.h>
#include <string.h>
#include <stdbool.h>

/* Початковий вектор (IV) за RFC 3394: 0xA6A6A6A6A6A6A6A6 */
static const uint8_t DEFAULT_IV[8] = { 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6 };

/* Зовнішня функція одиночного перетворення AES-128 (16 байтів in -> 16 байтів out) */
extern void aes128_encrypt_block(const uint8_t key[16], const uint8_t in[16], uint8_t out[16]);

/**
 * Загортання ключа контенту (AES Key Wrap, RFC 3394).
 * n: кількість 64-бітних блоків відкритого ключа (для AES-128 n = 2).
 * in_key: вхідний ключ довжиною n * 8 байтів (16 байтів).
 * out_wrapped: вихідний загорнутий блок довжиною (n + 1) * 8 байтів (24 байти).
 */
bool aes_key_wrap_128(const uint8_t kek[16], const uint8_t *in_key, size_t n, uint8_t *out_wrapped) {
    if (!kek || !in_key || !out_wrapped || n == 0) {
        return false;
    }

    uint8_t a[8];
    memcpy(a, DEFAULT_IV, 8);

    /* Масив блоків R[1]..R[n] */
    uint8_t r[n][8];
    for (size_t i = 0; i < n; ++i) {
        memcpy(r[i], in_key + (i * 8), 8);
    }

    /* 6 раундів змішування */
    for (uint32_t j = 0; j <= 5; ++j) {
        for (size_t i = 1; i <= n; ++i) {
            uint8_t b_in[16];
            uint8_t b_out[16];

            /* B = AES(K, A | R[i]) */
            memcpy(b_in, a, 8);
            memcpy(b_in + 8, r[i - 1], 8);

            aes128_encrypt_block(kek, b_in, b_out);

            /* A = MSB(64, B) ^ t */
            uint64_t t = (uint64_t)(n * j + i);
            memcpy(a, b_out, 8);
            for (int k = 0; k < 8; ++k) {
                a[7 - k] ^= (uint8_t)((t >> (k * 8)) & 0xFF);
            }

            /* R[i] = LSB(64, B) */
            memcpy(r[i - 1], b_out + 8, 8);
        }
    }

    /* Формування результату C = A | R[1] | ... | R[n] */
    memcpy(out_wrapped, a, 8);
    for (size_t i = 0; i < n; ++i) {
        memcpy(out_wrapped + 8 + (i * 8), r[i], 8);
    }

    return true;
}
