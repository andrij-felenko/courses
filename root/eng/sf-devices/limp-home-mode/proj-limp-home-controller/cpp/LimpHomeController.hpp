// ============================================================================
// LimpHomeController.hpp - C++20 Реалізація
// ============================================================================
#pragma once

#include <cstdint>
#include <chrono>
#include <array>
#include <span>
#include <optional>
#include <algorithm>

namespace embedded::limp {

enum class State : uint8_t {
    Normal          = 0,
    Throttled       = 1,
    LimpL1          = 2,
    LimpL2          = 3,
    CriticalLanding = 4,
    LatchedFault    = 5,
    Count
};

enum class EventSeverity : uint8_t {
    None         = 0,
    Warning      = 1,
    Critical1    = 2,
    Critical2    = 3,
    Fatal        = 4,
    Count
};

enum class DtcCode : uint16_t {
    Ok                 = 0x0000,
    MosfetOvertemp     = 0x1001,
    MotorOvertemp      = 0x1002,
    BatterySag         = 0x2001,
    CellUnbalance      = 0x2002,
    CurrentSenseFail   = 0x3001,
    CommLinkTimeout    = 0x4001,
    DescentStall       = 0x5001
};

struct SensorTelemetry {
    float mosfet_temp_c{25.0f};
    float motor_temp_c{25.0f};
    float bus_voltage_v{24.0f};
    float min_cell_voltage_v{4.0f};
    float total_current_a{0.0f};
    bool  current_sensors_healthy{true};
    bool  telemetry_link_healthy{true};
    std::chrono::milliseconds timestamp{0};
};

struct ControlOutputs {
    float max_allowed_current_a{80.0f};
    uint32_t target_pwm_freq_hz{25000};
    bool  enable_tier1_nav{true};
    bool  enable_tier2_sbc{true};
    bool  enable_tier3_payload{true};
    State current_state{State::Normal};
    DtcCode active_primary_dtc{DtcCode::Ok};
    uint32_t total_dtc_count{0};
};

struct Config {
    float temp_warn_c{90.0f};
    float temp_crit_c{105.0f};
    float temp_fatal_c{115.0f};
    float temp_hysteresis_c{8.0f};
    float cell_volt_warn_v{3.3f};
    float cell_volt_crit_v{3.0f};
    float nominal_current_max_a{80.0f};
    float limp_l1_current_max_a{40.0f};
    float limp_l2_current_max_a{28.0f};
    std::chrono::milliseconds min_dwell_time{10000};
};

struct FreezeFrame {
    DtcCode  code{DtcCode::Ok};
    uint8_t  subsystem_id{0};
    std::chrono::milliseconds timestamp{0};
    float    mosfet_temp_c{0.0f};
    float    bus_voltage_v{0.0f};
    float    min_cell_voltage_v{0.0f};
    float    total_current_a{0.0f};
    uint16_t crc16{0};
};

class LimpHomeController {
public:
    static constexpr size_t RingBufferSize = 16;

    explicit constexpr LimpHomeController(const Config& config) noexcept
        : config_(config) {}

    [[nodiscard]] ControlOutputs step(const SensorTelemetry& telem) noexcept {
        auto [severity, detected_dtc] = classify_telemetry(telem);

        if (detected_dtc != DtcCode::Ok && primary_dtc_ != detected_dtc) {
            push_freeze_frame(detected_dtc, 0x01, telem);
        }

        evaluate_state_transition(severity, telem);
        return generate_outputs(telem);
    }

    [[nodiscard]] State current_state() const noexcept { return current_state_; }
    [[nodiscard]] DtcCode active_dtc() const noexcept { return primary_dtc_; }
    [[nodiscard]] size_t dtc_count() const noexcept { return dtc_count_; }

    [[nodiscard]] std::optional<FreezeFrame> get_dtc_record(size_t index) const noexcept {
        if (index >= dtc_count_) return std::nullopt;
        size_t actual_idx = (head_ + RingBufferSize - dtc_count_ + index) % RingBufferSize;
        return ring_buffer_[actual_idx];
    }

private:
    [[nodiscard]] std::pair<EventSeverity, DtcCode> classify_telemetry(const SensorTelemetry& t) const noexcept {
        if (!t.current_sensors_healthy) {
            return {EventSeverity::Critical2, DtcCode::CurrentSenseFail};
        }
        if (t.mosfet_temp_c >= config_.temp_fatal_c) {
            return {EventSeverity::Critical2, DtcCode::MosfetOvertemp};
        }
        if (t.min_cell_voltage_v <= config_.cell_volt_crit_v) {
            return {EventSeverity::Critical2, DtcCode::BatterySag};
        }
        if (t.mosfet_temp_c >= config_.temp_crit_c) {
            return {EventSeverity::Critical1, DtcCode::MosfetOvertemp};
        }
        if (t.mosfet_temp_c >= config_.temp_warn_c) {
            return {EventSeverity::Warning, DtcCode::MosfetOvertemp};
        }
        if (t.min_cell_voltage_v <= config_.cell_volt_warn_v) {
            return {EventSeverity::Warning, DtcCode::BatterySag};
        }
        return {EventSeverity::None, DtcCode::Ok};
    }

