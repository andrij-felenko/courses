#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

namespace integrity {

[[nodiscard]] constexpr std::uint32_t calculate_crc32(std::span<const std::uint8_t> data) noexcept {
    std::uint32_t crc = 0xFFFFFFFFU;
    for (const auto byte : data) {
        crc ^= byte;
        for (std::uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 1U) {
                crc = (crc >> 1U) ^ 0xEDB88320U;
            } else {
                crc >>= 1U;
            }
        }
    }
    return ~crc;
}

} // namespace integrity
