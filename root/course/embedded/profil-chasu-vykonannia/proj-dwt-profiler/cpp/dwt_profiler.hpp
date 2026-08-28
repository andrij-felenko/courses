// dwt_profiler.hpp — Модуль апаратного профілювання на C++20
#pragma once

#include <cstdint>
#include <concepts>
#include <algorithm>
#include <limits>

namespace embedded::profiler {

#if defined(STM32F407xx) || defined(STM32F746xx) || defined(STM32H743xx)
  #include "stm32f4xx.h"
#else
  inline volatile uint32_t& core_debug_demcr = *reinterpret_cast<volatile uint32_t*>(0xE000EDFCU);
  inline volatile uint32_t& dwt_ctrl         = *reinterpret_cast<volatile uint32_t*>(0xE0001000U);
  inline volatile uint32_t& dwt_cyccnt       = *reinterpret_cast<volatile uint32_t*>(0xE0001004U);
  constexpr uint32_t demcr_trcena_bit  = (1UL << 24);
  constexpr uint32_t dwt_cyccntena_bit = (1UL << 0);
#endif

struct ExecutionStats {
    uint32_t min_cycles{std::numeric_limits<uint32_t>::max()};
    uint32_t max_cycles{0};
    uint64_t total_cycles{0};
    uint32_t samples_count{0};

    constexpr void update(uint32_t cycles) noexcept {
        min_cycles = std::min(min_cycles, cycles);
        max_cycles = std::max(max_cycles, cycles);
        total_cycles += cycles;
        ++samples_count;
    }

    [[nodiscard]] constexpr uint32_t average_cycles() const noexcept {
        return (samples_count > 0) ? static_cast<uint32_t>(total_cycles / samples_count) : 0;
    }

    constexpr void reset() noexcept {
        min_cycles = std::numeric_limits<uint32_t>::max();
        max_cycles = 0;
        total_cycles = 0;
        samples_count = 0;
    }
};

class DwtProfiler {
public:
    static bool init() noexcept {
#if defined(CoreDebug) && defined(DWT)
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
        DWT->CYCCNT = 0;
#else
        core_debug_demcr |= demcr_trcena_bit;
        dwt_ctrl |= dwt_cyccntena_bit;
        dwt_cyccnt = 0;
#endif
        calibrate();
        return is_running();
    }

    [[nodiscard]] static inline uint32_t get_cycles() noexcept {
#if defined(DWT)
        return DWT->CYCCNT;
#else
        return dwt_cyccnt;
#endif
    }

    [[nodiscard]] static uint32_t elapsed_cycles(uint32_t start_cycles) noexcept {
        const uint32_t now = get_cycles();
        const uint32_t raw_delta = now - start_cycles;
        return (raw_delta > s_overhead) ? (raw_delta - s_overhead) : 0;
    }

    [[nodiscard]] static constexpr uint64_t to_nanoseconds(uint32_t cycles, uint32_t cpu_freq_hz) noexcept {
        if (cpu_freq_hz == 0) return 0;
        return (static_cast<uint64_t>(cycles) * 1'000'000'000ULL) / cpu_freq_hz;
    }

    [[nodiscard]] static uint32_t get_overhead() noexcept {
        return s_overhead;
    }

private:
    static inline uint32_t s_overhead{0};

    static bool is_running() noexcept {
#if defined(DWT)
        return (DWT->CTRL & DWT_CTRL_CYCCNTENA_Msk) != 0;
#else
        return (dwt_ctrl & dwt_cyccntena_bit) != 0;
#endif
    }

    static void calibrate() noexcept {
        s_overhead = 0;
        uint32_t accumulated = 0;
        constexpr uint32_t iterations = 16;

        for (uint32_t i = 0; i < iterations; ++i) {
            __asm__ volatile("" ::: "memory"); // Бар'єр компілятора
            const uint32_t t0 = get_cycles();
            __asm__ volatile("" ::: "memory");
            const uint32_t t1 = get_cycles();
            accumulated += (t1 - t0);
        }
        s_overhead = accumulated / iterations;
    }
};

/**
 * @brief RAII-обгортка для автоматичного вимірювання тривалості блоку коду.
 */
class [[nodiscard]] ScopedTimer {
public:
    explicit ScopedTimer(ExecutionStats& stats) noexcept
        : m_stats(stats), m_start_cycles(DwtProfiler::get_cycles()) {}

    ~ScopedTimer() noexcept {
        const uint32_t elapsed = DwtProfiler::elapsed_cycles(m_start_cycles);
        m_stats.update(elapsed);
    }

    ScopedTimer(const ScopedTimer&) = delete;
    ScopedTimer& operator=(const ScopedTimer&) = delete;
    ScopedTimer(ScopedTimer&&) = delete;
    ScopedTimer& operator=(ScopedTimer&&) = delete;

private:
    ExecutionStats& m_stats;
    const uint32_t m_start_cycles;
};

} // namespace embedded::profiler
