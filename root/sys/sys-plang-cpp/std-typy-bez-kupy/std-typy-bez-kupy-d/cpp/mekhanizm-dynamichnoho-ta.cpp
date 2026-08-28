#include <span>
#include <cstdint>
#include <array>

// Функція приймає будь-яку неперервну пам'ять: C-масив, std::array, буфер DMA
uint16_t calculate_crc16(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (int i = 0; i < 8; ++i) {
            crc = (crc & 1) ? ((crc >> 1) ^ 0xA001) : (crc >> 1);
        }
    }
    return crc;
}

void demo_span() {
    uint8_t c_buffer[16] = {0};
    std::array<uint8_t, 32> cpp_array{};

    // Обидва виклики безпечні та автоматично формують std::span
    calculate_crc16(c_buffer);
    calculate_crc16(cpp_array);
}
