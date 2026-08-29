#pragma once

/*
 * Тривалість критичної секції в тактах ядра, лічильник DWT->CYCCNT.
 * Заголовок пристрою від виробника тягне core_cm4.h із блоками DWT
 * і CoreDebug та зі змінною SystemCoreClock.
 */

#include <cstdint>

#include "stm32f4xx.h"

#include "critical_section.hpp"

namespace embedded::debug {

class CycleCounter {
public:
    /* false — лічильника немає або він не побіг. Мовчки міряти нулі гірше,
       ніж не міряти взагалі. */
    [[nodiscard]] static bool init() noexcept
    {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        // На частині ядер блок DWT замкнено CoreSight-регістром LAR.
        *reinterpret_cast<volatile std::uint32_t*>(0xE0001FB0U) = 0xC5ACCE55U;

        if ((DWT->CTRL & DWT_CTRL_NOCYCCNT_Msk) != 0U) {
            return false;
        }
        DWT->CYCCNT = 0U;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

        const std::uint32_t probe = DWT->CYCCNT;
        __NOP();
        __NOP();
        __NOP();
        return DWT->CYCCNT != probe;
    }

    [[nodiscard]] static std::uint32_t now() noexcept { return DWT->CYCCNT; }

    /* __BKPT без зневаджувача — це HardFault, тому питаємо CoreDebug. */
    [[nodiscard]] static bool debugger_attached() noexcept
    {
        return (CoreDebug->DHCSR & CoreDebug_DHCSR_C_DEBUGEN_Msk) != 0U;
    }

    [[nodiscard]] static std::uint32_t to_ns(std::uint32_t cycles) noexcept
    {
        return static_cast<std::uint32_t>(
            static_cast<std::uint64_t>(cycles) * 1'000'000'000ULL / SystemCoreClock);
    }
};

struct SectionStats {
    std::uint32_t budget_cycles{0};   // 0 — бюджет не перевіряємо
    std::uint32_t last_cycles{0};
    std::uint32_t max_cycles{0};
    std::uint32_t overruns{0};

    void record(std::uint32_t elapsed) noexcept
    {
        last_cycles = elapsed;
        if (elapsed > max_cycles) {
            max_cycles = elapsed;
        }
        if (budget_cycles != 0U && elapsed > budget_cycles) {
            ++overruns;
            if (CycleCounter::debugger_attached()) {
                __BKPT(0);
            }
        }
    }
};

/*
 * Стан тримаємо самі, а не вкладеним вартовим: тіло деструктора виконується
 * ДО знищення членів, і вкладений вартовий зняв би блокування вже після
 * вимірювання, залишивши вихід із секції поза підрахунком.
 */
template <sync::LockPolicy Policy = sync::PrimaskLockPolicy>
class [[nodiscard]] ProfiledSection {
public:
    explicit ProfiledSection(SectionStats& stats) noexcept
        : stats_{stats}, start_{CycleCounter::now()}, state_{Policy::enter()} {}

    ~ProfiledSection() noexcept
    {
        Policy::exit(state_);
        // Різниця беззнакових коректна й через переповнення лічильника.
        stats_.record(CycleCounter::now() - start_);
    }

    ProfiledSection(const ProfiledSection&) = delete;
    ProfiledSection& operator=(const ProfiledSection&) = delete;
    ProfiledSection(ProfiledSection&&) = delete;
    ProfiledSection& operator=(ProfiledSection&&) = delete;

private:
    SectionStats& stats_;
    std::uint32_t start_;
    typename Policy::StateType state_;
};

}  // namespace embedded::debug
