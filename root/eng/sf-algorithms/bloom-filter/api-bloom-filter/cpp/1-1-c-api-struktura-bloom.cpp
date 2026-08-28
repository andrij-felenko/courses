#include <cstdint>
#include <vector>
#include <cstddef>

namespace sys {

struct bloom_filter_data {
    std::vector<std::uint8_t> bits; // Динамічний бітовий масив C++
    std::size_t num_bits{0};        // Кількість бітів m
    std::size_t num_hashes{0};      // Кількість хеш-функцій k
    std::size_t count{0};           // Кількість елементів n
};

} // namespace sys
