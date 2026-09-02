#pragma once

#include <cstdint>
#include <optional>

namespace board {

enum class ButtonEvent : std::uint8_t { Pressed, Released };

// Періодичне опитування. Стан автомата — це пара «останній визнаний рівень +
// скільки опитувань поспіль лінія показує протилежне»; поки лічильник не дійшов
// до StableTicks, зміна вважається брязкотом і події не дає.
//
// Заліза клас не торкається взагалі: рівень йому передають аргументом, тож
// автомат ганяється на столі звичайним юніт-тестом.
template <std::uint8_t StableTicks = 5>
class Debouncer {
    static_assert(StableTicks >= 2, "одне опитування не відрізняє брязкіт від натискання");

public:
    // pressedNow — стан у момент старту: якщо кнопку тримають від увімкнення
    // живлення, автомат не сміє видати фальшиве натискання.
    constexpr explicit Debouncer(bool pressedNow = false) noexcept : pressed_{pressedNow} {}

    // Викликається строго періодично, раз на 10 мс.
    constexpr std::optional<ButtonEvent> update(bool pressedRaw) noexcept {
        if (pressedRaw == pressed_) {
            counter_ = 0;  // лінія повернулася до визнаного рівня — це був брязкіт
            return std::nullopt;
        }
        if (++counter_ < StableTicks) {
            return std::nullopt;
        }
        counter_ = 0;
        pressed_ = pressedRaw;
        return pressed_ ? ButtonEvent::Pressed : ButtonEvent::Released;
    }

    [[nodiscard]] constexpr bool pressed() const noexcept { return pressed_; }

private:
    std::uint8_t counter_{0};
    bool pressed_{false};
};

}  // namespace board
