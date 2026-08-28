// power_sequencer.hpp - C++20 modern embedded implementation
#pragma once

#include <cstdint>
#include <concepts>
#include <expected>
#include <chrono>

namespace power {

enum class State : uint8_t {
    Off = 0,
    WaitCorePgood,
    EnableIo,
    WaitIoPgood,
    EnablePeriph,
    Ready,
    Fault
};

enum class Error : uint8_t {
    None = 0,
    CoreTimeout,
    IoTimeout,
    BrownoutDetected,
    OvercurrentFault
};

struct Config {
    std::chrono::milliseconds core_pg_timeout{50};
    std::chrono::milliseconds io_pg_timeout{50};
    std::chrono::milliseconds periph_stabilize_delay{10};
};

template <typename HardwareInterface>
concept PowerHardware = requires(HardwareInterface hw, bool en) {
    { hw.set_core_en(en) } -> std::same_as<void>;
    { hw.set_io_en(en) } -> std::same_as<void>;
    { hw.set_periph_en(en) } -> std::same_as<void>;
    { hw.read_core_pgood() } -> std::same_as<bool>;
    { hw.read_io_pgood() } -> std::same_as<bool>;
    { hw.read_fault_status() } -> std::same_as<bool>;
};

template <PowerHardware Hw>
class PowerSequencer {
public:
    explicit PowerSequencer(Hw& hardware, Config config = {})
        : hw_{hardware}, cfg_{config}, state_{State::Off}, error_{Error::None}, timer_ms_{0} {}

    void start_power_up() noexcept {
        if (state_ == State::Off || state_ == State::Fault) {
            error_ = Error::None;
            timer_ms_ = 0;
            hw_.set_periph_en(false);
            hw_.set_io_en(false);
            hw_.set_core_en(true);
            state_ = State::WaitCorePgood;
        }
    }

    void shutdown() noexcept {
        hw_.set_periph_en(false);
        hw_.set_io_en(false);
        hw_.set_core_en(false);
        state_ = State::Off;
    }

    void process_tick(std::chrono::milliseconds elapsed) noexcept {
        timer_ms_ += elapsed.count();

        if (hw_.read_fault_status() && state_ != State::Fault && state_ != State::Off) {
            trigger_fault(Error::OvercurrentFault);
            return;
        }

        switch (state_) {
            case State::WaitCorePgood:
                if (hw_.read_core_pgood()) {
                    hw_.set_io_en(true);
                    timer_ms_ = 0;
                    state_ = State::WaitIoPgood;
                } else if (timer_ms_ >= cfg_.core_pg_timeout.count()) {
                    trigger_fault(Error::CoreTimeout);
                }
                break;

            case State::WaitIoPgood:
                if (hw_.read_io_pgood()) {
                    timer_ms_ = 0;
                    state_ = State::EnablePeriph;
                } else if (timer_ms_ >= cfg_.io_pg_timeout.count()) {
                    trigger_fault(Error::IoTimeout);
                }
                break;

            case State::EnablePeriph:
                if (timer_ms_ >= cfg_.periph_stabilize_delay.count()) {
                    hw_.set_periph_en(true);
                    state_ = State::Ready;
                }
                break;

            case State::Ready:
                if (!hw_.read_core_pgood() || !hw_.read_io_pgood()) {
                    trigger_fault(Error::BrownoutDetected);
                }
                break;

            case State::Off:
            case State::Fault:
            default:
                break;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] Error error() const noexcept { return error_; }
    [[nodiscard]] bool is_ready() const noexcept { return state_ == State::Ready; }

private:
    void trigger_fault(Error err) noexcept {
        error_ = err;
        state_ = State::Fault;
        shutdown();
    }

    Hw& hw_;
    Config cfg_;
    State state_;
    Error error_;
    uint32_t timer_ms_;
};

} // namespace power
