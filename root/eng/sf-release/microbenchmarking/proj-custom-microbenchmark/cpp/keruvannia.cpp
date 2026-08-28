#include <span>
#include <cstdint>

namespace bench {

inline void flush_cache(std::span<const std::byte> memory_range) noexcept {
    const auto* ptr = reinterpret_cast<const char*>(memory_range.data());
    for (std::size_t i = 0; i < memory_range.size(); i += 64) {
        __builtin_ia32_clflushopt(reinterpret_cast<const void*>(ptr + i));
    }
    asm volatile("sfence" : : : "memory");
}

} // namespace bench