    void evaluate_state_transition(EventSeverity severity, const SensorTelemetry& telem) noexcept {
        State target = transition_matrix_[static_cast<size_t>(current_state_)][static_cast<size_t>(severity)];
        const auto time_in_state = telem.timestamp - state_entry_time_;

        if (target < current_state_) {
            bool allow_recovery = false;
            if (time_in_state >= config_.min_dwell_time) {
                if (current_state_ == State::Throttled && severity == EventSeverity::None) {
                    if (telem.mosfet_temp_c <= (config_.temp_warn_c - config_.temp_hysteresis_c) &&
                        telem.min_cell_voltage_v >= (config_.cell_volt_warn_v + 0.15f)) {
                        allow_recovery = true;
                    }
                } else if (current_state_ == State::LimpL1 && severity <= EventSeverity::Warning) {
                    if (telem.mosfet_temp_c <= (config_.temp_crit_c - config_.temp_hysteresis_c)) {
                        allow_recovery = true;
                    }
                }
            }
            if (!allow_recovery) {
                target = current_state_;
            }
        }

        if (target != current_state_) {
            current_state_ = target;
            state_entry_time_ = telem.timestamp;
        }
    }

    [[nodiscard]] ControlOutputs generate_outputs(const SensorTelemetry& telem) const noexcept {
        ControlOutputs out{};
        out.current_state = current_state_;
        out.active_primary_dtc = primary_dtc_;
        out.total_dtc_count = static_cast<uint32_t>(total_recorded_dtc_);

        switch (current_state_) {
            case State::Normal:
                out.max_allowed_current_a = config_.nominal_current_max_a;
                out.target_pwm_freq_hz = 25000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = true;
                out.enable_tier3_payload = true;
                break;

            case State::Throttled: {
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

            case State::LimpL1:
                out.max_allowed_current_a = config_.limp_l1_current_max_a;
                out.target_pwm_freq_hz = 10000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = true;
                out.enable_tier3_payload = false;
                break;

            case State::LimpL2:
            case State::CriticalLanding:
            case State::LatchedFault:
            default:
                out.max_allowed_current_a = config_.limp_l2_current_max_a;
                out.target_pwm_freq_hz = 8000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = false;
                out.enable_tier3_payload = false;
                break;
        }
        return out;
    }

    void push_freeze_frame(DtcCode code, uint8_t sub_id, const SensorTelemetry& t) noexcept {
        FreezeFrame& slot = ring_buffer_[head_];
        slot.code = code;
        slot.subsystem_id = sub_id;
        slot.timestamp = t.timestamp;
        slot.mosfet_temp_c = t.mosfet_temp_c;
        slot.bus_voltage_v = t.bus_voltage_v;
        slot.min_cell_voltage_v = t.min_cell_voltage_v;
        slot.total_current_a = t.total_current_a;
        slot.crc16 = 0xABCD;

        head_ = (head_ + 1) % RingBufferSize;
        if (dtc_count_ < RingBufferSize) dtc_count_++;
        total_recorded_dtc_++;

        if (primary_dtc_ == DtcCode::Ok) {
            primary_dtc_ = code;
        }
    }

    Config config_;
    State current_state_{State::Normal};
    DtcCode primary_dtc_{DtcCode::Ok};
    std::chrono::milliseconds state_entry_time_{0};
    std::array<FreezeFrame, RingBufferSize> ring_buffer_{};
    size_t head_{0};
    size_t dtc_count_{0};
    size_t total_recorded_dtc_{0};

    static constexpr std::array<std::array<State, static_cast<size_t>(EventSeverity::Count)>, static_cast<size_t>(State::Count)>
    transition_matrix_{{
        { State::Normal,    State::Throttled, State::LimpL1, State::LimpL2, State::CriticalLanding },
        { State::Normal,    State::Throttled, State::LimpL1, State::LimpL2, State::CriticalLanding },
        { State::Throttled, State::LimpL1,    State::LimpL1, State::LimpL2, State::CriticalLanding },
        { State::LimpL2,    State::LimpL2,    State::LimpL2, State::LimpL2, State::CriticalLanding },
        { State::CriticalLanding, State::CriticalLanding, State::CriticalLanding, State::CriticalLanding, State::LatchedFault },
        { State::LatchedFault,    State::LatchedFault,    State::LatchedFault,    State::LatchedFault,    State::LatchedFault }
    }};
};

} // namespace embedded::limp
