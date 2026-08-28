// TelemetryThrottler.hpp — Ідіоматична C++20 реалізація контролера частот
#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <functional>
#include <optional>
#include <span>

namespace mavlink::telemetry {

enum class State : uint8_t {
    Normal = 0,
    Degraded,
    Critical
};

struct StreamSetting {
    uint32_t msg_id{0};
    int32_t  interval_us{-1}; // -1 = вимкнено, >0 = період у мкс
};

class TelemetryThrottler {
public:
    using Milliseconds = std::chrono::milliseconds;
    using SendCallback = std::function<void(uint32_t msg_id, int32_t interval_us)>;

    explicit TelemetryThrottler(SendCallback sender)
        : send_command_(std::move(sender)) {}

    void on_radio_status(uint8_t txbuf_pct, uint8_t packet_loss_pct) noexcept {
        // Експоненційне згладжування заповнення вихідного FIFO модема
        txbuf_smooth_ = static_cast<uint8_t>((txbuf_smooth_ * 7 + txbuf_pct * 3) / 10);
        packet_loss_pct_ = packet_loss_pct;
    }

    void update(Milliseconds now) {
        auto next_state = evaluate_next_state(now);

        if (next_state != current_state_ || force_reapply_) {
            current_state_ = next_state;
            force_reapply_ = false;
            apply_current_profile();
        }
    }

    [[nodiscard]] State current_state() const noexcept { return current_state_; }
    [[nodiscard]] uint8_t smoothed_txbuf() const noexcept { return txbuf_smooth_; }

private:
    static constexpr std::array<StreamSetting, 6> kProfileNormal{{
        {30,   20'000},  // ATTITUDE (50 Гц)
        {33,  100'000},  // GLOBAL_POSITION_INT (10 Гц)
        {74,  100'000},  // VFR_HUD (10 Гц)
        {24,  200'000},  // GPS_RAW_INT (5 Гц)
        {1,   500'000},  // SYS_STATUS (2 Гц)
        {0,  1'000'000}  // HEARTBEAT (1 Гц)
    }};

    static constexpr std::array<StreamSetting, 6> kProfileDegraded{{
        {30,   66'666},  // ATTITUDE (15 Гц)
        {33,  250'000},  // GLOBAL_POSITION_INT (4 Гц)
        {74,  500'000},  // VFR_HUD (2 Гц)
        {24,  500'000},  // GPS_RAW_INT (2 Гц)
        {1,  1'000'000},  // SYS_STATUS (1 Гц)
        {0,  1'000'000}  // HEARTBEAT (1 Гц)
    }};

    static constexpr std::array<StreamSetting, 6> kProfileCritical{{
        {30,   200'000}, // ATTITUDE (5 Гц)
        {33, 1'000'000}, // GLOBAL_POSITION_INT (1 Гц)
        {74,        -1}, // VFR_HUD (Вимкнено)
        {24, 1'000'000}, // GPS_RAW_INT (1 Гц)
        {1,  1'000'000}, // SYS_STATUS (1 Гц)
        {0,  1'000'000}  // HEARTBEAT (1 Гц)
    }};

    State evaluate_next_state(Milliseconds now) noexcept {
        // 1. Аварійний перехід униз (Downgrade без затримки)
        if (txbuf_smooth_ > 85 || packet_loss_pct_ > 35) {
            recovery_start_time_.reset();
            return State::Critical;
        }
        if (txbuf_smooth_ > 60 || packet_loss_pct_ > 15) {
            if (current_state_ == State::Normal) {
                recovery_start_time_.reset();
                return State::Degraded;
            }
        }

        // 2. Ступінчасте відновлення вгору (Upgrade з 5-секундним гістерезисом)
        if (current_state_ == State::Critical && txbuf_smooth_ < 50 && packet_loss_pct_ < 10) {
            return check_recovery(now, State::Degraded);
        }
        if (current_state_ == State::Degraded && txbuf_smooth_ < 30 && packet_loss_pct_ < 5) {
            return check_recovery(now, State::Normal);
        }

        recovery_start_time_.reset();
        return current_state_;
    }

    State check_recovery(Milliseconds now, State target_state) noexcept {
        if (!recovery_start_time_.has_value()) {
            recovery_start_time_ = now;
            return current_state_;
        }
        if (now - *recovery_start_time_ >= std::chrono::seconds(5)) {
            recovery_start_time_.reset();
            return target_state;
        }
        return current_state_;
    }

    void apply_current_profile() {
        std::span<const StreamSetting> profile{};
        switch (current_state_) {
            case State::Normal:   profile = kProfileNormal; break;
            case State::Degraded: profile = kProfileDegraded; break;
            case State::Critical: profile = kProfileCritical; break;
        }

        for (const auto& item : profile) {
            if (send_command_) {
                send_command_(item.msg_id, item.interval_us);
            }
        }
    }

    SendCallback send_command_;
    State current_state_{State::Normal};
    bool force_reapply_{true};
    uint8_t txbuf_smooth_{0};
    uint8_t packet_loss_pct_{0};
    std::optional<Milliseconds> recovery_start_time_{std::nullopt};
};

} // namespace mavlink::telemetry
