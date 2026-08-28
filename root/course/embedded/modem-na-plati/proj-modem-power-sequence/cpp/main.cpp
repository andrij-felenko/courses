#include <chrono>
#include <cstdint>
#include <expected>
#include <functional>

enum class ModemState : uint8_t {
    Off,
    PulsingPwrkey,
    WaitingStatus,
    Ready,
    Sleep,
    ResetRecovery,
    Fault
};

enum class ModemError : uint8_t {
    BootTimeout,
    HardFault,
    InvalidState
};

struct ModemHalCallbacks {
    std::function<void(bool active_low)> set_pwrkey;
    std::function<void(bool active_low)> set_reset;
    std::function<void(bool high_sleep)> set_dtr;
    std::function<bool()> get_status;
};

class CellularModemHW {
public:
    using Milliseconds = std::chrono::milliseconds;

    explicit CellularModemHW(ModemHalCallbacks callbacks)
        : hal_(std::move(callbacks)),
          state_(ModemState::Off),
          pwrkey_pulse_(1000),
          boot_timeout_(5000),
          retry_count_(0),
          ri_pending_(false) {
        hal_.set_pwrkey(false);
        hal_.set_reset(false);
        hal_.set_dtr(false);
    }

    void on_ring_indicator_interrupt() noexcept {
        ri_pending_ = true;
    }

    std::expected<void, ModemError> request_power_on(Milliseconds now) {
        if (state_ == ModemState::Off || state_ == ModemState::Fault) {
            hal_.set_pwrkey(true);
            timer_start_ = now;
            state_ = ModemState::PulsingPwrkey;
            return {};
        }
        return std::unexpected(ModemError::InvalidState);
    }

    void set_sleep_mode(bool enable) {
        if (state_ == ModemState::Ready && enable) {
            hal_.set_dtr(true);
            state_ = ModemState::Sleep;
        } else if (state_ == ModemState::Sleep && !enable) {
            hal_.set_dtr(false);
            state_ = ModemState::Ready;
        }
    }

    void poll(Milliseconds now) {
        switch (state_) {
            case ModemState::PulsingPwrkey:
                if (now - timer_start_ >= pwrkey_pulse_) {
                    hal_.set_pwrkey(false);
                    timer_start_ = now;
                    state_ = ModemState::WaitingStatus;
                }
                break;

            case ModemState::WaitingStatus:
                if (hal_.get_status()) {
                    state_ = ModemState::Ready;
                    retry_count_ = 0;
                } else if (now - timer_start_ >= boot_timeout_) {
                    if (retry_count_++ < 3) {
                        hal_.set_reset(true);
                        timer_start_ = now;
                        state_ = ModemState::ResetRecovery;
                    } else {
                        state_ = ModemState::Fault;
                    }
                }
                break;

            case ModemState::ResetRecovery:
                if (now - timer_start_ >= Milliseconds(250)) {
                    hal_.set_reset(false);
                    timer_start_ = now;
                    state_ = ModemState::WaitingStatus;
                }
                break;

            case ModemState::Sleep:
                if (ri_pending_) {
                    ri_pending_ = false;
                    set_sleep_mode(false);
                }
                break;

            case ModemState::Ready:
            case ModemState::Off:
            case ModemState::Fault:
                break;
        }
    }

    [[nodiscard]] ModemState current_state() const noexcept {
        return state_;
    }

    [[nodiscard]] bool is_ready() const noexcept {
        return state_ == ModemState::Ready;
    }

private:
    ModemHalCallbacks hal_;
    ModemState state_;
    Milliseconds timer_start_{0};
    Milliseconds pwrkey_pulse_;
    Milliseconds boot_timeout_;
    uint8_t retry_count_;
    bool ri_pending_;
};
