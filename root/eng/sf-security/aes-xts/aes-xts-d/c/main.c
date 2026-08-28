#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

#define AES_BLOCK_LEN 16

/* Інтерфейс блокового шифрування AES-128 / AES-256 */
typedef struct {
    uint32_t round_keys_enc[60];
    uint32_t round_keys_dec[60];
    int rounds;
} aes_core_t;

void aes_core_init(aes_core_t *ctx, const uint8_t *key, size_t key_bytes);
void aes_core_encrypt(const aes_core_t *ctx, const uint8_t in[16], uint8_t out[16]);
void aes_core_decrypt(const aes_core_t *ctx, const uint8_t in[16], uint8_t out[16]);

/* Структура контексту XTS-AES */
typedef struct {
    aes_core_t cipher_data;   /* Key1: шифрування відбілених блоків даних */
    aes_core_t cipher_tweak;  /* Key2: шифрування початкового твіка LBA */
} xts_context_t;

/* Множення на alpha в полі GF(2^128) за стандартом IEEE 1619 у константному часі */
static void xts_mul_alpha(uint8_t t[16]) {
    uint8_t carry = 0;
    for (int i = 0; i < 16; ++i) {
        uint8_t next_carry = t[i] >> 7;
        t[i] = (uint8_t)((t[i] << 1) | carry);
        carry = next_carry;
    }
    /* Маска константного часу: 0x87, якщо carry != 0, інакше 0x00 */
    uint8_t mask = (uint8_t)(-(int8_t)carry) & 0x87;
    t[0] ^= mask;
}

/* Ініціалізація ключів: 32 байти для AES-128-XTS, 64 байти для AES-256-XTS */
bool xts_setup(xts_context_t *ctx, const uint8_t *key, size_t total_key_len) {
    if (!ctx || !key || (total_key_len != 32 && total_key_len != 64)) {
        return false;
    }
    size_t k_len = total_key_len / 2;
    /* Захист від однакових ключів K1 == K2 */
    if (memcmp(key, key + k_len, k_len) == 0) {
        return false;
    }
    aes_core_init(&ctx->cipher_data, key, k_len);
    aes_core_init(&ctx->cipher_tweak, key + k_len, k_len);
    return true;
}

/* Шифрування сектора з автоматичною обробкою неповного залишку через CTS */
bool xts_encrypt(const xts_context_t *ctx, const uint8_t tweak_lba[16],
                 const uint8_t *src, size_t len, uint8_t *dst) {
    if (!ctx || !tweak_lba || !src || !dst || len < AES_BLOCK_LEN) {
        return false;
    }

    uint8_t t[AES_BLOCK_LEN], pp[AES_BLOCK_LEN], cc[AES_BLOCK_LEN];

    /* 1. Базовий твік T0 = AES(Key2, LBA) */
    aes_core_encrypt(&ctx->cipher_tweak, tweak_lba, t);

    size_t full_blocks = len / AES_BLOCK_LEN;
    size_t rem = len % AES_BLOCK_LEN;
    size_t lim = (rem == 0) ? full_blocks : (full_blocks - 1);

    /* 2. Основний цикл повних блоків */
    for (size_t i = 0; i < lim; ++i) {
        const uint8_t *p_blk = src + i * AES_BLOCK_LEN;
        uint8_t *c_blk = dst + i * AES_BLOCK_LEN;

        for (int k = 0; k < AES_BLOCK_LEN; ++k) pp[k] = p_blk[k] ^ t[k];
        aes_core_encrypt(&ctx->cipher_data, pp, cc);
        for (int k = 0; k < AES_BLOCK_LEN; ++k) c_blk[k] = cc[k] ^ t[k];

        xts_mul_alpha(t);
    }

    /* 3. Обробка CTS для залишку */
    if (rem > 0) {
        size_t m = full_blocks;
        const uint8_t *p_m_minus_1 = src + (m - 1) * AES_BLOCK_LEN;
        const uint8_t *p_m = src + m * AES_BLOCK_LEN;
        uint8_t *c_m_minus_1 = dst + (m - 1) * AES_BLOCK_LEN;
        uint8_t *c_m = dst + m * AES_BLOCK_LEN;

        uint8_t c_prime[AES_BLOCK_LEN];
        for (int k = 0; k < AES_BLOCK_LEN; ++k) pp[k] = p_m_minus_1[k] ^ t[k];
        aes_core_encrypt(&ctx->cipher_data, pp, cc);
        for (int k = 0; k < AES_BLOCK_LEN; ++k) c_prime[k] = cc[k] ^ t[k];

        memcpy(c_m, c_prime, rem);

        uint8_t p_prime[AES_BLOCK_LEN];
        memcpy(p_prime, p_m, rem);
        memcpy(p_prime + rem, c_prime + rem, AES_BLOCK_LEN - rem);

        xts_mul_alpha(t);

        for (int k = 0; k < AES_BLOCK_LEN; ++k) pp[k] = p_prime[k] ^ t[k];
        aes_core_encrypt(&ctx->cipher_data, pp, cc);
        for (int k = 0; k < AES_BLOCK_LEN; ++k) c_m_minus_1[k] = cc[k] ^ t[k];
    }

    return true;
}

