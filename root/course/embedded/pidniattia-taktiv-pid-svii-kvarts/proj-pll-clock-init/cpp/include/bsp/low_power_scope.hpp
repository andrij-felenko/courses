#pragma once

#include "bsp/clock_tree.hpp"

/*
 * Динамічна зміна частоти (DVFS).
 * Порядок кроків строго зворотний: усе, що дозволяє швидкість, робиться
 * до її підняття — і після її зниження.
 */

namespace bsp::clock {

/* 168 МГц PLL -> 16 МГц HSI: Scale 3, Flash 0 WS, PLL вимкнено */
[[nodiscard]] Result enter_low_power() noexcept;

/* 16 МГц HSI -> 168 МГц PLL: дзеркальний порядок */
[[nodiscard]] Result enter_full_speed() noexcept;

/*
 * Пара «знизити/підняти» як область видимості: вихід із блоку сам повертає
 * повну швидкість, навіть коли з нього виходять раннім return. У C цю пару
 * доводиться тримати в голові й дублювати на кожній гілці.
 */
class LowPowerScope {
public:
    LowPowerScope() noexcept;
    ~LowPowerScope();

    LowPowerScope(const LowPowerScope&) = delete;
    LowPowerScope& operator=(const LowPowerScope&) = delete;

    /* Чи вдалося справді знизити частоту (наприклад, HSI міг не піднятися) */
    [[nodiscard]] bool lowered() const noexcept { return lowered_; }

private:
    bool lowered_;
};

} // namespace bsp::clock
