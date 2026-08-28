#include <cstdint>
#include <span>

uint32_t checksum_bad(std::span<const uint8_t> data) {
    volatile uint32_t sum = 0; // ПОМИЛКА: volatile для локальної змінної!
    for (uint8_t byte : data) {
        sum += byte;
    }
    return sum;
}
