#include <cstdint>

// Інкапсуляція апаратного дедлайну DWT у C++
class DwtTimeout {
public:
    static void init() noexcept {
        constexpr uint32_t TRCENA = (1UL << 24);
        constexpr uint32_t CYCCNTENA = (1UL << 0);
        CoreDebug->DEMCR |= TRCENA;
        DWT->CYCCNT = 0;
        DWT->CTRL |= CYCCNTENA;
    }

    constexpr DwtTimeout(uint32_t timeout_us, uint32_t cpu_freq_hz) noexcept
        : start_cycles_(DWT->CYCCNT),
          timeout_cycles_(timeout_us * (cpu_freq_hz / 1'000'000UL)) {}

    [[nodiscard]] bool expired() const noexcept {
        const uint32_t elapsed = DWT->CYCCNT - start_cycles_;
        return elapsed >= timeout_cycles_;
    }

private:
    uint32_t start_cycles_{0};
    uint32_t timeout_cycles_{0};
};
