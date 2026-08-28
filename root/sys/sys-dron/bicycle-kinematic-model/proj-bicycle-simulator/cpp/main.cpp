#include <cmath>
#include <numbers>
#include <algorithm>
#include <span>
#include <array>

/* Ідіоматична реалізація кінематичного симулятора на C++20 */
namespace robotics {

enum class IntegrationMethod {
    Euler,
    ExactArc,
    RungeKutta4
};

struct BicycleParams {
    double l_f{1.2};             // Відстань CoM -> передня вісь, м
    double l_r{1.4};             // Відстань CoM -> задня вісь, м
    double max_steer{0.65};      // Максимальний кут вивороту керма, рад (~37.2 град)
    double max_steer_rate{1.2};  // Гранична швидкість сервоприводу, рад/с
    double max_accel{3.0};       // Граничне прискорення, м/с^2

    [[nodiscard]] constexpr double wheelbase() const noexcept {
        return l_f + l_r;
    }
};

struct BicycleState {
    double x{0.0};
    double y{0.0};
    double theta{0.0};
    double v{0.0};
    double delta{0.0};
};

struct BicycleDerivatives {
    double dx{0.0};
    double dy{0.0};
    double dtheta{0.0};
    double dv{0.0};
    double ddelta{0.0};
};

class KinematicBicycleModel {
public:
    explicit constexpr KinematicBicycleModel(BicycleParams params) noexcept
        : params_{params} {}

    [[nodiscard]] BicycleDerivatives evaluate_derivatives(
        const BicycleState& state,
        double accel,
        double steer_rate) const noexcept
    {
        const double L = params_.wheelbase();
        const double beta = std::atan((params_.l_r / L) * std::tan(state.delta));
        const double heading_eff = state.theta + beta;

        return BicycleDerivatives{
            .dx = state.v * std::cos(heading_eff),
            .dy = state.v * std::sin(heading_eff),
            .dtheta = (state.v / L) * std::tan(state.delta) * std::cos(beta),
            .dv = accel,
            .ddelta = steer_rate
        };
    }

    void step(
        BicycleState& state,
        double target_v,
        double target_delta,
        double dt,
        IntegrationMethod method = IntegrationMethod::RungeKutta4) const noexcept
    {
        if (dt <= 0.0) return;

        // Обмеження прискорень та кутів
        const double v_err = target_v - state.v;
        const double accel = std::clamp(v_err / dt, -params_.max_accel, params_.max_accel);

        const double delta_clamped = std::clamp(target_delta, -params_.max_steer, params_.max_steer);
        const double delta_err = delta_clamped - state.delta;
        const double steer_rate = std::clamp(delta_err / dt, -params_.max_steer_rate, params_.max_steer_rate);

        switch (method) {
            case IntegrationMethod::Euler:
                integrate_euler(state, accel, steer_rate, dt);
                break;
            case IntegrationMethod::ExactArc:
                integrate_exact_arc(state, accel, steer_rate, dt);
                break;
            case IntegrationMethod::RungeKutta4:
                integrate_rk4(state, accel, steer_rate, dt);
                break;
        }

        state.theta = normalize_angle(state.theta);
        state.delta = std::clamp(state.delta, -params_.max_steer, params_.max_steer);
    }

    // Симуляція пачки кроків уперед (траєкторний горизонт прогнозування)
    void predict_trajectory(
        BicycleState initial_state,
        double target_v,
        double target_delta,
        double dt,
        std::span<BicycleState> out_trajectory) const noexcept
    {
        BicycleState current = initial_state;
        for (auto& point : out_trajectory) {
            step(current, target_v, target_delta, dt, IntegrationMethod::RungeKutta4);
            point = current;
        }
    }

private:
    BicycleParams params_;

    static double normalize_angle(double angle) noexcept {
        while (angle > std::numbers::pi) angle -= 2.0 * std::numbers::pi;
        while (angle < -std::numbers::pi) angle += 2.0 * std::numbers::pi;
        return angle;
    }

    void integrate_euler(BicycleState& s, double a, double sr, double dt) const noexcept {
        const auto d = evaluate_derivatives(s, a, sr);
        s.x += d.dx * dt;
        s.y += d.dy * dt;
        s.theta += d.dtheta * dt;
        s.v += d.dv * dt;
        s.delta += d.ddelta * dt;
    }

    void integrate_exact_arc(BicycleState& s, double a, double sr, double dt) const noexcept {
        const double L = params_.wheelbase();
        const double beta = std::atan((params_.l_r / L) * std::tan(s.delta));
        const double omega = (s.v / L) * std::tan(s.delta) * std::cos(beta);
        const double delta_theta = omega * dt;

        if (std::abs(omega) > 1e-6) {
            const double R = s.v / omega;
            s.x += R * (std::sin(s.theta + beta + delta_theta) - std::sin(s.theta + beta));
            s.y += R * (-std::cos(s.theta + beta + delta_theta) + std::cos(s.theta + beta));
        } else {
            s.x += s.v * std::cos(s.theta + beta) * dt;
            s.y += s.v * std::sin(s.theta + beta) * dt;
        }

        s.theta += delta_theta;
        s.v += a * dt;
        s.delta += sr * dt;
    }

    void integrate_rk4(BicycleState& s, double a, double sr, double dt) const noexcept {
        const auto k1 = evaluate_derivatives(s, a, sr);

        const BicycleState s2{
            .x = s.x + 0.5 * dt * k1.dx,
            .y = s.y + 0.5 * dt * k1.dy,
            .theta = s.theta + 0.5 * dt * k1.dtheta,
            .v = s.v + 0.5 * dt * k1.dv,
            .delta = s.delta + 0.5 * dt * k1.ddelta
        };
        const auto k2 = evaluate_derivatives(s2, a, sr);

        const BicycleState s3{
            .x = s.x + 0.5 * dt * k2.dx,
            .y = s.y + 0.5 * dt * k2.dy,
            .theta = s.theta + 0.5 * dt * k2.dtheta,
            .v = s.v + 0.5 * dt * k2.dv,
            .delta = s.delta + 0.5 * dt * k2.ddelta
        };
        const auto k3 = evaluate_derivatives(s3, a, sr);

        const BicycleState s4{
            .x = s.x + dt * k3.dx,
            .y = s.y + dt * k3.dy,
            .theta = s.theta + dt * k3.dtheta,
            .v = s.v + dt * k3.dv,
            .delta = s.delta + dt * k3.ddelta
        };
        const auto k4 = evaluate_derivatives(s4, a, sr);

        s.x += (dt / 6.0) * (k1.dx + 2.0 * k2.dx + 2.0 * k3.dx + k4.dx);
        s.y += (dt / 6.0) * (k1.dy + 2.0 * k2.dy + 2.0 * k3.dy + k4.dy);
        s.theta += (dt / 6.0) * (k1.dtheta + 2.0 * k2.dtheta + 2.0 * k3.dtheta + k4.dtheta);
        s.v += (dt / 6.0) * (k1.dv + 2.0 * k2.dv + 2.0 * k3.dv + k4.dv);
        s.delta += (dt / 6.0) * (k1.ddelta + 2.0 * k2.ddelta + 2.0 * k3.ddelta + k4.ddelta);
    }
};

} // namespace robotics
