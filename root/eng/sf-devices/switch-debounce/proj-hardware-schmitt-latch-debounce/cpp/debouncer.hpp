#pragma once

#include <cstdint>

namespace embedded {

enum class ButtonEvent : uint8_t {
    None = 0,
    Pressed,
    Released,
    LongPress
};

enum class ButtonState : uint8_t {
    Released = 0,
    DebouncePress,
    Pressed,
    DebounceRelease
};

template <uint16_t DebounceMs = 20, uint16_t LongPressMs = 1000>
class Debouncer {
public:
    constexpr Debouncer() = default;

    ButtonEvent update(bool raw_pressed, uint16_t elapsed_ms) noexcept {
        ButtonEvent event = ButtonEvent::None;

        switch (state_) {
            case ButtonState::Released:
                if (raw_pressed) {
                    state_ = ButtonState::DebouncePress;
                    timer_ms_ = 0;
                }
                break;

            case ButtonState::DebouncePress:
                timer_ms_ += elapsed_ms;
                if (timer_ms_ >= DebounceMs) {
                    if (raw_pressed) {
                        state_ = ButtonState::Pressed;
                        hold_timer_ms_ = 0;
                        long_press_fired_ = false;
                        event = ButtonEvent::Pressed;
                    } else {
                        state_ = ButtonState::Released;
                    }
                }
                break;

            case ButtonState::Pressed:
                if (!raw_pressed) {
                    state_ = ButtonState::DebounceRelease;
                    timer_ms_ = 0;
                } else {
                    hold_timer_ms_ += elapsed_ms;
                    if (!long_press_fired_ && (hold_timer_ms_ >= LongPressMs)) {
                        long_press_fired_ = true;
                        event = ButtonEvent::LongPress;
                    }
                }
                break;

            case ButtonState::DebounceRelease:
                timer_ms_ += elapsed_ms;
                if (timer_ms_ >= DebounceMs) {
                    if (!raw_pressed) {
                        state_ = ButtonState::Released;
                        event = ButtonEvent::Released;
                    } else {
                        state_ = ButtonState::Pressed;
                    }
                }
                break;
        }

        return event;
    }

    [[nodiscard]] bool isPressed() const noexcept {
        return state_ == ButtonState::Pressed;
    }

private:
    ButtonState state_{ButtonState::Released};
    uint16_t timer_ms_{0};
    uint16_t hold_timer_ms_{0};
    bool long_press_fired_{false};
};

} // namespace embedded
