#include <cstdint>
#include <array>
#include <optional>
#include <functional>

enum class EventType : uint8_t {
    None = 0,
    ButtonPress,
    ButtonRelease,
    ButtonShortClick,
    ButtonDoubleClick,
    ButtonLongPressStart,
    ButtonLongPressHold,
    ButtonRepeat,
    EncoderCW,
    EncoderCCW
};

struct InputEvent {
    uint8_t id{0};
    EventType type{EventType::None};
    uint16_t durationMs{0};
};

/* --- Безпечна шаблонна кільцева черга FIFO --- */
template <typename T, size_t Capacity>
class EventQueue {
public:
    constexpr EventQueue() = default;

    bool push(const T& item) noexcept {
        if (count_ >= Capacity) {
            return false;
        }
        buffer_[head_] = item;
        head_ = (head_ + 1) % Capacity;
        ++count_;
        return true;
    }

    std::optional<T> pop() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }
        T item = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        --count_;
        return item;
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }

private:
    std::array<T, Capacity> buffer_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
};

/* --- Об'єктно-орієнтований контролер кнопки з FSM --- */
class Button {
public:
    using PinReader = std::function<bool()>;

    enum class State : uint8_t {
        Idle,
        DebouncingPress,
        Pressed,
        DebouncingRelease,
        WaitDoubleClick,
        LongPress,
        Repeat
    };

    Button(uint8_t id, PinReader reader) noexcept
        : id_{id}, readPin_{std::move(reader)} {}

    template <size_t N>
    void tick(uint16_t tickMs, EventQueue<InputEvent, N>& queue) noexcept {
        const bool rawActive = !readPin_(); /* Active-low: 0 В означає активний стан */
        history_ = static_cast<uint8_t>((history_ << 1) | (rawActive ? 1 : 0));

        const bool isStableActive = (history_ == 0xFF);
        const bool isStableInactive = (history_ == 0x00);

        switch (state_) {
        case State::Idle:
            if (rawActive) {
                state_ = State::DebouncingPress;
                timerMs_ = 0;
            }
            break;

        case State::DebouncingPress:
            timerMs_ += tickMs;
            if (isStableActive) {
                state_ = State::Pressed;
                pressDurationMs_ = 0;
                queue.push({id_, EventType::ButtonPress, 0});
            } else if (timerMs_ > 30) {
                state_ = State::Idle;
            }
            break;

        case State::Pressed:
            pressDurationMs_ += tickMs;
            if (!rawActive) {
                state_ = State::DebouncingRelease;
                timerMs_ = 0;
            } else if (pressDurationMs_ >= LongPressThresholdMs) {
                state_ = State::LongPress;
                timerMs_ = 0;
                queue.push({id_, EventType::ButtonLongPressStart, pressDurationMs_});
            }
            break;

        case State::DebouncingRelease:
            timerMs_ += tickMs;
            if (isStableInactive) {
                queue.push({id_, EventType::ButtonRelease, pressDurationMs_});
                state_ = State::WaitDoubleClick;
                timerMs_ = 0;
            } else if (timerMs_ > 30) {
                state_ = State::Pressed;
            }
            break;

        case State::WaitDoubleClick:
            timerMs_ += tickMs;
            if (rawActive) {
                queue.push({id_, EventType::ButtonDoubleClick, timerMs_});
                state_ = State::DebouncingPress;
                timerMs_ = 0;
            } else if (timerMs_ >= DoubleClickTimeoutMs) {
                queue.push({id_, EventType::ButtonShortClick, pressDurationMs_});
                state_ = State::Idle;
            }
            break;

        case State::LongPress:
            pressDurationMs_ += tickMs;
            timerMs_ += tickMs;
            if (!rawActive) {
                state_ = State::Idle;
                queue.push({id_, EventType::ButtonRelease, pressDurationMs_});
            } else if (timerMs_ >= 100) {
                timerMs_ = 0;
                state_ = State::Repeat;
                queue.push({id_, EventType::ButtonLongPressHold, pressDurationMs_});
            }
            break;

        case State::Repeat:
            pressDurationMs_ += tickMs;
            timerMs_ += tickMs;
            if (!rawActive) {
                state_ = State::Idle;
                queue.push({id_, EventType::ButtonRelease, pressDurationMs_});
            } else if (timerMs_ >= RepeatRateMs) {
                timerMs_ = 0;
                queue.push({id_, EventType::ButtonRepeat, pressDurationMs_});
            }
            break;
        }
    }

private:
    static constexpr uint16_t LongPressThresholdMs = 800;
    static constexpr uint16_t DoubleClickTimeoutMs = 250;
    static constexpr uint16_t RepeatRateMs = 80;

    uint8_t id_{0};
    PinReader readPin_{};
    State state_{State::Idle};
    uint16_t timerMs_{0};
    uint16_t pressDurationMs_{0};
    uint8_t history_{0x00};
};

/* --- Декодер квадратурного енкодера на C++ --- */
class RotaryEncoder {
public:
    using PinReader = std::function<bool()>;

    RotaryEncoder(uint8_t id, PinReader readA, PinReader readB) noexcept
        : id_{id}, readA_{std::move(readA)}, readB_{std::move(readB)} {
        const uint8_t a = readA_() ? 1 : 0;
        const uint8_t b = readB_() ? 1 : 0;
        prevState_ = static_cast<uint8_t>((a << 1) | b);
    }

    template <size_t N>
    void tick(EventQueue<InputEvent, N>& queue) noexcept {
        const uint8_t a = readA_() ? 1 : 0;
        const uint8_t b = readB_() ? 1 : 0;
        const uint8_t currState = static_cast<uint8_t>((a << 1) | b);

        if (currState == prevState_) {
            return;
        }

        const uint8_t code = static_cast<uint8_t>((prevState_ << 2) | currState);
        const int8_t step = StateTable[code];
        prevState_ = currState;

        if (step != 0) {
            subSteps_ += step;
            if (subSteps_ >= 4) {
                subSteps_ = 0;
                queue.push({id_, EventType::EncoderCW, 1});
            } else if (subSteps_ <= -4) {
                subSteps_ = 0;
                queue.push({id_, EventType::EncoderCCW, 1});
            }
        }
    }

private:
    static constexpr std::array<int8_t, 16> StateTable = {
         0, -1,  1,  0,
         1,  0,  0, -1,
        -1,  0,  0,  1,
         0,  1, -1,  0
    };

    uint8_t id_{0};
    PinReader readA_{};
    PinReader readB_{};
    uint8_t prevState_{0};
    int8_t subSteps_{0};
};
