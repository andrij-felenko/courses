// Ідіоматичний DWT-таймер на C++20
#pragma once
#include <cstdint>
#include <concepts>

namespace embedded::timing {

class DwtCycleCounter {
public:
    static inline void init() noexcept {
#if defined(CoreDebug) && defined(DWT)
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
        DWT->CYCCNT = 0;
#endif
    }

    [[nodiscard]] static inline uint32_t now() noexcept {
        __asm__ volatile("" ::: "memory");
        const uint32_t cycles = DWT->CYCCNT;
        __asm__ volatile("" ::: "memory");
        return cycles;
    }
};

template <typename Callable>
[[nodiscard]] inline uint32_t measure_cycles(Callable&& func) noexcept {
    const uint32_t t_start = DwtCycleCounter::now();
    func();
    const uint32_t t_end = DwtCycleCounter::now();
    return (t_end - t_start);
}

} // namespace embedded::timing
