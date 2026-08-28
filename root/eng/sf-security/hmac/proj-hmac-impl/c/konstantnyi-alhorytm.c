#include <stdint.h>
#include <stddef.h>

/**
 * Безпечне порівняння двох буферів однакової довжини в константному часі.
 * Повертає 1, якщо буфери ідентичні, і 0 у разі будь-якої розбіжності.
 */
int constant_time_memcmp(const void *a, const void *b, size_t len) {
    const volatile uint8_t *pa = (const volatile uint8_t *)a;
    const volatile uint8_t *pb = (const volatile uint8_t *)b;
    volatile uint8_t diff = 0;

    for (size_t i = 0; i < len; i++) {
        diff |= (pa[i] ^ pb[i]);
    }

    /* Відображення: diff == 0 -> 1; diff != 0 -> 0 без розгалужень */
    return (int)((1u ^ ((diff | (0u - diff)) >> 31)));
}

/**
 * Верифікація HMAC-SHA256 підпису.
 */
int hmac_sha256_verify(const uint8_t *key, size_t key_len,
                       const uint8_t *msg, size_t msg_len,
                       const uint8_t expected_mac[32]) {
    uint8_t computed_mac[32];
    hmac_sha256(key, key_len, msg, msg_len, computed_mac);

    int is_valid = constant_time_memcmp(computed_mac, expected_mac, 32);

    /* Безпечне затирання обчисленого підпису у стеку */
    for (volatile int i = 0; i < 32; i++) computed_mac[i] = 0;

    return is_valid;
}
