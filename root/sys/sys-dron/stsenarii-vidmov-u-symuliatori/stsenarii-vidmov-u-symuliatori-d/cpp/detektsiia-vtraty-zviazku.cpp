#include <chrono>
#include <cstdint>
#include <optional>

class LinkWatchdog {
public:
    enum class State : uint8_t {
        Ok,
        DebounceHold,
        FailsafeActive
    };

    explicit LinkWatchdog(std::chrono::microseconds timeout = std::chrono::milliseconds(1500),
                         std::chrono::microseconds debounce = std::chrono::milliseconds(2000),
                         std::chrono::microseconds recovery = std::chrono::milliseconds(1000))
        : timeout_duration_(timeout),
          debounce_duration_(debounce),
          recovery_duration_(recovery),
          state_(State::Ok) {}

    void on_packet_received(std::chrono::microseconds now) noexcept {
        last_packet_time_ = now;
        if (state_ == State::DebounceHold) {
            if (!recovery_start_time_) {
                recovery_start_time_ = now;
            } else if (now - *recovery_start_time_ >= recovery_duration_) {
                state_ = State::Ok;
                loss_detected_time_.reset();
                recovery_start_time_.reset();
            }
        }
    }

    [[nodiscard]] State update(std::chrono::microseconds now) noexcept {
        const auto silence = now - last_packet_time_;

        switch (state_) {
        case State::Ok:
            if (silence > timeout_duration_) {
                state_ = State::DebounceHold;
                loss_detected_time_ = now;
                recovery_start_time_.reset();
            }
            break;

        case State::DebounceHold:
            if (silence > timeout_duration_) {
                if (loss_detected_time_ && (now - *loss_detected_time_ >= debounce_duration_)) {
                    state_ = State::FailsafeActive;
                }
            }
            break;

        case State::FailsafeActive:
            if (silence <= timeout_duration_) {
                if (!recovery_start_time_) {
                    recovery_start_time_ = now;
                } else if (now - *recovery_start_time_ >= recovery_duration_ * 3) {
                    state_ = State::Ok;
                    loss_detected_time_.reset();
                    recovery_start_time_.reset();
                }
            } else {
                recovery_start_time_.reset();
            }
            break;
        }

        return state_;
    }

    [[nodiscard]] bool is_failsafe_active() const noexcept {
        return state_ == State::FailsafeActive;
    }

private:
    std::chrono::microseconds timeout_duration_;
    std::chrono::microseconds debounce_duration_;
    std::chrono::microseconds recovery_duration_;

    std::chrono::microseconds last_packet_time_{0};
    std::optional<std::chrono::microseconds> loss_detected_time_;
    std::optional<std::chrono::microseconds> recovery_start_time_;
    State state_;
};
