/* Файл: ButtonLedDriver.hpp (C++20: RAII, Type-Safe, Object-Oriented) */
#include <cstdint>
#include <concepts>
#include <functional>

template <typename GpioReader, typename GpioWriter>
class DebouncedButtonLed {
public:
    enum class State { Released, DebouncingPress, Held, DebouncingRelease };

    constexpr DebouncedButtonLed(GpioReader reader, GpioWriter writer, uint8_t debounceTicks = 5)
        : reader_(reader), writer_(writer), debounceThreshold_(debounceTicks) {}

    // Періодичне оновлення стану кнопки (викликається кожні 10 мс)
    void tick(const std::function<void()>& onPressAction = nullptr) {
        const bool rawPressed = (reader_() == 0); // Активний нуль (pull-up)

        if (rawPressed != lastRawState_) {
            lastRawState_ = rawPressed;
            counter_ = 0;
        } else if (counter_ < debounceThreshold_) {
            if (++counter_ == debounceThreshold_) {
                stableState_ = rawPressed;
                if (stableState_ && state_ == State::Released) {
                    state_ = State::Held;
                    ledState_ = !ledState_;
                    writer_(ledState_); // Перемикаємо стан світлодіода
                    if (onPressAction) {
                        onPressAction();
                    }
                } else if (!stableState_) {
                    state_ = State::Released;
                }
            }
        }
    }

    [[nodiscard]] bool isLedActive() const noexcept { return ledState_; }

private:
    GpioReader reader_;
    GpioWriter writer_;
    uint8_t debounceThreshold_;
    uint8_t counter_{0};
    bool lastRawState_{false};
    bool stableState_{false};
    bool ledState_{false};
    State state_{State::Released};
};
