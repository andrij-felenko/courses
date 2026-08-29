// hal/clock.hpp — час у типах, а не в голих мілісекундах.
// std::chrono::milliseconds не дає переплутати період із міткою часу й не
// коштує жодного такту: усе перетворення відбувається на етапі компіляції.
#pragma once

#include <chrono>
#include <cstdint>

namespace hal {

using Millis = std::chrono::milliseconds;

// Монотонний час від старту. Реалізують порти: SysTick на платі,
// віртуальний годинник на комп'ютері розробника.
[[nodiscard]] Millis now() noexcept;

// Приспати ядро до найближчого переривання.
void cpu_sleep() noexcept;

// Активне очікування для коротких апаратних затримок усередині драйверів.
void delay(Millis duration) noexcept;

[[nodiscard]] inline Millis elapsed_since(Millis mark) noexcept
{
    return now() - mark;
}

} // namespace hal
