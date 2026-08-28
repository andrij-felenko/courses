/* Читання серіалізованого лічильника тактів на C++ */
#include <cstdint>

namespace bench {

inline std::uint64_t rdtsc_start() noexcept {
    std::uint32_t cycles_high = 0, cycles_low = 0;
    asm volatile("lfence\n\t"
                 "rdtsc\n\t"
                 : "=a"(cycles_low), "=d"(cycles_high));
    return (static_cast<std::uint64_t>(cycles_high) << 32) | cycles_low;
}

inline std::uint64_t rdtsc_end() noexcept {
    std::uint32_t cycles_high = 0, cycles_low = 0;
    asm volatile("rdtscp\n\t"
                 "lfence\n\t"
                 : "=a"(cycles_low), "=d"(cycles_high)
                 :
                 : "rcx");
    return (static_cast<std::uint64_t>(cycles_high) << 32) | cycles_low;
}

} // namespace bench
