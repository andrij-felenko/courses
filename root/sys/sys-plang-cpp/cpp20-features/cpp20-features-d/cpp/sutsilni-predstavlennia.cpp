#include <span>
#include <vector>
#include <array>

void process_buffer(std::span<const uint8_t> buffer) {
    for (uint8_t byte : buffer) {
        // Обробка байтів
    }
}

uint8_t raw[128];
std::vector<uint8_t> vec(64);
std::array<uint8_t, 32> arr;

process_buffer(raw); // Працює з C-масивом
process_buffer(vec); // Працює з std::vector
process_buffer(arr); // Працює з std::array
