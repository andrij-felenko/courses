#include <immintrin.h>
#include <span>
#include <cstddef>

void flush_span_from_cache(std::span<const std::byte> memory) noexcept {
    const auto* ptr = memory.data();
    for (std::size_t offset = 0; offset < memory.size_bytes(); offset += 64) {
        _mm_clflushopt(ptr + offset);
    }
    _mm_sfence();
}
