#include <stdint.h>
#include <stddef.h>

/**
 * @brief Безпечне порівняння двох блоків пам'яті за константний час
 * @return 0, якщо блоки ідентичні; ненульове значення, якщо є розбіжність
 */
int ble_crypto_constant_time_memcmp(const void *a, const void *b, size_t len) {
    const uint8_t *p1 = (const uint8_t *)a;
    const uint8_t *p2 = (const uint8_t *)b;
    uint8_t diff = 0;

    for (size_t i = 0; i < len; ++i) {
        diff |= (p1[i] ^ p2[i]);
    }

    return (int)diff;
}
