#include <cstdint>
#include <cmath>
#include <string_view>
#include <optional>
#include <expected>

enum class FlightMode : uint8_t {
    Manual = 0,
    Stabilize,
    AltHold,
    PosHold,
    Auto,
    Guided,
    RTL,
    Land,
    EmergencyLand,
    Terminate
};

enum class TransitionError : uint8_t {
    NoGpsFix,
    BadHdop,
    EkfUnhealthy,
    NoMissionLoaded,
    NoHomePosition,
    ThrottleMismatch,
    FailsafeActive,
    InvalidMode
};

struct TelemetrySnapshot {
    bool armed{false};
    bool in_air{false};
    uint8_t gps_fix_type{0};      // 3: 3D Fix
    uint8_t gps_num_sats{0};
    float gps_hdop{99.0f};
    float gps_vdop{99.0f};
    bool ekf_pos_horiz_valid{false};
    bool ekf_pos_vert_valid{false};
    float ekf_innov_pos{1.0f};
    bool compass_healthy{false};
    uint16_t mission_item_count{0};
    bool home_position_set{false};
    float current_throttle{0.0f}; // 0.0f - 1.0f
    float stick_throttle{0.0f};   // 0.0f - 1.0f
    float vertical_velocity{0.0f}; // м/с
    bool rc_link_lost{false};
    bool gcs_link_lost{false};
    uint8_t battery_failsafe_stage{0}; // 0: OK, 1: Warning, 2: Critical
    bool hardware_kill_switch{false};
};

struct LandDetectorState {
    bool ground_contact{false};
    bool landed{false};
    uint32_t contact_start_ms{0};
};

class FlightModeFSM {
public:
    FlightModeFSM() = default;

    [[nodiscard]] FlightMode current_mode() const noexcept { return current_mode_; }
    [[nodiscard]] FlightMode previous_mode() const noexcept { return previous_mode_; }
    [[nodiscard]] bool is_failsafe_locked() const noexcept { return failsafe_locked_; }
    [[nodiscard]] bool is_landed() const noexcept { return land_detector_.landed; }

    // Запит на перемикання режиму зі строгою перевіркою охоронців
    std::expected<void, TransitionError> request_mode(FlightMode target, const TelemetrySnapshot& t, uint32_t now_ms) noexcept {
        if (failsafe_locked_ && target != FlightMode::Stabilize) {
            return std::unexpected(TransitionError::FailsafeActive);
        }

        if (target == current_mode_) {
            return {};
        }

        if (!check_throttle_matching(current_mode_, target, t)) {
            return std::unexpected(TransitionError::ThrottleMismatch);
        }

        auto guard_result = verify_guard(target, t);
        if (!guard_result.has_value()) {
            return std::unexpected(guard_result.error());
        }

        perform_transition(target, now_ms);
        failsafe_locked_ = false;
        return {};
    }

    // Періодичне оновлення логіки детектора посадки, арбітражу та деградації (50-100 Гц)
    void update(const TelemetrySnapshot& t, uint32_t now_ms) noexcept {
        update_land_detector(t, now_ms);

        if (handle_preemption(t, now_ms)) {
            return;
        }

        if (t.in_air) {
            handle_graceful_degradation(t, now_ms);
        }
    }

    static constexpr std::string_view mode_name(FlightMode mode) noexcept {
        switch (mode) {
            case FlightMode::Manual:        return "MANUAL";
            case FlightMode::Stabilize:     return "STABILIZE";
            case FlightMode::AltHold:       return "ALT_HOLD";
            case FlightMode::PosHold:       return "POS_HOLD";
            case FlightMode::Auto:          return "AUTO";
            case FlightMode::Guided:        return "GUIDED";
            case FlightMode::RTL:           return "RTL";
            case FlightMode::Land:          return "LAND";
            case FlightMode::EmergencyLand: return "EMERGENCY_LAND";
            case FlightMode::Terminate:     return "TERMINATE";
        }
        return "UNKNOWN";
    }

private:
    FlightMode current_mode_{FlightMode::Stabilize};
    FlightMode previous_mode_{FlightMode::Stabilize};
    uint32_t last_transition_ms_{0};
    bool failsafe_locked_{false};
    LandDetectorState land_detector_{};

    void perform_transition(FlightMode new_mode, uint32_t now_ms) noexcept {
        previous_mode_ = current_mode_;
        current_mode_ = new_mode;
        last_transition_ms_ = now_ms;
    }

    [[nodiscard]] static std::expected<void, TransitionError> guard_pos_hold(const TelemetrySnapshot& t) noexcept {
        if (t.gps_fix_type < 3 || t.gps_num_sats < 6) {
            return std::unexpected(TransitionError::NoGpsFix);
        }
        if (t.gps_hdop > 1.5f || t.gps_vdop > 2.0f) {
            return std::unexpected(TransitionError::BadHdop);
        }
        if (!t.ekf_pos_horiz_valid || !t.compass_healthy || t.ekf_innov_pos > 0.3f) {
            return std::unexpected(TransitionError::EkfUnhealthy);
        }
        return {};
    }

