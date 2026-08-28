// dwt_timer.hpp - Ідіоматичний таймер DWT на C++20
#pragma once

#include <cstdint>
#include <chrono>

namespace Hardware {

class DwtTimer {
public:
    static bool init() noexcept {
        demcr() |= demcr_trcena;
        cyccnt() = 0U;
        ctrl() |= ctrl_cyccntena;
        return (ctrl() & ctrl_cyccntena) != 0U;
    }

    [[nodiscard]] static inline uint32_t get_cycles() noexcept {
        return cyccnt();
    }

    [[nodiscard]] static constexpr uint32_t delta_cycles(uint32_t start, uint32_t stop) noexcept {
        return stop - start;
    }

    template <uint32_t CpuFreqHz>
    [[nodiscard]] static constexpr std::chrono::microseconds to_microseconds(uint32_t cycles) noexcept {
        const auto us = (static_cast<uint64_t>(cycles) * 1'000'000ULL) / CpuFreqHz;
        return std::chrono::microseconds(us);
    }

private:
    static constexpr uint32_t demcr_trcena  = (1U << 24);
    static constexpr uint32_t ctrl_cyccntena = (1U << 0);

    static inline volatile uint32_t& demcr() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(0xE000EDFCU);
    }
    static inline volatile uint32_t& ctrl() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(0xE0001000U);
    }
    static inline volatile uint32_t& cyccnt() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(0xE0001004U);
    }
};

} // namespace Hardware
