#include <iostream>
#include <iomanip>
#include <cstdint>
#include <span>
#include <string_view>

extern "C" const uint32_t g_crc32_lookup[256];

namespace telemetry {

[[nodiscard]] uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (const uint8_t byte_val : data) {
        const uint8_t table_idx = static_cast<uint8_t>((crc ^ byte_val) & 0xFFU);
        crc = (crc >> 8U) ^ g_crc32_lookup[table_idx];
    }
    return crc ^ 0xFFFFFFFFU;
}

} // namespace telemetry

int main() {
    constexpr std::string_view msg = "Firmware telemetry packet payload";
    const std::span<const uint8_t> payload_bytes{
        reinterpret_cast<const uint8_t*>(msg.data()), msg.size()
    };

    const uint32_t checksum = telemetry::calculate_crc32(payload_bytes);
    std::cout << "Обчислена контрольна сума CRC-32: 0x"
              << std::hex << std::uppercase << std::setfill('0') << std::setw(8)
              << checksum << '\n';
    return 0;
}
