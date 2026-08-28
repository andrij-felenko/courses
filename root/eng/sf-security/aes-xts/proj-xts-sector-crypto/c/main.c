#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

#define AES_BLOCK_SIZE 16

/* Мінімальний симетричний інтерфейс блокового шифру AES-128 / AES-256 */
typedef struct {
    uint32_t round_keys_enc[60];
    uint32_t round_keys_dec[60];
    int rounds;
} aes_ctx_t;

/* Прототипи базових блокових перетворень AES (апаратні AES-NI або софтверні) */
void aes_init(aes_ctx_t *ctx, const uint8_t *key, size_t key_len);
void aes_encrypt_block(const aes_ctx_t *ctx, const uint8_t in[16], uint8_t out[16]);
void aes_decrypt_block(const aes_ctx_t *ctx, const uint8_t in[16], uint8_t out[16]);

/* Контекст XTS з двома незалежними ключами */
typedef struct {
    aes_ctx_t ctx_data;   /* Key1: шифрування даних */
    aes_ctx_t ctx_tweak;  /* Key2: шифрування твіка */
} xts_ctx_t;

/* Множення 128-бітного твіка на alpha в GF(2^128) за стандартом IEEE 1619 (константний час) */
static void xts_gf128_mul_alpha(uint8_t t[16]) {
    uint8_t carry = 0;
    for (int i = 0; i < 16; ++i) {
        uint8_t next_carry = t[i] >> 7;
        t[i] = (uint8_t)((t[i] << 1) | carry);
        carry = next_carry;
    }
    /* Якщо старший біт t[15] дорівнював 1, робимо XOR із поліномом 0x87 у байті 0 */
    uint8_t mask = (uint8_t)(-(int8_t)carry) & 0x87;
    t[0] ^= mask;
}

/* Ініціалізація XTS контексту (key_len = 32 байти для AES-128-XTS або 64 байти для AES-256-XTS) */
bool xts_init(xts_ctx_t *ctx, const uint8_t *key, size_t key_len) {
    if (!ctx || !key || (key_len != 32 && key_len != 64)) {
        return false;
    }
    size_t single_key_len = key_len / 2;
    /* Перевірка вимоги нерівності ключів Key1 != Key2 */
    if (memcmp(key, key + single_key_len, single_key_len) == 0) {
        return false;
    }
    aes_init(&ctx->ctx_data, key, single_key_len);
    aes_init(&ctx->ctx_tweak, key + single_key_len, single_key_len);
    return true;
}

/* Шифрування сектора в режимі XTS-AES з підтримкою Ciphertext Stealing */
bool xts_encrypt_sector(const xts_ctx_t *ctx, const uint8_t tweak_in[16],
                        const uint8_t *plaintext, size_t len, uint8_t *ciphertext) {
    if (!ctx || !tweak_in || !plaintext || !ciphertext || len < AES_BLOCK_SIZE) {
        return false;
    }

    uint8_t t[AES_BLOCK_SIZE];
    uint8_t pp[AES_BLOCK_SIZE];
    uint8_t cc[AES_BLOCK_SIZE];

    /* 1. Обчислення базового твіка: T0 = AES_Enc(Key2, tweak_in) */
    aes_encrypt_block(&ctx->ctx_tweak, tweak_in, t);

    size_t full_blocks = len / AES_BLOCK_SIZE;
    size_t remainder = len % AES_BLOCK_SIZE;
    size_t lim = (remainder == 0) ? full_blocks : (full_blocks - 1);

    /* 2. Шифрування повних блоків */
    for (size_t i = 0; i < lim; ++i) {
        const uint8_t *p_blk = plaintext + i * AES_BLOCK_SIZE;
        uint8_t *c_blk = ciphertext + i * AES_BLOCK_SIZE;

        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            pp[k] = p_blk[k] ^ t[k];
        }
        aes_encrypt_block(&ctx->ctx_data, pp, cc);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            c_blk[k] = cc[k] ^ t[k];
        }

        xts_gf128_mul_alpha(t);
    }

    /* 3. Обробка залишку через Ciphertext Stealing (CTS) */
    if (remainder > 0) {
        size_t m = full_blocks;
        const uint8_t *p_m_minus_1 = plaintext + (m - 1) * AES_BLOCK_SIZE;
        const uint8_t *p_m = plaintext + m * AES_BLOCK_SIZE;
        uint8_t *c_m_minus_1 = ciphertext + (m - 1) * AES_BLOCK_SIZE;
        uint8_t *c_m = ciphertext + m * AES_BLOCK_SIZE;

        /* Шифруємо передостанній блок P[m-1] з поточним твіком T[m-1] */
        uint8_t c_prime[AES_BLOCK_SIZE];
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            pp[k] = p_m_minus_1[k] ^ t[k];
        }
        aes_encrypt_block(&ctx->ctx_data, pp, cc);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            c_prime[k] = cc[k] ^ t[k];
        }

        /* Викрадення: перші remainder байтів C' йдуть у C[m] */
        memcpy(c_m, c_prime, remainder);

        /* Формуємо блок P'[m-1] = P[m] || залишок C' */
        uint8_t p_prime[AES_BLOCK_SIZE];
        memcpy(p_prime, p_m, remainder);
        memcpy(p_prime + remainder, c_prime + remainder, AES_BLOCK_SIZE - remainder);

        /* Наступний твік T[m] */
        xts_gf128_mul_alpha(t);

        /* Шифруємо P'[m-1] з твіком T[m] -> C[m-1] */
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            pp[k] = p_prime[k] ^ t[k];
        }
        aes_encrypt_block(&ctx->ctx_data, pp, cc);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            c_m_minus_1[k] = cc[k] ^ t[k];
        }
    }

    return true;
}

