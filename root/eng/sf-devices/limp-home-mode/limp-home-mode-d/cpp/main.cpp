#include <cstdint>
#include <chrono>
#include <optional>
#include <algorithm>
#include <span>

namespace embedded::power {

enum class LimpState : uint8_t {
    Normal          = 0,
    Throttled       = 1,
    LimpL1          = 2,
    LimpL2          = 3,
    CriticalLanding = 4,
    LatchedFault    = 5
};

enum class DiagnosticCode : uint16_t {
    None              = 0x0000,
    MosfetOvertemp    = 0x1001,
    BatteryUndervolt  = 0x2001,
    CellUnbalance     = 0x2002,
    PhaseCurrentFault = 0x3001,
    CommLinkLost      = 0x4001
};

struct SensorTelemetry {
    float mosfet_temp_c{25.0f};
    float bus_voltage_v{24.0f};
    float min_cell_voltage_v{4.0f};
    float total_current_a{0.0f};
    bool  current_sensor_valid{true};
    bool  comm_link_active{true};
    std::chrono::milliseconds timestamp{0};
};

struct ControlOutputs {
    float max_allowed_current_a{80.0f};
    uint32_t target_pwm_freq_hz{25000};
    bool  enable_tier1_nav{true};
    bool  enable_tier2_sbc{true};
    bool  enable_tier3_payload{true};
    LimpState current_state{LimpState::Normal};
    DiagnosticCode active_dtc{DiagnosticCode::None};
};

struct ControllerConfig {
    float temp_warn_c{90.0f};
    float temp_crit_c{105.0f};
    float temp_fatal_c{115.0f};
    float temp_hysteresis_c{8.0f};
    float volt_min_cell_warn_v{3.3f};
    float volt_min_cell_crit_v{3.0f};
    float nominal_current_max_a{80.0f};
    float limp_l1_current_max_a{40.0f};
    float limp_l2_current_max_a{28.0f};
    std::chrono::milliseconds min_dwell_time{10000};
};

class LimpHomeController {
public:
    explicit constexpr LimpHomeController(const ControllerConfig& cfg) noexcept
        : config_(cfg) {}

    [[nodiscard]] ControlOutputs update(const SensorTelemetry& telem) noexcept {
        const auto now = telem.timestamp;
        const auto dwell = now - state_entry_time_;
        const auto fault = detect_fault(telem);

        evaluate_state_machine(telem, fault, dwell, now);
        return generate_outputs(telem);
    }

    [[nodiscard]] LimpState current_state() const noexcept { return state_; }
    [[nodiscard]] DiagnosticCode latched_dtc() const noexcept { return latched_dtc_; }

private:
    [[nodiscard]] DiagnosticCode detect_fault(const SensorTelemetry& t) const noexcept {
        if (!t.current_sensor_valid) return DiagnosticCode::PhaseCurrentFault;
        if (t.mosfet_temp_c >= config_.temp_fatal_c) return DiagnosticCode::MosfetOvertemp;
        if (t.min_cell_voltage_v <= config_.volt_min_cell_crit_v) return DiagnosticCode::BatteryUndervolt;
        if (t.mosfet_temp_c >= config_.temp_crit_c) return DiagnosticCode::MosfetOvertemp;
        if (t.mosfet_temp_c >= config_.temp_warn_c || t.min_cell_voltage_v <= config_.volt_min_cell_warn_v) {
            return DiagnosticCode::MosfetOvertemp;
        }
        return DiagnosticCode::None;
    }

    void transition_to(LimpState next, DiagnosticCode dtc, std::chrono::milliseconds now) noexcept {
        if (state_ != next) {
            state_ = next;
            state_entry_time_ = now;
            if (dtc != DiagnosticCode::None && latched_dtc_ == DiagnosticCode::None) {
                latched_dtc_ = dtc;
            }
        }
    }

