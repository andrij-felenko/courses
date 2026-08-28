#include <iostream>
#include <bit>
#include <cstdint>
#include <span>
#include <concepts>

namespace net {

[[nodiscard]] constexpr uint32_t decode_be32(std::span<const uint8_t, 4> bytes) noexcept {
    if constexpr (std::endian::native == std::endian::little) {
        uint32_t val = (static_cast<uint32_t>(bytes[0]) << 24) |
                       (static_cast<uint32_t>(bytes[1]) << 16) |
                       (static_cast<uint32_t>(bytes[2]) << 8)  |
                       (static_cast<uint32_t>(bytes[3]));
        return val;
    } else {
        uint32_t val = (static_cast<uint32_t>(bytes[3]) << 24) |
                       (static_cast<uint32_t>(bytes[2]) << 16) |
                       (static_cast<uint32_t>(bytes[1]) << 8)  |
                       (static_cast<uint32_t>(bytes[0]));
        return val;
    }
}

} // namespace net
