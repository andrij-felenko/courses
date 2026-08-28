#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <algorithm>
#include <numeric>
#include <chrono>
#include <cstdint>

enum class FatState {
    Idle,
    OcvCheck,
    WeldResistanceTest,
    PrechargeQualification,
    CcCvChargeTest,
    SafetyTripVerification,
    Passed,
    Failed
};

enum class FatError {
    None,
    OcvOutOfBounds,
    CellImbalanceTooHigh,
    WeldResistanceExcessive,
    TemperatureGradientHigh,
    OvervoltageProtectionFailed,
    CommunicationTimeout
};

struct FatLimits {
    uint16_t min_cell_mv{2800};
    uint16_t max_cell_mv{4250};
    uint16_t max_imbalance_mv{25};
    uint32_t max_weld_resistance_uohm{700};
    int16_t  max_temp_c{50};
    int16_t  max_temp_gradient_c{6};
    uint16_t ovp_trip_threshold_mv{4280};
};

struct PackTelemetry {
    std::vector<uint16_t> cell_mv;
    std::vector<int16_t>  temp_c;
    std::vector<uint32_t> weld_res_uohm;
    int32_t               current_ma{0};
    bool                  bms_chg_mosfet_active{true};
    bool                  bms_dsg_mosfet_active{true};
};

class FatRunner {
public:
    explicit FatRunner(FatLimits limits) : limits_(limits) {}

    void set_telemetry(PackTelemetry telemetry) {
        telemetry_ = std::move(telemetry);
    }

    [[nodiscard]] FatState state() const noexcept { return state_; }
    [[nodiscard]] FatError last_error() const noexcept { return last_error_; }

    void tick(std::chrono::milliseconds dt) {
        step_timer_ += dt;

        switch (state_) {
            case FatState::Idle:
                state_ = FatState::OcvCheck;
                step_timer_ = std::chrono::milliseconds{0};
                break;

            case FatState::OcvCheck:
                if (auto res = evaluate_ocv(); !res) {
                    last_error_ = res.error();
                    state_ = FatState::Failed;
                } else {
                    state_ = FatState::WeldResistanceTest;
                    step_timer_ = std::chrono::milliseconds{0};
                }
                break;

            case FatState::WeldResistanceTest:
                if (auto res = evaluate_weld_resistance(); !res) {
                    last_error_ = res.error();
                    state_ = FatState::Failed;
                } else {
                    state_ = FatState::CcCvChargeTest;
                    step_timer_ = std::chrono::milliseconds{0};
                }
                break;

            case FatState::CcCvChargeTest:
                if (auto res = evaluate_thermal(); !res) {
                    last_error_ = res.error();
                    state_ = FatState::Failed;
                } else if (step_timer_ >= std::chrono::milliseconds{5000}) {
                    state_ = FatState::SafetyTripVerification;
                    step_timer_ = std::chrono::milliseconds{0};
                }
                break;

            case FatState::SafetyTripVerification:
                if (!telemetry_.bms_chg_mosfet_active) {
                    state_ = FatState::Passed;
                } else if (step_timer_ > std::chrono::milliseconds{2000}) {
                    last_error_ = FatError::OvervoltageProtectionFailed;
                    state_ = FatState::Failed;
                }
                break;

            case FatState::Passed:
            case FatState::Failed:
                break;
        }
    }

private:
    [[nodiscard]] std::expected<void, FatError> evaluate_ocv() const {
        if (telemetry_.cell_mv.empty()) {
            return std::unexpected(FatError::CommunicationTimeout);
        }

        const auto [min_it, max_it] = std::minmax_element(
            telemetry_.cell_mv.begin(), telemetry_.cell_mv.end());

        if (*min_it < limits_.min_cell_mv || *max_it > limits_.max_cell_mv) {
            return std::unexpected(FatError::OcvOutOfBounds);
        }

        if (static_cast<uint16_t>(*max_it - *min_it) > limits_.max_imbalance_mv) {
            return std::unexpected(FatError::CellImbalanceTooHigh);
        }

        return {};
    }

    [[nodiscard]] std::expected<void, FatError> evaluate_weld_resistance() const {
        for (const auto r_uohm : telemetry_.weld_res_uohm) {
            if (r_uohm > limits_.max_weld_resistance_uohm) {
                return std::unexpected(FatError::WeldResistanceExcessive);
            }
        }
        return {};
    }

    [[nodiscard]] std::expected<void, FatError> evaluate_thermal() const {
        if (telemetry_.temp_c.empty()) {
            return {};
        }

        const auto [min_it, max_it] = std::minmax_element(
            telemetry_.temp_c.begin(), telemetry_.temp_c.end());

        if (*max_it > limits_.max_temp_c) {
            return std::unexpected(FatError::TemperatureGradientHigh);
        }

        if (static_cast<int16_t>(*max_it - *min_it) > limits_.max_temp_gradient_c) {
            return std::unexpected(FatError::TemperatureGradientHigh);
        }

        return {};
    }

    FatLimits limits_;
    PackTelemetry telemetry_;
    FatState state_{FatState::Idle};
    FatError last_error_{FatError::None};
    std::chrono::milliseconds step_timer_{0};
};
