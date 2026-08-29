/* periodic_timer.hpp — TIM2 як джерело переривань 1 кГц.
 *
 * Об'єкт володіє периферійним блоком: поки він живий, таймер рахує; коли
 * виходить з області видимості — лічильник зупинено, вектор у NVIC знято,
 * тактування вимкнено. Забути «закрити» таймер тут неможливо.
 */
#pragma once

#include <cstdint>
#include <expected>

#include "hw/mmio.hpp"

namespace hw {

enum class TimerError {
    clock_too_slow,      // із такої частоти мікросекунди не набрати
    clock_not_exact,     // предільник дав би дробове значення
    prescaler_overflow,  // PSC не влазить у 16 біт
};

class PeriodicTimer {
public:
    /* timer_clock — частота на вході самого таймера, а не частота шини:
     * при неодиничному дільнику APB1 довідник подвоює тактову таймерів
     * (на STM32F407 PCLK1 = 42 МГц дає таймеру 84 МГц). */
    [[nodiscard]] static std::expected<PeriodicTimer, TimerError>
    start_1khz(Hertz timer_clock) noexcept;

    ~PeriodicTimer();

    PeriodicTimer(PeriodicTimer&& other) noexcept;
    PeriodicTimer& operator=(PeriodicTimer&& other) noexcept;

    /* Периферійний блок один на весь чип — копіювати володіння нічим. */
    PeriodicTimer(const PeriodicTimer&) = delete;
    PeriodicTimer& operator=(const PeriodicTimer&) = delete;

    /* Кількість переповнень від старту, тобто мілісекунди. */
    [[nodiscard]] std::uint32_t ticks() const noexcept;

private:
    PeriodicTimer() noexcept = default;
    void release() noexcept;

    bool owns_{true};
};

} // namespace hw
