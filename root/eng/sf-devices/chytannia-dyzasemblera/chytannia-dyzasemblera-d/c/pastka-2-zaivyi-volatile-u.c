#include <stdint.h>
#include <stddef.h>

uint32_t checksum_bad(const uint8_t* data, size_t len) {
    volatile uint32_t sum = 0; // ПОМИЛКА: volatile для локальної змінної!
    for (size_t i = 0; i < len; ++i) {
        sum += data[i];
    }
    return sum;
}
