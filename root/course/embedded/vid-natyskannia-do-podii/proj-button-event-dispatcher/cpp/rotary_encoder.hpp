#pragma once

#include <array>
#include <concepts>
#include <cstddef>
#include <cstdint>

#include "event_queue.hpp"
#include "input_event.hpp"

namespace input {

template <class T>
concept PhasePolicy = requires {
    { T::isHigh() } noexcept -> std::same_as<bool>;
};

/* Декодер квадратури на таблиці переходів коду Грея. Обидві фази — політики,
   тож увесь декодер компілюється в кілька інструкцій без жодного непрямого
   виклику: це і є та сама абстракція за нульову ціну. */
template <PhasePolicy PhaseA, PhasePolicy PhaseB>
class RotaryEncoder {
public:
    /* Скільки чвертей періоду припадає на один клац фіксатора. */
    static constexpr std::int8_t StepsPerDetent = 4;

    explicit RotaryEncoder(std::uint8_t id) noexcept : id_{id}, prev_{sample()} {}

    template <std::size_t N>
    void tick(EventQueue<InputEvent, N>& queue) noexcept {
        const std::uint8_t curr = sample();
        if (curr == prev_) {
            return;  // вал стоїть — найчастіший випадок
        }

        const std::uint8_t code = static_cast<std::uint8_t>((prev_ << 2) | curr);
        const std::int8_t step = Table[code];
        prev_ = curr;

        if (step == 0) {
            /* Обидва біти змінилися між вибірками: сильний брязкіт або вал
               крутнули швидше за темп опитування. Напрямок невідомий — краще
               втратити крок, ніж додати хибний. */
            if (glitches_ < UINT16_MAX) {
                ++glitches_;
            }
            return;
        }

        // Зміна напрямку посеред клацу: недокручені чверті вже нічого не значать.
        if ((step > 0 && subSteps_ < 0) || (step < 0 && subSteps_ > 0)) {
            subSteps_ = 0;
        }
        subSteps_ = static_cast<std::int8_t>(subSteps_ + step);

        if (subSteps_ >= StepsPerDetent) {
            subSteps_ = 0;
            queue.push(InputEvent{id_, EventType::EncoderCW, 1});
        } else if (subSteps_ <= -StepsPerDetent) {
            subSteps_ = 0;
            queue.push(InputEvent{id_, EventType::EncoderCCW, 1});
        }
    }

    [[nodiscard]] constexpr std::uint16_t glitches() const noexcept { return glitches_; }

private:
    /* Індекс = (prev << 2) | curr, стани у порядку [A B] = 00, 01, 10, 11.
       Нуль означає «руху немає» або «так не буває» (00↔11, 01↔10). */
    static constexpr std::array<std::int8_t, 16> Table{
         0, +1, -1,  0,
        -1,  0,  0, +1,
        +1,  0,  0, -1,
         0, -1, +1,  0
    };

    static std::uint8_t sample() noexcept {
        return static_cast<std::uint8_t>((PhaseA::isHigh() ? 0b10 : 0b00) |
                                         (PhaseB::isHigh() ? 0b01 : 0b00));
    }

    std::uint8_t  id_{0};
    std::uint8_t  prev_{0};
    std::int8_t   subSteps_{0};
    std::uint16_t glitches_{0};
};

}  // namespace input
