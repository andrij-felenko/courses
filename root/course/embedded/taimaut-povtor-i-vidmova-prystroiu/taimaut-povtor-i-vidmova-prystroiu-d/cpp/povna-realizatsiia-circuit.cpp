#include <cstdint>
#include <chrono>

extern uint32_t platform_get_millis() noexcept;

class CircuitBreaker {
public:
    enum class State : uint8_t {
        Closed = 0,
        Open,
        HalfOpen
    };

    constexpr CircuitBreaker(uint8_t threshold, std::chrono::milliseconds cooldown) noexcept
        : failure_threshold_(threshold),
          cooldown_period_ms_(static_cast<uint32_t>(cooldown.count())) {}

    [[nodiscard]] bool allow_transaction() noexcept {
        const uint32_t now = platform_get_millis();

        switch (state_) {
            case State::Closed:
                return true;

            case State::Open:
                if ((now - state_change_time_ms_) >= cooldown_period_ms_) {
                    state_ = State::HalfOpen;
                    return true;
                }
                return false;

            case State::HalfOpen:
                return false;

            default:
                return false;
        }
    }

    void report_success() noexcept {
        failure_count_ = 0;
        if (state_ != State::Closed) {
            state_ = State::Closed;
            state_change_time_ms_ = platform_get_millis();
        }
    }

    void report_failure() noexcept {
        ++total_errors_;
        const uint32_t now = platform_get_millis();

        if (state_ == State::HalfOpen) {
            state_ = State::Open;
            state_change_time_ms_ = now;
        } else if (state_ == State::Closed) {
            if (++failure_count_ >= failure_threshold_) {
                state_ = State::Open;
                state_change_time_ms_ = now;
            }
        }
    }

    [[nodiscard]] constexpr State state() const noexcept { return state_; }
    [[nodiscard]] constexpr uint32_t total_errors() const noexcept { return total_errors_; }

private:
    State    state_{State::Closed};
    uint8_t  failure_count_{0};
    uint8_t  failure_threshold_{5};
    uint32_t state_change_time_ms_{0};
    uint32_t cooldown_period_ms_{5000};
    uint32_t total_errors_{0};
};
