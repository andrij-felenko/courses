#include <string_view>
#include <cstdint>

namespace sys {

// Метод C++ для вставки префікса складеного ключа
void insert_prefix_key(std::span<std::uint8_t> bit_array, std::size_t m, std::size_t k,
                       std::string_view full_key, std::size_t prefix_len) noexcept {
    std::string_view prefix = full_key.substr(0, std::min(prefix_len, full_key.size()));
    auto [h1, h2] = hash_128(prefix.data(), prefix.size());
    for (std::size_t i = 0; i < k; ++i) {
        std::size_t idx = (h1 + i * h2) % m;
        bit_array[idx >> 3] |= static_cast<std::uint8_t>(1u << (idx & 7));
    }
}

} // namespace sys
