#include <x86intrin.h>
#include <cstdint>

namespace sys {
    inline std::uint64_t calculate_ns(std::uint64_t time_zero, std::uint32_t time_mult, std::uint16_t time_shift) noexcept {
        std::uint64_t tsc = __rdtsc();
        std::uint64_t quot = tsc >> time_shift;
        std::uint64_t rem  = tsc & ((1ULL << time_shift) - 1);
        return time_zero + quot * time_mult + ((rem * time_mult) >> time_shift);
    }
}
