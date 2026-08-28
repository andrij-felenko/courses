#include <cstdint>
#include <cstddef>
#include <bitset>
#include <array>
#include <optional>
#include <span>

namespace safety {

enum class SensorBit : size_t {
    DoorClosed    = 0, // Кінцевик кришки (NC): 1 = закрита
    PressureOk    = 1, // Реле тиску: 1 = тиск у нормі
    WaterFlowOk   = 2, // Датчик протоку: 1 = потік достатній
    TempSafe      = 3, // Термостат безпеки: 1 = температура < 80C
    EstopNormal   = 4, // Кнопка E-Stop (NC): 1 = не натиснута
    Count         = 5
};

using SensorBitmap = std::bitset<static_cast<size_t>(SensorBit::Count)>;

enum class SystemState {
    Idle,
    Preparing,
    Heating,
    Tripped
};

struct ChannelConfig {
    SensorBit bit;
    uint32_t stable_delay_ms;
};

class InterlockChannel {
public:
    constexpr InterlockChannel(SensorBit bit, uint32_t delay_ms) noexcept
        : bit_(bit), delay_ms_(delay_ms) {}

    void update(bool raw_val, uint32_t now_ms) noexcept {
        if (raw_val != last_raw_val_) {
            last_raw_val_ = raw_val;
            last_change_ms_ = now_ms;
        }

        if ((now_ms - last_change_ms_) >= delay_ms_) {
            qualified_val_ = last_raw_val_;
        }
    }

    [[nodiscard]] constexpr bool is_qualified() const noexcept { return qualified_val_; }
    [[nodiscard]] constexpr SensorBit bit() const noexcept { return bit_; }

private:
    SensorBit bit_;
    uint32_t delay_ms_{0};
    uint32_t last_change_ms_{0};
    bool last_raw_val_{false};
    bool qualified_val_{false};
};

struct StateRule {
    SensorBitmap permissive_req;     // Обов'язкові біти = 1 для старту
    SensorBitmap permissive_forbid;  // Заборонені біти = 0 для старту
    SensorBitmap inhibit_required;   // Біти, зникнення яких викликає Trip
};

class InterlockManager {
public:
    InterlockManager() noexcept {
        channels_[0] = InterlockChannel(SensorBit::DoorClosed, 50);
        channels_[1] = InterlockChannel(SensorBit::PressureOk, 200);
        channels_[2] = InterlockChannel(SensorBit::WaterFlowOk, 500);
        channels_[3] = InterlockChannel(SensorBit::TempSafe, 100);
        channels_[4] = InterlockChannel(SensorBit::EstopNormal, 10);
    }

    void update_inputs(const SensorBitmap& raw_inputs, uint32_t now_ms) noexcept {
        SensorBitmap current;
        for (auto& ch : channels_) {
            bool raw = raw_inputs.test(static_cast<size_t>(ch.bit()));
            ch.update(raw, now_ms);
            if (ch.is_qualified()) {
                current.set(static_cast<size_t>(ch.bit()));
            }
        }
        qualified_bitmap_ = current;
    }

    [[nodiscard]] bool can_enter_state(SystemState target, SensorBitmap* missing_out = nullptr) const noexcept {
        const auto& rule = get_rule(target);

        // Перевірка необхідних бітів: (req & ~present) мусить бути порожнім
        SensorBitmap missing = rule.permissive_req & ~qualified_bitmap_;
        SensorBitmap forbidden = qualified_bitmap_ & rule.permissive_forbid;

        if (missing.any() || forbidden.any()) {
            if (missing_out) {
                *missing_out = missing | forbidden;
            }
            return false;
        }
        return true;
    }

    // Безперервний нагляд активного стану: повертає причину зриву, якщо інваріант порушено
    [[nodiscard]] std::optional<SensorBitmap> check_active_invariants() noexcept {
        if (state_ == SystemState::Idle || state_ == SystemState::Tripped) {
            return std::nullopt;
        }

        const auto& rule = get_rule(state_);
        SensorBitmap lost_signals = rule.inhibit_required & ~qualified_bitmap_;

        if (lost_signals.any()) {
            trip_latch_cause_ = lost_signals;
            state_ = SystemState::Tripped;
            return lost_signals;
        }
        return std::nullopt;
    }

    bool trip_reset() noexcept {
        if (state_ != SystemState::Tripped) {
            return false;
        }

        if (qualified_bitmap_.test(static_cast<size_t>(SensorBit::EstopNormal))) {
            trip_latch_cause_.reset();
            state_ = SystemState::Idle;
            return true;
        }
        return false;
    }

    [[nodiscard]] SystemState current_state() const noexcept { return state_; }
    [[nodiscard]] SensorBitmap trip_cause() const noexcept { return trip_latch_cause_; }

private:
    [[nodiscard]] static constexpr StateRule get_rule(SystemState st) noexcept {
        StateRule rule{};
        switch (st) {
            case SystemState::Preparing:
                rule.permissive_req.set(static_cast<size_t>(SensorBit::DoorClosed));
                rule.permissive_req.set(static_cast<size_t>(SensorBit::EstopNormal));
                rule.inhibit_required = rule.permissive_req;
                break;
            case SystemState::Heating:
                rule.permissive_req.set(static_cast<size_t>(SensorBit::DoorClosed));
                rule.permissive_req.set(static_cast<size_t>(SensorBit::PressureOk));
                rule.permissive_req.set(static_cast<size_t>(SensorBit::WaterFlowOk));
                rule.permissive_req.set(static_cast<size_t>(SensorBit::TempSafe));
                rule.permissive_req.set(static_cast<size_t>(SensorBit::EstopNormal));
                rule.inhibit_required = rule.permissive_req;
                break;
            case SystemState::Idle:
            case SystemState::Tripped:
            default:
                break;
        }
        return rule;
    }

    std::array<InterlockChannel, static_cast<size_t>(SensorBit::Count)> channels_{};
    SensorBitmap qualified_bitmap_{};
    SensorBitmap trip_latch_cause_{};
    SystemState state_{SystemState::Idle};
};

} // namespace safety