    [[nodiscard]] static std::expected<void, TransitionError> guard_auto(const TelemetrySnapshot& t) noexcept {
        auto pos_guard = guard_pos_hold(t);
        if (!pos_guard.has_value()) {
            return pos_guard;
        }
        if (t.mission_item_count == 0) {
            return std::unexpected(TransitionError::NoMissionLoaded);
        }
        if (!t.home_position_set) {
            return std::unexpected(TransitionError::NoHomePosition);
        }
        return {};
    }

    [[nodiscard]] static std::expected<void, TransitionError> guard_rtl(const TelemetrySnapshot& t) noexcept {
        if (!t.home_position_set) {
            return std::unexpected(TransitionError::NoHomePosition);
        }
        if (!t.ekf_pos_horiz_valid && !t.ekf_pos_vert_valid) {
            return std::unexpected(TransitionError::EkfUnhealthy);
        }
        return {};
    }

    [[nodiscard]] std::expected<void, TransitionError> verify_guard(FlightMode target, const TelemetrySnapshot& t) const noexcept {
        switch (target) {
            case FlightMode::Manual:
            case FlightMode::Stabilize:
                return {};
            case FlightMode::AltHold:
                if (!t.ekf_pos_vert_valid) {
                    return std::unexpected(TransitionError::EkfUnhealthy);
                }
                return {};
            case FlightMode::PosHold:
            case FlightMode::Guided:
                return guard_pos_hold(t);
            case FlightMode::Auto:
                return guard_auto(t);
            case FlightMode::RTL:
                return guard_rtl(t);
            case FlightMode::Land:
            case FlightMode::EmergencyLand:
            case FlightMode::Terminate:
                return {};
        }
        return std::unexpected(TransitionError::InvalidMode);
    }

    [[nodiscard]] static bool check_throttle_matching(FlightMode current, FlightMode target, const TelemetrySnapshot& t) noexcept {
        const bool is_current_auto = (current == FlightMode::AltHold ||
                                      current == FlightMode::PosHold ||
                                      current == FlightMode::Auto ||
                                      current == FlightMode::Guided ||
                                      current == FlightMode::Land ||
                                      current == FlightMode::RTL);

        const bool is_target_manual = (target == FlightMode::Manual ||
                                       target == FlightMode::Stabilize);

        if (t.in_air && is_current_auto && is_target_manual) {
            const float diff = std::abs(t.stick_throttle - t.current_throttle);
            if (diff > 0.15f) {
                return false;
            }
        }
        return true;
    }

    void update_land_detector(const TelemetrySnapshot& t, uint32_t now_ms) noexcept {
        if (!t.in_air || (current_mode_ != FlightMode::Land && current_mode_ != FlightMode::EmergencyLand)) {
            land_detector_ = {};
            return;
        }

        const bool vz_stopped = std::abs(t.vertical_velocity) < 0.25f;
        const bool throttle_min = t.current_throttle < 0.20f;

        if (vz_stopped && throttle_min) {
            if (!land_detector_.ground_contact) {
                land_detector_.ground_contact = true;
                land_detector_.contact_start_ms = now_ms;
            } else if (now_ms - land_detector_.contact_start_ms > 1500) {
                land_detector_.landed = true;
            }
        } else {
            land_detector_.ground_contact = false;
            land_detector_.contact_start_ms = 0;
        }
    }

    bool handle_preemption(const TelemetrySnapshot& t, uint32_t now_ms) noexcept {
        if (t.hardware_kill_switch) {
            perform_transition(FlightMode::Terminate, now_ms);
            failsafe_locked_ = true;
            return true;
        }

        if (t.battery_failsafe_stage >= 2 && current_mode_ != FlightMode::EmergencyLand) {
            perform_transition(FlightMode::EmergencyLand, now_ms);
            failsafe_locked_ = true;
            return true;
        }

        if (t.rc_link_lost && t.in_air) {
            if (current_mode_ != FlightMode::RTL && current_mode_ != FlightMode::Land && current_mode_ != FlightMode::EmergencyLand) {
                if (guard_rtl(t).has_value()) {
                    perform_transition(FlightMode::RTL, now_ms);
                } else {
                    perform_transition(FlightMode::Land, now_ms);
                }
                return true;
            }
        }
        return false;
    }

    void handle_graceful_degradation(const TelemetrySnapshot& t, uint32_t now_ms) noexcept {
        if (current_mode_ == FlightMode::PosHold || current_mode_ == FlightMode::Auto) {
            if (!guard_pos_hold(t).has_value()) {
                perform_transition(FlightMode::AltHold, now_ms);
            }
        }

        if (current_mode_ == FlightMode::AltHold) {
            if (!t.ekf_pos_vert_valid) {
                perform_transition(FlightMode::Stabilize, now_ms);
            }
        }
    }
};