/* Дешифрування сектора */
bool xts_decrypt(const xts_context_t *ctx, const uint8_t tweak_lba[16],
                 const uint8_t *src, size_t len, uint8_t *dst) {
    if (!ctx || !tweak_lba || !src || !dst || len < AES_BLOCK_LEN) {
        return false;
    }

    uint8_t t[AES_BLOCK_LEN], cc[AES_BLOCK_LEN], pp[AES_BLOCK_LEN];

    aes_core_encrypt(&ctx->cipher_tweak, tweak_lba, t);

    size_t full_blocks = len / AES_BLOCK_LEN;
    size_t rem = len % AES_BLOCK_LEN;
    size_t lim = (rem == 0) ? full_blocks : (full_blocks - 1);

    for (size_t i = 0; i < lim; ++i) {
        const uint8_t *c_blk = src + i * AES_BLOCK_LEN;
        uint8_t *p_blk = dst + i * AES_BLOCK_LEN;

        for (int k = 0; k < AES_BLOCK_LEN; ++k) cc[k] = c_blk[k] ^ t[k];
        aes_core_decrypt(&ctx->cipher_data, cc, pp);
        for (int k = 0; k < AES_BLOCK_LEN; ++k) p_blk[k] = pp[k] ^ t[k];

        xts_mul_alpha(t);
    }

    if (rem > 0) {
        size_t m = full_blocks;
        const uint8_t *c_m_minus_1 = src + (m - 1) * AES_BLOCK_LEN;
        const uint8_t *c_m = src + m * AES_BLOCK_LEN;
        uint8_t *p_m_minus_1 = dst + (m - 1) * AES_BLOCK_LEN;
        uint8_t *p_m = dst + m * AES_BLOCK_LEN;

        uint8_t t_m_minus_1[AES_BLOCK_LEN];
        memcpy(t_m_minus_1, t, AES_BLOCK_LEN);
        xts_mul_alpha(t);

        uint8_t p_prime[AES_BLOCK_LEN];
        for (int k = 0; k < AES_BLOCK_LEN; ++k) cc[k] = c_m_minus_1[k] ^ t[k];
        aes_core_decrypt(&ctx->cipher_data, cc, pp);
        for (int k = 0; k < AES_BLOCK_LEN; ++k) p_prime[k] = pp[k] ^ t[k];

        memcpy(p_m, p_prime, rem);

        uint8_t c_prime[AES_BLOCK_LEN];
        memcpy(c_prime, c_m, rem);
        memcpy(c_prime + rem, p_prime + rem, AES_BLOCK_LEN - rem);

        for (int k = 0; k < AES_BLOCK_LEN; ++k) cc[k] = c_prime[k] ^ t_m_minus_1[k];
        aes_core_decrypt(&ctx->cipher_data, cc, pp);
        for (int k = 0; k < AES_BLOCK_LEN; ++k) p_m_minus_1[k] = pp[k] ^ t_m_minus_1[k];
    }

    return true;
}
