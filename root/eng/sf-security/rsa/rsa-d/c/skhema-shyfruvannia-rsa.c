#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* Прототип криптографічної геш-функції SHA-256 */
void sha256(const uint8_t *data, size_t len, uint8_t out[32]);

/* Генератор маски MGF1 на базі SHA-256 (RFC 8017 PKCS#1 v2.2) */
void mgf1_sha256(const uint8_t *seed, size_t seed_len, uint8_t *mask, size_t mask_len) {
    uint32_t counter = 0;
    uint8_t counter_bytes[4];
    uint8_t hash_buf[32 + 4];
    uint8_t digest[32];
    size_t generated = 0;

    memcpy(hash_buf, seed, seed_len);

    while (generated < mask_len) {
        /* Запис лічильника у форматі Big-Endian */
        counter_bytes[0] = (uint8_t)(counter >> 24);
        counter_bytes[1] = (uint8_t)(counter >> 16);
        counter_bytes[2] = (uint8_t)(counter >> 8);
        counter_bytes[3] = (uint8_t)(counter);

        memcpy(hash_buf + seed_len, counter_bytes, 4);
        sha256(hash_buf, seed_len + 4, digest);

        size_t to_copy = mask_len - generated;
        if (to_copy > 32) to_copy = 32;

        memcpy(mask + generated, digest, to_copy);
        generated += to_copy;
        counter++;
    }
}