    void evaluate_state_machine(const SensorTelemetry& telem,
                                DiagnosticCode fault,
                                std::chrono::milliseconds dwell,
                                std::chrono::milliseconds now) noexcept {
        switch (state_) {
            case LimpState::Normal:
                if (fault == DiagnosticCode::PhaseCurrentFault ||
                    telem.mosfet_temp_c >= config_.temp_fatal_c ||
                    telem.min_cell_voltage_v <= config_.volt_min_cell_crit_v) {
                    transition_to(LimpState::LimpL2, fault, now);
                } else if (telem.mosfet_temp_c >= config_.temp_crit_c) {
                    transition_to(LimpState::LimpL1, fault, now);
                } else if (fault != DiagnosticCode::None) {
                    transition_to(LimpState::Throttled, fault, now);
                }
                break;

            case LimpState::Throttled:
                if (fault == DiagnosticCode::PhaseCurrentFault ||
                    telem.mosfet_temp_c >= config_.temp_fatal_c ||
                    telem.min_cell_voltage_v <= config_.volt_min_cell_crit_v) {
                    transition_to(LimpState::LimpL2, fault, now);
                } else if (telem.mosfet_temp_c >= config_.temp_crit_c) {
                    transition_to(LimpState::LimpL1, fault, now);
                } else if (dwell >= config_.min_dwell_time) {
                    if (telem.mosfet_temp_c <= (config_.temp_warn_c - config_.temp_hysteresis_c) &&
                        telem.min_cell_voltage_v > (config_.volt_min_cell_warn_v + 0.15f)) {
                        transition_to(LimpState::Normal, DiagnosticCode::None, now);
                    }
                }
                break;

            case LimpState::LimpL1:
                if (fault == DiagnosticCode::PhaseCurrentFault ||
                    telem.mosfet_temp_c >= config_.temp_fatal_c ||
                    telem.min_cell_voltage_v <= config_.volt_min_cell_crit_v) {
                    transition_to(LimpState::LimpL2, fault, now);
                } else if (dwell >= config_.min_dwell_time * 2) {
                    if (telem.mosfet_temp_c <= (config_.temp_crit_c - config_.temp_hysteresis_c) &&
                        telem.min_cell_voltage_v > (config_.volt_min_cell_warn_v + 0.2f)) {
                        transition_to(LimpState::Throttled, DiagnosticCode::None, now);
                    }
                }
                break;

            case LimpState::LimpL2:
            case LimpState::CriticalLanding:
            case LimpState::LatchedFault:
            default:
                break;
        }
    }

    [[nodiscard]] ControlOutputs generate_outputs(const SensorTelemetry& telem) const noexcept {
        ControlOutputs out{};
        out.current_state = state_;
        out.active_dtc = latched_dtc_;

        switch (state_) {
            case LimpState::Normal:
                out.max_allowed_current_a = config_.nominal_current_max_a;
                out.target_pwm_freq_hz = 25000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = true;
                out.enable_tier3_payload = true;
                break;

            case LimpState::Throttled: {
                const float factor = std::clamp(
                    (config_.temp_crit_c - telem.mosfet_temp_c) / (config_.temp_crit_c - config_.temp_warn_c),
                    0.0f, 1.0f
                );
                out.max_allowed_current_a = config_.limp_l1_current_max_a +
                    factor * (config_.nominal_current_max_a - config_.limp_l1_current_max_a);
                out.target_pwm_freq_hz = 16000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = true;
                out.enable_tier3_payload = true;
                break;
            }

            case LimpState::LimpL1:
                out.max_allowed_current_a = config_.limp_l1_current_max_a;
                out.target_pwm_freq_hz = 10000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = true;
                out.enable_tier3_payload = false;
                break;

            case LimpState::LimpL2:
            case LimpState::CriticalLanding:
            case LimpState::LatchedFault:
                out.max_allowed_current_a = config_.limp_l2_current_max_a;
                out.target_pwm_freq_hz = 8000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = false;
                out.enable_tier3_payload = false;
                break;
        }
        return out;
    }

    ControllerConfig config_;
    LimpState state_{LimpState::Normal};
    DiagnosticCode latched_dtc_{DiagnosticCode::None};
    std::chrono::milliseconds state_entry_time_{0};
};

} // namespace embedded::power
