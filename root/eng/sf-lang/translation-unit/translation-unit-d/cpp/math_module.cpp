// math_module.cpp
#include <span>
#include <cstdint>

// Визначення глобальної змінної та функції (External Linkage)
int g_operation_count = 0;

int calculate_checksum(std::span<const uint8_t> data) noexcept {
    g_operation_count++;
    int sum = 0;
    for (uint8_t byte : data) {
        sum += byte;
    }
    return sum;
}
