/* Зовнішня функція одиночного дешифрування AES-128 (16 байтів in -> 16 байтів out) */
extern void aes128_decrypt_block(const uint8_t key[16], const uint8_t in[16], uint8_t out[16]);

/**
 * Розгортання ключа контенту (AES Key Unwrap, RFC 3394).
 * in_wrapped: вхідний загорнутий блок довжиною (n + 1) * 8 байтів (24 байти).
 * n: кількість 64-бітних блоків відкритого ключа (для AES-128 n = 2).
 * out_key: вихідний відкритий ключ довжиною n * 8 байтів (16 байтів).
 * Повертає true, якщо цілісність підтверджено (IV збігся), false при збої.
 */
bool aes_key_unwrap_128(const uint8_t kek[16], const uint8_t *in_wrapped, size_t n, uint8_t *out_key) {
    if (!kek || !in_wrapped || !out_key || n == 0) {
        return false;
    }

    uint8_t a[8];
    memcpy(a, in_wrapped, 8);

    uint8_t r[n][8];
    for (size_t i = 0; i < n; ++i) {
        memcpy(r[i], in_wrapped + 8 + (i * 8), 8);
    }

    /* 6 зворотних раундів */
    for (int32_t j = 5; j >= 0; --j) {
        for (size_t i = n; i >= 1; --i) {
            uint64_t t = (uint64_t)(n * j + i);
            for (int k = 0; k < 8; ++k) {
                a[7 - k] ^= (uint8_t)((t >> (k * 8)) & 0xFF);
            }

            uint8_t b_in[16];
            uint8_t b_out[16];

            /* B = AES_inv(K, (A ^ t) | R[i]) */
            memcpy(b_in, a, 8);
            memcpy(b_in + 8, r[i - 1], 8);

            aes128_decrypt_block(kek, b_in, b_out);

            memcpy(a, b_out, 8);
            memcpy(r[i - 1], b_out + 8, 8);
        }
    }

    /* Перевірка вектора цілісності IV */
    if (memcmp(a, DEFAULT_IV, 8) != 0) {
        /* Збій цілісності: очищаємо пам'ять і повертаємо помилку */
        memset(r, 0, sizeof(r));
        return false;
    }

    for (size_t i = 0; i < n; ++i) {
        memcpy(out_key + (i * 8), r[i], 8);
    }

    return true;
}
