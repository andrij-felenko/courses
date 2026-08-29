// systick_counter.hpp — запасне джерело тактів для ядер без DWT
// (Cortex-M0/M0+: STM32F0, STM32L0, RP2040).
//
// SysTick рахує ВНИЗ від LOAD до нуля, розрядність 24 біти. Прапорець
// COUNTFLAG зводиться при переході через нуль і скидається читанням CTRL,
// тож один оберт за час заміру ми бачимо, а другий — уже ні.
#pragma once

#include <cstdint>
#include <limits>

#include "dwt_profiler.hpp" // mmio::reg

namespace embedded::profiler {

class SysTickCounter {
public:
    /// Пускає таймер у вільний біг на повну 24-бітну глибину.
    /// УВАГА: забирає SysTick у HAL/RTOS — системний тік на цей час стане.
    static std::uint32_t init() noexcept {
        mmio::reg(ctrl_addr) = 0;             // зупинити на час переналаштування
        mmio::reg(load_addr) = max_load;      // найдовший період: 2^24 тактів
        mmio::reg(val_addr) = 0;              // запис скидає лічильник і COUNTFLAG
        mmio::reg(ctrl_addr) = enable | clksource; // від HCLK, без переривання

        static_cast<void>(mmio::reg(ctrl_addr)); // гасимо COUNTFLAG від пуску
        s_overhead = calibrate();
        return s_overhead;
    }

    /// Показ лічильника на початок заміру.
    [[nodiscard]] static std::uint32_t start() noexcept {
        // Чистимо прапорець ПЕРЕД заміром, інакше побачимо чужий оберт.
        static_cast<void>(mmio::reg(ctrl_addr));
        return mmio::reg(val_addr);
    }

    [[nodiscard]] static std::uint32_t elapsed_cycles(std::uint32_t start_value) noexcept {
        const std::uint32_t now = mmio::reg(val_addr);
        // Читання CTRL і скидає, і повертає COUNTFLAG — робимо його рівно раз.
        const bool wrapped = (mmio::reg(ctrl_addr) & countflag) != 0;
        const std::uint32_t period = mmio::reg(load_addr) + 1U;

        // Один оберт: дорахували від start до нуля й далі від LOAD до now.
        // Другого обертання прапорець не розрізняє — на 48 МГц межа заміру
        // це ≈ 349 мс, і довші ділянки цим лічильником просто не міряють.
        const std::uint32_t elapsed =
            wrapped ? start_value + (period - now) : start_value - now;

        return elapsed > s_overhead ? elapsed - s_overhead : 0U;
    }

    [[nodiscard]] static std::uint32_t overhead() noexcept { return s_overhead; }

private:
    static constexpr std::uintptr_t ctrl_addr = 0xE000E010U;
    static constexpr std::uintptr_t load_addr = 0xE000E014U;
    static constexpr std::uintptr_t val_addr = 0xE000E018U;

    static constexpr std::uint32_t enable = 1U << 0;
    static constexpr std::uint32_t clksource = 1U << 2; // 1 — від HCLK, без ділення на 8
    static constexpr std::uint32_t countflag = 1U << 16;
    static constexpr std::uint32_t max_load = 0x00FFFFFFU;

    static std::uint32_t calibrate() noexcept {
        std::uint32_t best = std::numeric_limits<std::uint32_t>::max();

        for (int i = 0; i < 32; ++i) {
            __asm__ volatile("" ::: "memory");
            const std::uint32_t v0 = mmio::reg(val_addr);
            __asm__ volatile("" ::: "memory");
            const std::uint32_t v1 = mmio::reg(val_addr);

            if (const std::uint32_t delta = v0 - v1; delta < best) { // рахує вниз
                best = delta;
            }
        }
        return best;
    }

    static inline std::uint32_t s_overhead{0};
};

} // namespace embedded::profiler
