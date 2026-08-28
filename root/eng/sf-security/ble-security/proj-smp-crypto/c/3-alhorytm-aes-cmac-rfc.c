#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

extern void aes128_ecb_encrypt(const uint8_t key[16], const uint8_t input[16], uint8_t output[16]);

/* Бітовий зсув 128-бітного блоку вліво на 1 біт з урахуванням константи поля Rb = 0x87 */
static void ble_cmac_shift_left(const uint8_t input[16], uint8_t output[16]) {
    uint8_t overflow = 0;
    for (int i = 15; i >= 0; --i) {
        uint8_t next_overflow = (input[i] & 0x80) ? 1 : 0;
        output[i] = (uint8_t)((input[i] << 1) | overflow);
        overflow = next_overflow;
    }
}

static void ble_cmac_generate_subkeys(const uint8_t key[16], uint8_t k1[16], uint8_t k2[16]) {
    uint8_t zero[16] = {0};
    uint8_t l[16];

    aes128_ecb_encrypt(key, zero, l);

    /* Обчислення K1 */
    ble_cmac_shift_left(l, k1);
    if (l[0] & 0x80) {
        k1[15] ^= 0x87; /* Константа поля Rb */
    }

    /* Обчислення K2 */
    ble_cmac_shift_left(k1, k2);
    if (k1[0] & 0x80) {
        k2[15] ^= 0x87;
    }
}

/**
 * @brief Повна реалізація AES-CMAC за стандартом RFC 4493
 */
void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]) {
    uint8_t k1[16];
    uint8_t k2[16];
    ble_cmac_generate_subkeys(key, k1, k2);

    size_t n = (msg_len + 15) / 16;
    bool is_complete = false;

    if (n == 0) {
        n = 1;
        is_complete = false;
    } else {
        is_complete = (msg_len % 16 == 0);
    }

    uint8_t m_last[16];
    memset(m_last, 0, sizeof(m_last));

    if (is_complete) {
        for (int i = 0; i < 16; ++i) {
            m_last[i] = msg[(n - 1) * 16 + i] ^ k1[i];
        }
    } else {
        size_t rem = msg_len % 16;
        for (size_t i = 0; i < rem; ++i) {
            m_last[i] = msg[(n - 1) * 16 + i];
        }
        m_last[rem] = 0x80; /* Доповнення бітом 1 і нулями */
        for (int i = 0; i < 16; ++i) {
            m_last[i] ^= k2[i];
        }
    }

    uint8_t x[16] = {0};
    uint8_t y[16];

    for (size_t i = 0; i < n - 1; ++i) {
        for (int j = 0; j < 16; ++j) {
            y[j] = x[j] ^ msg[i * 16 + j];
        }
        aes128_ecb_encrypt(key, y, x);
    }

    for (int j = 0; j < 16; ++j) {
        y[j] = x[j] ^ m_last[j];
    }
    aes128_ecb_encrypt(key, y, mac_out);
}
