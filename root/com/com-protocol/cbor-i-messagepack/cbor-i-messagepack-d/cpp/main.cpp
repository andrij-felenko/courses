// Безпечне зчитування Big-Endian uint32 у C++20 / C++23
#include <bit>
#include <cstring>
#include <span>

inline uint32_t read_be32(std::span<const uint8_t, 4> bytes) noexcept {
    uint32_t val;
    std::memcpy(&val, bytes.data(), sizeof(val));
    if constexpr (std::endian::native == std::endian::little) {
        return std::byteswap(val);
    }
    return val;
}
