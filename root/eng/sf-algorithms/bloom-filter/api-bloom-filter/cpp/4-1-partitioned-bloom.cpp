#include <span>
#include <cstdint>
#include <cstddef>

namespace sys {

void add_partitioned(std::span<std::uint8_t> bits, std::size_t section_bits,
                     std::size_t k, std::uint64_t h1, std::uint64_t h2) noexcept {
    for (std::size_t i = 0; i < k; ++i) {
        std::size_t bit_in_section = (h1 + i * h2) % section_bits;
        std::size_t global_bit = i * section_bits + bit_in_section;
        bits[global_bit >> 3] |= static_cast<std::uint8_t>(1u << (global_bit & 7));
    }
}

} // namespace sys
