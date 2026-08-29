#include "uav/return_budget.hpp"

#include <cstdint>
#include <expected>
#include <string_view>
#include <utility>

namespace uav::nav {

enum class RtlReason : std::uint8_t {
    BatteryPointOfNoReturn,
    CrosswindLimit,
    HeadwindLimit
};

// Гачки автопілота: EKF, failsafe, журнал Flash і шина телеметрії.
// Реалізовані поза модулем — тут лише їхній контракт.
namespace autopilot {
Telemetry readTelemetry();
void triggerRtl(RtlReason reason);
void triggerEmergencyLand(RtlReason reason);
void postWarning(std::string_view text);
void postCritical(std::string_view text);
void logEvent(std::string_view tag, float value);
} // namespace autopilot

// Періодична задача навігації: 2 Гц у польотному циклі.
class NavigationTask {
public:
    [[nodiscard]] static std::expected<NavigationTask, Error> create(const Config& config) noexcept {
        auto estimator = Estimator::create(config);
        if (!estimator) {
            return std::unexpected{estimator.error()};
        }
        return NavigationTask{std::move(*estimator)};
    }

    void onPeriodicUpdate(float dt_sec) noexcept {
        const Telemetry telemetry = autopilot::readTelemetry();
        const auto budget = estimator_.update(telemetry, dt_sec);
        since_warning_s_ += dt_sec;

        if (!budget) {
            handleError(budget.error());
            return;
        }
        bad_frames_ = 0;

        if (budget->rtl_mandatory) {
            engageReturn(*budget);
        } else if (budget->state == State::Caution && since_warning_s_ >= 5.0f) {
            since_warning_s_ = 0.0f;
            autopilot::postWarning("PNR approaching: wind reserve critical");
        }
    }

private:
    explicit NavigationTask(Estimator estimator) noexcept : estimator_{std::move(estimator)} {}

    void handleError(Error error) noexcept {
        switch (error) {
            case Error::CrosswindLimit:
                autopilot::logEvent(toString(error), 0.0f);
                autopilot::postCritical("Crosswind exceeds airspeed: landing here");
                autopilot::triggerEmergencyLand(RtlReason::CrosswindLimit);
                return;
            case Error::HeadwindTooHigh:
                autopilot::logEvent(toString(error), 0.0f);
                autopilot::postCritical("Headwind stops return: landing here");
                autopilot::triggerEmergencyLand(RtlReason::HeadwindLimit);
                return;
            case Error::InvalidTelemetry:
            case Error::InvalidConfig:
                // Один зіпсований кадр — не подія; десять поспіль (5 с) — відмова давачів.
                if (++bad_frames_ >= 10) {
                    bad_frames_ = 0;
                    autopilot::postCritical("Return budget estimation failed: invalid state");
                }
                return;
        }
    }

    void engageReturn(const Budget& budget) noexcept {
        if (budget.state == State::EmergencyLand) {
            autopilot::logEvent("PACK_SAG_V", budget.projected_sag_voltage_v);
            autopilot::postCritical("Battery sag below cutoff: landing here");
            autopilot::triggerEmergencyLand(RtlReason::BatteryPointOfNoReturn);
            return;
        }
        if (!rtl_engaged_) {
            rtl_engaged_ = true;
            autopilot::logEvent("PNR_RETURN_WH", budget.e_return_total_wh);
            autopilot::logEvent("PNR_USABLE_WH", budget.e_usable_compensated_wh);
            autopilot::postCritical("Point of no return: RTL engaged");
            autopilot::triggerRtl(RtlReason::BatteryPointOfNoReturn);
        }
    }

    Estimator estimator_;
    float since_warning_s_{0.0f};
    std::uint32_t bad_frames_{0};
    bool rtl_engaged_{false};
};

} // namespace uav::nav
