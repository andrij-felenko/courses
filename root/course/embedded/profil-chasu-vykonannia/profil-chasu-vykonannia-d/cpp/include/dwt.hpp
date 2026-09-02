// Лічильник тактів ядра й накопичувач розкиду. Роздільна здатність — один
// такт; на 168 МГц це 5.95 нс.
#pragma once

#include <atomic>
#include <cstdint>
#include <limits>
#include <utility>

#include "stm32f4xx.h"

namespace prof {

class Dwt {
public:
    // Розблоковує трасування й перевіряє ділом, що лічильник пішов.
    [[nodiscard]] static bool enable() noexcept
    {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
#if defined(__CORTEX_M) && (__CORTEX_M == 7U)
        // На Cortex-M7 блок трасування замкнений, і запис у CTRL мовчки не діє.
        *reinterpret_cast<volatile std::uint32_t*>(0xE0001FB0UL) = 0xC5ACCE55UL;
#endif
        if ((DWT->CTRL & DWT_CTRL_NOCYCCNT_Msk) != 0U) {
            return false;   // кремній без CYCCNT
        }

        DWT->CYCCNT = 0U;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
        __DSB();

        const std::uint32_t first = now();
        for (volatile unsigned i = 0U; i < 8U; ++i) {
        }
        return now() != first;
    }

    [[nodiscard]] static std::uint32_t now() noexcept
    {
        // Бар'єр рівня компілятора: читання лічильника не має переїхати
        // через вимірюваний код. Апаратних бар'єрів тут не потрібно.
        std::atomic_signal_fence(std::memory_order_seq_cst);
        const std::uint32_t cycles = DWT->CYCCNT;
        std::atomic_signal_fence(std::memory_order_seq_cst);
        return cycles;
    }

    // Різниця коректна й через переповнення: арифметика за модулем 2^32.
    [[nodiscard]] static std::uint32_t since(std::uint32_t start) noexcept
    {
        return now() - start;
    }

    [[nodiscard]] static constexpr std::uint32_t micros_x100(std::uint32_t cycles,
                                                             std::uint32_t f_mhz) noexcept
    {
        return static_cast<std::uint32_t>((static_cast<std::uint64_t>(cycles) * 100U) / f_mhz);
    }
};

// Міряє власну область видимості й кладе результат у чужу змінну.
class [[nodiscard]] ScopedCycleMeter {
public:
    explicit ScopedCycleMeter(std::uint32_t& sink) noexcept
        : sink_{sink}, start_{Dwt::now()} {}

    ~ScopedCycleMeter() noexcept { sink_ = Dwt::now() - start_; }

    ScopedCycleMeter(const ScopedCycleMeter&) = delete;
    ScopedCycleMeter& operator=(const ScopedCycleMeter&) = delete;

private:
    std::uint32_t& sink_;
    std::uint32_t start_;
};

template <class Fn>
[[nodiscard]] std::uint32_t measure(Fn&& fn) noexcept
{
    const std::uint32_t start = Dwt::now();
    std::forward<Fn>(fn)();
    return Dwt::now() - start;
}

// Смуга [min; max] — те, що насправді описує систему реального часу;
// середнє тут не має сенсу.
struct CycleSpan {
    std::uint32_t min{std::numeric_limits<std::uint32_t>::max()};
    std::uint32_t max{0};
    std::uint32_t count{0};

    constexpr void add(std::uint32_t cycles) noexcept
    {
        if (cycles < min) { min = cycles; }
        if (cycles > max) { max = cycles; }
        ++count;
    }

    [[nodiscard]] constexpr std::uint32_t jitter() const noexcept
    {
        return (count != 0U) ? (max - min) : 0U;
    }
};

}  // namespace prof
