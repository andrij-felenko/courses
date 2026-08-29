// Джерела пробудження: кнопка на EXTI0 і будильник RTC.
//
// Окремий модуль, бо саме тут ламаються найтихіше: плата, що заснула без
// жодного дозволеного джерела, зовні не відрізняється від зависання.
#pragma once

#include <chrono>
#include <optional>
#include <string_view>

#include "mcu.hpp"

namespace lowpower {

enum class WakeReason { Button, Rtc };

[[nodiscard]] constexpr std::string_view describe(WakeReason r) noexcept
{
    switch (r) {
    case WakeReason::Button: return "кнопка";
    case WakeReason::Rtc:    return "будильник RTC";
    }
    return "?";
}

namespace wakeup {

// Одноразове налаштування EXTI0 і годинника RTC.
void init();

// Заводить будильник RTC. Роздільність — секунда (лічильник від ck_spre).
void arm(std::chrono::seconds after);

// Скидає прапорці EXTI, RTC і черги NVIC. Без цього WFI повернеться миттєво:
// незнятий pending будить ядро тієї ж миті.
void clear_pending();

// Порожньо, якщо після останнього clear_pending() ніхто не будив.
[[nodiscard]] std::optional<WakeReason> last_reason();

} // namespace wakeup
} // namespace lowpower
