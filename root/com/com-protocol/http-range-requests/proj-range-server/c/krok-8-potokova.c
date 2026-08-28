#include <stdint.h>
#include <stddef.h>

/* Обчислення швидкої контрольної суми Adler-32 для перевірки зрізу */
uint32_t calculate_adler32(const uint8_t *data, size_t len) {
    uint32_t a = 1, b = 0;
    for (size_t i = 0; i < len; ++i) {
        a = (a + data[i]) % 65521;
        b = (b + a) % 65521;
    }
    return (b << 16) | a;
}
