#include <array>
#include <string_view>
#include <algorithm>
#include <numeric>
#include <optional>
#include <span>

namespace reflow {

enum class ReflowZone : uint8_t {
    Preheat,
    Soak,
    Reflow,
    Cooling,
    Finished
};

[[nodiscard]] constexpr std::string_view to_string(ReflowZone zone) noexcept {
    switch (zone) {
        case ReflowZone::Preheat:  return "PREHEAT";
        case ReflowZone::Soak:     return "SOAK";
        case ReflowZone::Reflow:   return "REFLOW";
        case ReflowZone::Cooling:  return "COOLING";
        case ReflowZone::Finished: return "FINISHED";
    }
    return "UNKNOWN";
}

struct ProfileLimits {
    double min_preheat_ramp{1.0};   // +1.0 C/s
    double max_preheat_ramp{3.0};   // +3.0 C/s
    double soak_temp_min{150.0};    // 150.0 C
    double soak_temp_max{200.0};    // 200.0 C
    double min_soak_time{60.0};     // 60.0 s
    double max_soak_time{120.0};    // 120.0 s
    double liquidus_temp{217.0};    // 217.0 C
    double min_tal_time{45.0};      // 45.0 s
    double max_tal_time{90.0};      // 90.0 s
    double min_peak_temp{235.0};    // 235.0 C
    double max_peak_temp{255.0};    // 255.0 C
    double max_cooling_ramp{-4.0};  // -4.0 C/s
};

struct UpdateResult {
    ReflowZone zone;
    double current_temp;
    double ramp_rate;
    double tal_seconds;
    bool has_violation;
};

template <size_t WindowSize = 5>
class ProfileAnalyzer {
public:
    explicit constexpr ProfileAnalyzer(ProfileLimits limits = {}) noexcept
        : limits_{limits} 
    {
        history_.fill(25.0);
    }

    [[nodiscard]] UpdateResult update(double raw_temp, double dt, double total_time) noexcept {
        current_temp_ = raw_temp;
        
        const double oldest = history_[history_idx_];
        history_[history_idx_] = raw_temp;
        history_idx_ = (history_idx_ + 1) % WindowSize;

        const double ramp_rate = (current_temp_ - oldest) / (WindowSize * dt);
        peak_temp_ = std::max(peak_temp_, current_temp_);

        if (current_temp_ >= limits_.liquidus_temp) {
            tal_seconds_ += dt;
        }

        switch (zone_) {
            case ReflowZone::Preheat:
                if (ramp_rate > limits_.max_preheat_ramp) {
                    has_violation_ = true;
                }
                if (current_temp_ >= limits_.soak_temp_min) {
                    zone_ = ReflowZone::Soak;
                    soak_start_sec_ = total_time;
                }
                break;

            case ReflowZone::Soak:
                if (current_temp_ >= limits_.liquidus_temp) {
                    zone_ = ReflowZone::Reflow;
                    soak_duration_sec_ = total_time - soak_start_sec_;
                    if (soak_duration_sec_ < limits_.min_soak_time ||
                        soak_duration_sec_ > limits_.max_soak_time) {
                        has_violation_ = true;
                    }
                }
                break;

            case ReflowZone::Reflow:
                if (current_temp_ < limits_.liquidus_temp && peak_temp_ >= limits_.min_peak_temp) {
                    zone_ = ReflowZone::Cooling;
                    if (tal_seconds_ < limits_.min_tal_time ||
                        tal_seconds_ > limits_.max_tal_time ||
                        peak_temp_ > limits_.max_peak_temp) {
                        has_violation_ = true;
                    }
                }
                break;

            case ReflowZone::Cooling:
                if (ramp_rate < limits_.max_cooling_ramp) {
                    has_violation_ = true;
                }
                if (current_temp_ <= 50.0) {
                    zone_ = ReflowZone::Finished;
                }
                break;

            case ReflowZone::Finished:
                break;
        }

        return UpdateResult{
            .zone = zone_,
            .current_temp = current_temp_,
            .ramp_rate = ramp_rate,
            .tal_seconds = tal_seconds_,
            .has_violation = has_violation_
        };
    }

    [[nodiscard]] constexpr double peak_temperature() const noexcept { return peak_temp_; }
    [[nodiscard]] constexpr double tal_duration() const noexcept { return tal_seconds_; }
    [[nodiscard]] constexpr ReflowZone current_zone() const noexcept { return zone_; }

private:
    ProfileLimits limits_;
    ReflowZone zone_{ReflowZone::Preheat};
    double current_temp_{25.0};
    double peak_temp_{25.0};
    double tal_seconds_{0.0};
    double soak_start_sec_{0.0};
    double soak_duration_sec_{0.0};
    bool has_violation_{false};
    std::array<double, WindowSize> history_{};
    size_t history_idx_{0};
};

} // namespace reflow
