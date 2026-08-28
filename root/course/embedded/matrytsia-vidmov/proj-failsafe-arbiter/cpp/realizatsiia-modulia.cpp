#include <cstdint>
#include <chrono>
#include <span>

namespace autopilot::failsafe {

enum class Action : uint8_t {
    None = 0,
    Warn,
    AltHold,
    ReturnToLaunch,
    Land,
    Terminate
};

struct Config {
    std::chrono::milliseconds rc_timeout{1500};
    std::chrono::milliseconds gcs_timeout{5000};
    std::chrono::milliseconds gnss_timeout{3000};
    std::chrono::milliseconds batt_debounce{1000};
    std::chrono::milliseconds geofence_debounce{500};
};

class DebounceTimer {
public:
    void update(bool condition, std::chrono::milliseconds now,
                std::chrono::milliseconds threshold, uint32_t& mask, Fault fault) noexcept
    {
        const uint32_t flag = to_mask(fault);
        if (condition) {
            if (start_time_.count() == 0) {
                start_time_ = now;
            }
            if ((now - start_time_) >= threshold) {
                mask |= flag;
            }
        } else {
            start_time_ = std::chrono::milliseconds{0};
            mask &= ~flag;
        }
    }

private:
    std::chrono::milliseconds start_time_{0};
};

class Arbiter {
public:
    explicit constexpr Arbiter(Config cfg) noexcept : cfg_(cfg) {}

    [[nodiscard]] Action evaluate(uint32_t raw_faults, std::chrono::milliseconds now) noexcept {
        // Оновлення таймерів гістерезису
        rc_timer_.update((raw_faults & to_mask(Fault::RcLost)) != 0, now, cfg_.rc_timeout, confirmed_mask_, Fault::RcLost);
        gcs_timer_.update((raw_faults & to_mask(Fault::GcsLost)) != 0, now, cfg_.gcs_timeout, confirmed_mask_, Fault::GcsLost);
        gnss_timer_.update((raw_faults & to_mask(Fault::GnssGlitch)) != 0, now, cfg_.gnss_timeout, confirmed_mask_, Fault::GnssGlitch);
        batt_low_timer_.update((raw_faults & to_mask(Fault::BatteryLow)) != 0, now, cfg_.batt_debounce, confirmed_mask_, Fault::BatteryLow);
        batt_crit_timer_.update((raw_faults & to_mask(Fault::BatteryCrit)) != 0, now, cfg_.batt_debounce, confirmed_mask_, Fault::BatteryCrit);
        fence_timer_.update((raw_faults & to_mask(Fault::Geofence)) != 0, now, cfg_.geofence_debounce, confirmed_mask_, Fault::Geofence);

        if (raw_faults & to_mask(Fault::ActuatorFail)) confirmed_mask_ |= to_mask(Fault::ActuatorFail);
        if (raw_faults & to_mask(Fault::AttitudeLoss)) confirmed_mask_ |= to_mask(Fault::AttitudeLoss);

        return resolve_conflicts();
    }

    [[nodiscard]] uint32_t confirmed_faults() const noexcept { return confirmed_mask_; }

private:
    [[nodiscard]] bool has_fault(Fault f) const noexcept {
        return (confirmed_mask_ & to_mask(f)) != 0;
    }

    [[nodiscard]] Action resolve_conflicts() noexcept {
        if (has_fault(Fault::AttitudeLoss)) {
            return Action::Terminate;
        }
        if (has_fault(Fault::BatteryCrit)) {
            return Action::Land;
        }
        if (has_fault(Fault::Geofence)) {
            return has_fault(Fault::GnssGlitch) ? Action::Land : Action::ReturnToLaunch;
        }
        if (has_fault(Fault::RcLost)) {
            return has_fault(Fault::GnssGlitch) ? Action::Land : Action::ReturnToLaunch;
        }
        if (has_fault(Fault::GnssGlitch)) {
            return Action::AltHold;
        }
        if (has_fault(Fault::BatteryLow)) {
            return has_fault(Fault::GnssGlitch) ? Action::Land : Action::ReturnToLaunch;
        }
        return Action::None;
    }

    Config cfg_;
    uint32_t confirmed_mask_{0};
    DebounceTimer rc_timer_;
    DebounceTimer gcs_timer_;
    DebounceTimer gnss_timer_;
    DebounceTimer batt_low_timer_;
    DebounceTimer batt_crit_timer_;
    DebounceTimer fence_timer_;
};

} // namespace autopilot::failsafe
