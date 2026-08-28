/* aec_q200_flex_monitor.hpp — Ідіоматична C++20 імплементація */
#pragma once
#include <concepts>
#include <chrono>
#include <expected>
#include <cmath>
#include <string_view>

namespace aec_q200 {

enum class FailureMode {
    CapacitanceDegradation,
    LowOhmicShortCircuit,
    OpenCircuitFracture
};

enum class ExecutionPhase {
    Idle,
    Calibrating,
    Descending,
    Dwelling,
    Retracting,
    Completed
};

struct QualificationParameters {
    float initial_capacitance_pf{100'000.0f};  // 100 нФ
    float target_deflection_mm{5.0f};          // 5.0 мм за AEC-Q200 Soft-Term
    float actuator_speed_mm_s{1.0f};           // 1.0 мм/с
    float pcb_thickness_mm{1.6f};              // Плата 1.6 мм FR-4
    float support_span_mm{90.0f};              // Проліт 90 мм
    float dwell_duration_s{60.0f};             // Витримка 60 с
    float filter_alpha{0.15f};                 // Коефіцієнт ФНЧ
};

struct TelemetryFrame {
    float measured_capacitance_pf{0.0f};
    float leakage_current_na{0.0f};
    float raw_strain_ppm{0.0f};
};

struct FailureReport {
    float failure_deflection_mm{0.0f};
    float failure_microstrain{0.0f};
    float final_capacitance_pf{0.0f};
    float final_leakage_na{0.0f};
    FailureMode failure_type{};
};

class FlexQualificationStation {
public:
    static constexpr float kMaxAllowedCapDropPercent = 5.0f;
    static constexpr float kMaxAllowedLeakageCurrentNA = 50.0f;

    explicit constexpr FlexQualificationStation(const QualificationParameters& params) noexcept
        : params_(params) {}

    [[nodiscard]] constexpr float calculate_strain_ppm(float deflection_mm) const noexcept {
        if (params_.support_span_mm <= 0.0f) return 0.0f;
        const float numerator = 6.0f * params_.pcb_thickness_mm * deflection_mm;
        const float denominator = params_.support_span_mm * params_.support_span_mm;
        return (numerator / denominator) * 1.0e6f;
    }

    [[nodiscard]] std::expected<ExecutionPhase, FailureReport> process_step(
        const TelemetryFrame& telemetry,
        float delta_time_s
    ) noexcept {
        if (phase_ == ExecutionPhase::Completed || phase_ == ExecutionPhase::Idle) {
            return phase_;
        }

        // Цифрова фільтрація тензосигналу
        filtered_strain_ppm_ = params_.filter_alpha * telemetry.raw_strain_ppm +
                               (1.0f - params_.filter_alpha) * filtered_strain_ppm_;

        // Оновлення переміщення пуансона
        if (phase_ == ExecutionPhase::Descending) {
            current_deflection_mm_ += params_.actuator_speed_mm_s * delta_time_s;
            if (current_deflection_mm_ >= params_.target_deflection_mm) {
                current_deflection_mm_ = params_.target_deflection_mm;
                phase_ = ExecutionPhase::Dwelling;
                dwell_elapsed_s_ = 0.0f;
            }
        } else if (phase_ == ExecutionPhase::Dwelling) {
            dwell_elapsed_s_ += delta_time_s;
            if (dwell_elapsed_s_ >= params_.dwell_duration_s) {
                phase_ = ExecutionPhase::Completed;
                return phase_;
            }
        }

        current_microstrain_ = calculate_strain_ppm(current_deflection_mm_);

        const float cap_delta_pct = (params_.initial_capacitance_pf > 0.0f)
            ? (std::abs(telemetry.measured_capacitance_pf - params_.initial_capacitance_pf) /
               params_.initial_capacitance_pf * 100.0f)
            : 0.0f;

        // Перевірка 1: Сплеск струму витоку (КЗ через розтріскування)
        if (telemetry.leakage_current_na >= kMaxAllowedLeakageCurrentNA) {
            phase_ = ExecutionPhase::Completed;
            return std::unexpected(FailureReport{
                .failure_deflection_mm = current_deflection_mm_,
                .failure_microstrain = current_microstrain_,
                .final_capacitance_pf = telemetry.measured_capacitance_pf,
                .final_leakage_na = telemetry.leakage_current_na,
                .failure_type = FailureMode::LowOhmicShortCircuit
            });
        }

        // Перевірка 2: Відхилення ємності понад 5%
        if (cap_delta_pct >= kMaxAllowedCapDropPercent) {
            phase_ = ExecutionPhase::Completed;
            const auto mode = (telemetry.measured_capacitance_pf < params_.initial_capacitance_pf * 0.1f)
                ? FailureMode::OpenCircuitFracture
                : FailureMode::CapacitanceDegradation;

            return std::unexpected(FailureReport{
                .failure_deflection_mm = current_deflection_mm_,
                .failure_microstrain = current_microstrain_,
                .final_capacitance_pf = telemetry.measured_capacitance_pf,
                .final_leakage_na = telemetry.leakage_current_na,
                .failure_type = mode
            });
        }

        return phase_;
    }

    [[nodiscard]] constexpr float current_deflection() const noexcept { return current_deflection_mm_; }
    [[nodiscard]] constexpr float current_microstrain() const noexcept { return current_microstrain_; }
    [[nodiscard]] constexpr float filtered_strain() const noexcept { return filtered_strain_ppm_; }
    [[nodiscard]] constexpr ExecutionPhase current_phase() const noexcept { return phase_; }

private:
    QualificationParameters params_{};
    ExecutionPhase phase_{ExecutionPhase::Descending};
    float current_deflection_mm_{0.0f};
    float current_microstrain_{0.0f};
    float filtered_strain_ppm_{0.0f};
    float dwell_elapsed_s_{0.0f};
};

} // namespace aec_q200
