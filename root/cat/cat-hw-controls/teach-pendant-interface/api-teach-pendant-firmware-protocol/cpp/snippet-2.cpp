#include <cstdint>
#include <cstddef>
#include <span>

// Обчислення CRC-16 Modbus на C++ з використанням концепцій безпечної пам'яті
std::uint16_t calculate_crc16_modbus(std::span<const std::uint8_t> data) {
    std::uint16_t crc = 0xFFFF;
    for (std::uint8_t byte : data) {
        crc ^= byte;
        for (std::uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}
