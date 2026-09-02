#pragma once

#include <optional>

#include "debouncer.hpp"

namespace board {

// Другий підхід зі статті: фронт на лінії EXTI0 маскує саму лінію й запускає
// одноразовий TIM3 на 20 мс; рівень зчитується вже після брязкоту. У спокої
// кнопка не коштує процесору жодного такту.
class InterruptButton {
public:
    static void start() noexcept;

    // Забирає накопичену подію й одразу її гасить. Кличеться з головного циклу.
    [[nodiscard]] static std::optional<ButtonEvent> takeEvent() noexcept;
};

}  // namespace board
