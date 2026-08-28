#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define AES_BLOCK_SIZE 16

/* Зсув 128-бітного блоку вліво на 1 біт у порядку Big-Endian */
static void cmac_shift_left(const uint8_t *in, uint8_t *out) {
    uint8_t overflow = 0;
    for (int i = 15; i >= 0; --i) {
        out[i] = (uint8_t)((in[i] << 1) | overflow);
        overflow = (uint8_t)((in[i] & 0x80) ? 1 : 0);
    }
}

/* Генерація підключів K1 та K2 згідно з RFC 4493 */
static void cmac_generate_subkeys(const uint8_t *key, uint8_t *k1, uint8_t *k2,
                                  void (*aes128_encrypt)(const uint8_t*, const uint8_t*, uint8_t*)) {
    uint8_t zero[AES_BLOCK_SIZE] = {0};
    uint8_t l[AES_BLOCK_SIZE];
    aes128_encrypt(key, zero, l);

    /* Обчислення K1 = (L << 1) ^ (msb(L) ? 0x87 : 0) */
    cmac_shift_left(l, k1);
    if (l[0] & 0x80) {
        k1[15] ^= 0x87;
    }

    /* Обчислення K2 = (K1 << 1) ^ (msb(K1) ? 0x87 : 0) */
    cmac_shift_left(k1, k2);
    if (k1[0] & 0x80) {
        k2[15] ^= 0x87;
    }
}

/* Обчислення AES-CMAC для довільної довжини повідомлення */
void aes_cmac(const uint8_t *key, const uint8_t *msg, size_t len, uint8_t *mac,
              void (*aes128_encrypt)(const uint8_t*, const uint8_t*, uint8_t*)) {
    uint8_t k1[AES_BLOCK_SIZE], k2[AES_BLOCK_SIZE];
    cmac_generate_subkeys(key, k1, k2, aes128_encrypt);

    size_t n_blocks = (len + AES_BLOCK_SIZE - 1) / AES_BLOCK_SIZE;
    if (n_blocks == 0) {
        n_blocks = 1;
    }

    bool last_block_complete = (len > 0) && (len % AES_BLOCK_SIZE == 0);
    uint8_t x[AES_BLOCK_SIZE] = {0};
    uint8_t y[AES_BLOCK_SIZE];

    for (size_t i = 0; i < n_blocks - 1; ++i) {
        for (size_t b = 0; b < AES_BLOCK_SIZE; ++b) {
            y[b] = x[b] ^ msg[i * AES_BLOCK_SIZE + b];
        }
        aes128_encrypt(key, y, x);
    }

    /* Обробка останнього блоку з підключем K1 або K2 */
    uint8_t last_block[AES_BLOCK_SIZE] = {0};
    size_t last_len = len - (n_blocks - 1) * AES_BLOCK_SIZE;
    if (last_block_complete) {
        for (size_t b = 0; b < AES_BLOCK_SIZE; ++b) {
            last_block[b] = msg[(n_blocks - 1) * AES_BLOCK_SIZE + b] ^ k1[b];
        }
    } else {
        if (last_len > 0) {
            memcpy(last_block, msg + (n_blocks - 1) * AES_BLOCK_SIZE, last_len);
        }
        last_block[last_len] = 0x80; /* Доповнення 1000... */
        for (size_t b = 0; b < AES_BLOCK_SIZE; ++b) {
            last_block[b] ^= k2[b];
        }
    }

    for (size_t b = 0; b < AES_BLOCK_SIZE; ++b) {
        y[b] = x[b] ^ last_block[b];
    }
    aes128_encrypt(key, y, mac);
}

/* Функція зобов'язання f4 (Commitment):
   C_a = AES-CMAC_N_a(PKa_x || PKb_x || Z) */
void bt_smp_f4(const uint8_t *pka_x, const uint8_t *pkb_x, const uint8_t *nonce,
               uint8_t z_flag, uint8_t *confirm_out,
               void (*aes128_encrypt)(const uint8_t*, const uint8_t*, uint8_t*)) {
    uint8_t msg[65];
    memcpy(msg, pka_x, 32);
    memcpy(msg + 32, pkb_x, 32);
    msg[64] = z_flag;

    aes_cmac(nonce, msg, sizeof(msg), confirm_out, aes128_encrypt);
}

/* Розрахунок 6-значного коду Numeric Comparison g2:
   V = AES-CMAC_N_a(PKa_x || PKb_x || N_b)[0..3] mod 10^6 */
uint32_t bt_smp_g2(const uint8_t *pka_x, const uint8_t *pkb_x,
                   const uint8_t *na, const uint8_t *nb,
                   void (*aes128_encrypt)(const uint8_t*, const uint8_t*, uint8_t*)) {
    uint8_t msg[80];
    memcpy(msg, pka_x, 32);
    memcpy(msg + 32, pkb_x, 32);
    memcpy(msg + 64, nb, 16);

    uint8_t mac[16];
    aes_cmac(na, msg, sizeof(msg), mac, aes128_encrypt);

    /* Молодші 4 байти в форматі Little-Endian */
    uint32_t raw_val = ((uint32_t)mac[0]) |
                       (((uint32_t)mac[1]) << 8) |
                       (((uint32_t)mac[2]) << 16) |
                       (((uint32_t)mac[3]) << 24);

    return raw_val % 1000000U;
}

/* Захищене порівняння за сталий час проти атак через аналіз часу */
bool bt_smp_constant_time_eq16(const uint8_t *a, const uint8_t *b) {
    uint8_t diff = 0;
    for (size_t i = 0; i < 16; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}
