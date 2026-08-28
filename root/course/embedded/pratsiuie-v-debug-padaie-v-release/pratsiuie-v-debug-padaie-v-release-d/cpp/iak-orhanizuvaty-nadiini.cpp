#include <cstdint>
#include <chrono>

// Ідіоматичний C++: типобезпечні інтервали часу на базі DWT
class DwtClock {
public:
    static void init() noexcept {
        // Увімкнення лічильника тактів Cortex-M
        *reinterpret_cast<volatile std::uint32_t*>(0xE000EDFC) |= (1UL << 24); // DEMCR.TRCENA
        *reinterpret_cast<volatile std::uint32_t*>(0xE0001000) |= (1UL << 0);  // DWT_CTRL.CYCCNTENA
    }

    static void delay_us(std::uint32_t microseconds, std::uint32_t cpu_freq_hz) noexcept {
        const std::uint32_t start = *reinterpret_cast<volatile std::uint32_t*>(0xE0001004); // CYCCNT
        const std::uint32_t ticks = microseconds * (cpu_freq_hz / 1'000'000U);
        while ((*reinterpret_cast<volatile std::uint32_t*>(0xE0001004) - start) < ticks) {
            // Апаратне очікування
        }
    }
};
