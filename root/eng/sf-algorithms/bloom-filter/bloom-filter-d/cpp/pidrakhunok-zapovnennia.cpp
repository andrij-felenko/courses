#include <cstdint>
#include <numeric>
#include <span>
#include <bit>

namespace sys {

// Швидкий підрахунок одиничних бітів у C++20
std::size_t count_set_bits(std::span<const std::uint8_t> bits) noexcept {
    std::size_t total = 0;
    std::size_t i = 0;
    const auto* ptr64 = reinterpret_cast<const std::uint64_t*>(bits.data());
    std::size_t words64 = bits.size() / 8;
    for (; i < words64; ++i) {
        total += static_cast<std::size_t>(std::popcount(ptr64[i]));
    }
    for (std::size_t j = words64 * 8; j < bits.size(); ++j) {
        total += static_cast<std::size_t>(std::popcount(bits[j]));
    }
    return total;
}

} // namespace sys
