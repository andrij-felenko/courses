#include <cstdint>
#include <cstddef>
#include <span>

namespace crc {

inline constexpr uint32_t CRC32_POLYNOMIAL = 0x04C11DB7U;

[[nodiscard]] constexpr uint32_t crc32_bitwise(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;

    for (uint8_t byte : data) {
        crc ^= (static_cast<uint32_t>(byte) << 24);

        for (int bit = 0; bit < 8; ++bit) {
            if ((crc & 0x80000000U) != 0) {
                crc = (crc << 1) ^ CRC32_POLYNOMIAL;
            } else {
                crc = (crc << 1);
            }
        }
    }

    return crc ^ 0xFFFFFFFFU;
}

} // namespace crc