/* Дешифрування сектора в режимі XTS-AES */
bool xts_decrypt_sector(const xts_ctx_t *ctx, const uint8_t tweak_in[16],
                        const uint8_t *ciphertext, size_t len, uint8_t *plaintext) {
    if (!ctx || !tweak_in || !ciphertext || !plaintext || len < AES_BLOCK_SIZE) {
        return false;
    }

    uint8_t t[AES_BLOCK_SIZE];
    uint8_t cc[AES_BLOCK_SIZE];
    uint8_t pp[AES_BLOCK_SIZE];

    aes_encrypt_block(&ctx->ctx_tweak, tweak_in, t);

    size_t full_blocks = len / AES_BLOCK_SIZE;
    size_t remainder = len % AES_BLOCK_SIZE;
    size_t lim = (remainder == 0) ? full_blocks : (full_blocks - 1);

    for (size_t i = 0; i < lim; ++i) {
        const uint8_t *c_blk = ciphertext + i * AES_BLOCK_SIZE;
        uint8_t *p_blk = plaintext + i * AES_BLOCK_SIZE;

        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            cc[k] = c_blk[k] ^ t[k];
        }
        aes_decrypt_block(&ctx->ctx_data, cc, pp);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            p_blk[k] = pp[k] ^ t[k];
        }

        xts_gf128_mul_alpha(t);
    }

    if (remainder > 0) {
        size_t m = full_blocks;
        const uint8_t *c_m_minus_1 = ciphertext + (m - 1) * AES_BLOCK_SIZE;
        const uint8_t *c_m = ciphertext + m * AES_BLOCK_SIZE;
        uint8_t *p_m_minus_1 = plaintext + (m - 1) * AES_BLOCK_SIZE;
        uint8_t *p_m = plaintext + m * AES_BLOCK_SIZE;

        /* Зберігаємо T[m-1] та генеруємо T[m] */
        uint8_t t_m_minus_1[AES_BLOCK_SIZE];
        memcpy(t_m_minus_1, t, AES_BLOCK_SIZE);
        xts_gf128_mul_alpha(t);

        /* Дешифруємо C[m-1] з твіком T[m] -> P'[m-1] */
        uint8_t p_prime[AES_BLOCK_SIZE];
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            cc[k] = c_m_minus_1[k] ^ t[k];
        }
        aes_decrypt_block(&ctx->ctx_data, cc, pp);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            p_prime[k] = pp[k] ^ t[k];
        }

        /* Перші remainder байтів P' є відкритим хвостом P[m] */
        memcpy(p_m, p_prime, remainder);

        /* Відновлюємо C'[m-1] = C[m] || хвіст P'[m-1] */
        uint8_t c_prime[AES_BLOCK_SIZE];
        memcpy(c_prime, c_m, remainder);
        memcpy(c_prime + remainder, p_prime + remainder, AES_BLOCK_SIZE - remainder);

        /* Дешифруємо C'[m-1] з твіком T[m-1] -> P[m-1] */
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            cc[k] = c_prime[k] ^ t_m_minus_1[k];
        }
        aes_decrypt_block(&ctx->ctx_data, cc, pp);
        for (int k = 0; k < AES_BLOCK_SIZE; ++k) {
            p_m_minus_1[k] = pp[k] ^ t_m_minus_1[k];
        }
    }

    return true;
}
