#include <cstdint>
#include <vector>
#include <cstddef>
#include <algorithm>

namespace sys {

// Метод об'єднання бітових векторів двох фільтрів у C++
void merge_bloom_filters(std::vector<std::uint8_t>& dst, const std::vector<std::uint8_t>& src) noexcept {
    std::size_t min_bytes = std::min(dst.size(), src.size());
    std::size_t i = 0;
    for (; i + 7 < min_bytes; i += 8) {
        auto* d64 = reinterpret_cast<std::uint64_t*>(&dst[i]);
        const auto* s64 = reinterpret_cast<const std::uint64_t*>(&src[i]);
        *d64 |= *s64;
    }
    for (; i < min_bytes; ++i) {
        dst[i] |= src[i];
    }
}

} // namespace sys
