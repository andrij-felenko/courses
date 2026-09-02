#pragma once

#include <chrono>
#include <concepts>
#include <cstddef>
#include <cstdint>

#include "event_queue.hpp"
#include "input_event.hpp"

namespace input {

/* Тривалості типізовані, але 16-бітні: заради кнопки ніхто не тримає
   64-бітний std::chrono::milliseconds на мікроконтролері. */
using Millis = std::chrono::duration<std::uint16_t, std::milli>;

/* Пін віддається політикою, а не std::function: виклик інлайниться, купа не
   потрібна, віртуальної таблиці немає. Active-low живе в самій політиці —
   автомат про рівні напруги не знає нічого. */
template <class T>
concept PinPolicy = requires {
    { T::isPressed() } noexcept -> std::same_as<bool>;
};

/* Насичене додавання: утримання довше за 65 секунд не повинно обернути
   лічильник на нуль і вдати коротке натискання. */
constexpr Millis addSat(Millis base, Millis delta) noexcept {
    const std::uint32_t sum = std::uint32_t{base.count()} + std::uint32_t{delta.count()};
    return Millis{static_cast<std::uint16_t>(sum > 0xFFFFu ? 0xFFFFu : sum)};
}

template <PinPolicy Pin>
class Button {
public:
    enum class State : std::uint8_t {
        Idle,
        DebouncingPress,
        Pressed,
        DebouncingRelease,
        WaitDoubleClick,
        LongPress,
        Repeat
    };

    explicit constexpr Button(std::uint8_t id) noexcept : id_{id} {}

    /* Викликається з переривання таймера рівно раз на тік. dt передається
       явно: якщо таймер плаває через пріоритетніші переривання, автомат усе
       одно міряє час, а не тіки. */
    template <std::size_t N>
    void tick(Millis dt, EventQueue<InputEvent, N>& queue) noexcept {
        const bool low = Pin::isPressed();

        /* Зсувний регістр: одиниця — вибірка «відпущено». Вісім однакових
           поспіль (0xFF або 0x00) означають стабільний рівень: при тіку 5 мс
           це 40 мс тиші, довше за брязкіт будь-якої тактової кнопки. */
        history_ = static_cast<std::uint8_t>((history_ << 1) | (low ? 0u : 1u));
        const bool stablePressed  = (history_ == 0x00);
        const bool stableReleased = (history_ == 0xFF);

        timer_ = addSat(timer_, dt);

        const auto emit = [&](EventType type, Millis value) noexcept {
            queue.push(InputEvent{id_, type, value.count()});
        };

        switch (state_) {
        case State::Idle:
            // Перший же низький рівень лише ЗАПУСКАЄ перевірку.
            if (low) {
                state_ = State::DebouncingPress;
                timer_ = Millis{0};
            }
            break;

        case State::DebouncingPress:
            if (stablePressed) {
                pressDuration_ = timer_;  // дебаунс теж був утриманням
                timer_ = Millis{0};
                longFired_ = false;
                state_ = State::Pressed;
                emit(EventType::ButtonPress, Millis{0});
                if (secondPress_) {
                    emit(EventType::ButtonDoubleClick, gap_);
                    secondPress_ = false;
                    noClick_ = true;  // після подвійного одинарного не буде
                }
            } else if (stableReleased || timer_ > DebounceTimeout) {
                // Стабільного нуля так і не дочекалися: наведення, не натискання.
                state_ = State::Idle;
                secondPress_ = false;
            }
            break;

        case State::Pressed:
            pressDuration_ = addSat(pressDuration_, dt);
            if (!low) {
                state_ = State::DebouncingRelease;
                timer_ = Millis{0};
            } else if (!longFired_ && pressDuration_ >= LongPressThreshold) {
                longFired_ = true;
                noClick_ = true;
                state_ = State::LongPress;
                timer_ = Millis{0};
                emit(EventType::ButtonLongPressStart, pressDuration_);
            }
            break;

        case State::DebouncingRelease:
            pressDuration_ = addSat(pressDuration_, dt);
            if (stableReleased) {
                emit(EventType::ButtonRelease, pressDuration_);
                if (noClick_) {
                    noClick_ = false;
                    longFired_ = false;
                    state_ = State::Idle;
                } else {
                    state_ = State::WaitDoubleClick;
                    timer_ = Millis{0};
                }
            } else if (stablePressed) {
                // Брязкіт розмикання, а не відпускання: вертаємось назад.
                state_ = longFired_ ? State::Repeat : State::Pressed;
                timer_ = Millis{0};
            }
            break;

        case State::WaitDoubleClick:
            if (low) {
                gap_ = timer_;
                secondPress_ = true;
                state_ = State::DebouncingPress;
                timer_ = Millis{0};
            } else if (timer_ >= DoubleClickWindow) {
                // Вікно минуло — аж тепер клік одинарний.
                emit(EventType::ButtonShortClick, pressDuration_);
                state_ = State::Idle;
            }
            break;

        case State::LongPress:
            pressDuration_ = addSat(pressDuration_, dt);
            if (!low) {
                state_ = State::DebouncingRelease;
                timer_ = Millis{0};
            } else if (timer_ >= HoldReportPeriod) {
                timer_ = Millis{0};
                state_ = State::Repeat;
                emit(EventType::ButtonLongPressHold, pressDuration_);
            }
            break;

        case State::Repeat:
            pressDuration_ = addSat(pressDuration_, dt);
            if (!low) {
                state_ = State::DebouncingRelease;
                timer_ = Millis{0};
            } else if (timer_ >= repeatInterval(pressDuration_)) {
                timer_ = Millis{0};
                emit(EventType::ButtonRepeat, pressDuration_);
            }
            break;
        }
    }

    [[nodiscard]] constexpr State state() const noexcept { return state_; }

private:
    static constexpr Millis DebounceTimeout{60};    // довше за 8 вибірок історії
    static constexpr Millis LongPressThreshold{800};
    static constexpr Millis DoubleClickWindow{250};
    static constexpr Millis HoldReportPeriod{100};
    static constexpr Millis RepeatSlow{100};
    static constexpr Millis RepeatFast{20};
    static constexpr Millis FullSpeedAfter{3000};

    /* Розгін автоповтору: лінійно від RepeatSlow одразу після порогу
       утримання до RepeatFast на FullSpeedAfter. Саме це дає плавне
       перемотування меню від 0 до 1000 одним натисканням. */
    static constexpr Millis repeatInterval(Millis held) noexcept {
        if (held <= LongPressThreshold) {
            return RepeatSlow;
        }
        if (held >= FullSpeedAfter) {
            return RepeatFast;
        }
        const std::uint32_t span = std::uint32_t{FullSpeedAfter.count()} -
                                   std::uint32_t{LongPressThreshold.count()};
        const std::uint32_t past = std::uint32_t{held.count()} -
                                   std::uint32_t{LongPressThreshold.count()};
        const std::uint32_t drop = (std::uint32_t{RepeatSlow.count()} -
                                    std::uint32_t{RepeatFast.count()}) * past / span;
        return Millis{static_cast<std::uint16_t>(RepeatSlow.count() - drop)};
    }

    std::uint8_t  id_{0};
    State         state_{State::Idle};
    Millis        timer_{0};          // час у поточному стані
    Millis        pressDuration_{0};  // тривалість поточного утримання
    Millis        gap_{0};            // пауза між кліками пари
    std::uint8_t  history_{0xFF};     // стартуємо з «відпущено»
    bool          longFired_{false};
    bool          noClick_{false};
    bool          secondPress_{false};
};

}  // namespace input
