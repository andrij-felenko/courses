#include <cstdint>
#include <utility>

class I2cBusRecoveryFSM {
public:
    static constexpr uint8_t MaxRecoveryPulses = 9;
    static constexpr uint32_t MaxTimeoutTicks = 1000;

    enum class State {
        Idle,
        Busy,
        Timeout,
        Recovering,
        Error
    };

    I2cBusRecoveryFSM() noexcept { reset(); }

    void reset() noexcept {
        state_ = State::Idle;
        wait_ticks_ = 0;
        pulse_count_ = 0;
        sda_stuck_low_ = false;
    }

    void start_transaction() noexcept {
        state_ = State::Busy;
        wait_ticks_ = 0;
    }

    void complete_transaction() noexcept {
        state_ = State::Idle;
        wait_ticks_ = 0;
    }

    void tick(bool sda_is_high, [[maybe_unused]] bool scl_is_high) noexcept {
        switch (state_) {
        case State::Idle:
            wait_ticks_ = 0;
            break;

        case State::Busy:
            if (++wait_ticks_ > MaxTimeoutTicks) {
                state_ = State::Timeout;
            }
            break;

        case State::Timeout:
            if (!sda_is_high) {
                sda_stuck_low_ = true;
                pulse_count_ = 0;
                state_ = State::Recovering;
            } else {
                state_ = State::Error;
            }
            break;

        case State::Recovering:
            if (pulse_count_ < MaxRecoveryPulses) {
                pulse_count_++;
                if (sda_is_high) {
                    sda_stuck_low_ = false;
                    state_ = State::Idle;
                }
            } else {
                state_ = sda_is_high ? State::Idle : State::Error;
            }
            break;

        case State::Error:
            break;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] bool is_recovering() const noexcept { return state_ == State::Recovering; }

private:
    State state_{State::Idle};
    uint32_t wait_ticks_{0};
    uint8_t pulse_count_{0};
    bool sda_stuck_low_{false};
};
