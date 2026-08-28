#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>

namespace magnetics {

struct PhysicsConfig {
    double rod_length{0.10};       // m
    double lambda_s{1.2e-3};       // strain saturation
    double h_sat{120000.0};        // A/m
    double h_bias{40000.0};        // A/m bias field
    double turns_per_m{2000.0};    // 1/m
    double mass{0.5};              // kg
    double stiffness{5.0e6};       // N/m
    double damping{150.0};         // N s/m
};

struct StepResult {
    double time_s;
    double current_a;
    double h_field_a_per_m;
    double position_m;
    double velocity_m_per_s;
    double strain;
};

enum class ActuatorError {
    InvalidTimeStep,
    ThermalOverload,
    MechanicalLimitExceeded
};

class TerfenolActuator {
public:
    explicit TerfenolActuator(PhysicsConfig config) 
        : config_(config) {}

    [[nodiscard]] double calculate_strain(double h_field) const noexcept {
        const double ratio = h_field / config_.h_sat;
        return config_.lambda_s * std::tanh(ratio * ratio);
    }

    [[nodiscard]] std::expected<StepResult, ActuatorError> 
    step(double drive_current, double dt) noexcept {
        if (dt <= 0.0 || dt > 1e-2) {
            return std::unexpected(ActuatorError::InvalidTimeStep);
        }

        current_a_ = drive_current;
        h_field_ = config_.h_bias + config_.turns_per_m * drive_current;
        strain_ = calculate_strain(h_field_);

        const double f_ext = config_.stiffness * config_.rod_length * strain_;
        const double accel = (f_ext - config_.stiffness * position_m_ - config_.damping * velocity_m_per_s_) / config_.mass;

        velocity_m_per_s_ += accel * dt;
        position_m_ += velocity_m_per_s_ * dt;
        time_s_ += dt;

        if (std::abs(position_m_) > config_.rod_length * 0.1) {
            return std::unexpected(ActuatorError::MechanicalLimitExceeded);
        }

        return StepResult{
            .time_s = time_s_,
            .current_a = current_a_,
            .h_field_a_per_m = h_field_,
            .position_m = position_m_,
            .velocity_m_per_s = velocity_m_per_s_,
            .strain = strain_
        };
    }

private:
    PhysicsConfig config_;
    double time_s_{0.0};
    double current_a_{0.0};
    double h_field_{0.0};
    double position_m_{0.0};
    double velocity_m_per_s_{0.0};
    double strain_{0.0};
};

} // namespace magnetics

int main() {
    using namespace magnetics;

    PhysicsConfig cfg{};
    TerfenolActuator actuator(cfg);

    constexpr double dt = 1e-5;
    constexpr double freq = 500.0;
    constexpr double current_amp = 5.0;

    std::cout << "Time(s),Current(A),H(A/m),Pos(um),Strain(ppm)\n";

    for (int i = 0; i <= 1000; ++i) {
        const double t = i * dt;
        const double drive_current = current_amp * std::sin(2.0 * std::numbers::pi * freq * t);

        auto res = actuator.step(drive_current, dt);
        if (!res) {
            std::cerr << "Simulation error encountered!\n";
            return 1;
        }

        if (i % 50 == 0) {
            std::cout << res->time_s << ","
                      << res->current_a << ","
                      << res->h_field_a_per_m << ","
                      << res->position_m * 1e6 << ","
                      << res->strain * 1e6 << "\n";
        }
    }

    return 0;
}
