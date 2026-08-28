#include <array>
#include <span>
#include <cmath>
#include <algorithm>
#include <expected>
#include <numbers>

namespace safety {

inline constexpr size_t NumJoints = 3;
inline constexpr float DeltaTimeSec = 0.001f;

enum class State : uint8_t {
    Normal = 0,
    WarningSls,
    ControlledStopSS1,
    StoTripped
};

struct CartesianBox {
    float x_min, x_max;
    float y_min, y_max;
    float z_min, z_max;

    [[nodiscard]] constexpr bool contains(const std::array<float, 3>& pt) const noexcept {
        return (pt[0] >= x_min && pt[0] <= x_max &&
                pt[1] >= y_min && pt[1] <= y_max &&
                pt[2] >= z_min && pt[2] <= z_max);
    }
};

struct Config {
    std::array<float, NumJoints> max_joint_vel{1.5f, 1.5f, 2.0f};
    std::array<float, NumJoints> collision_threshold{12.0f, 10.0f, 6.0f};
    std::array<float, NumJoints> observer_gain_ki{25.0f, 25.0f, 25.0f};
    CartesianBox allowed_zone{-0.8f, 0.8f, -0.8f, 0.8f, 0.0f, 1.2f};
};

class Watchdog {
public:
    explicit constexpr Watchdog(const Config& cfg) noexcept
        : cfg_(cfg), state_(State::Normal), sto_active_(false) {
        momentum_integral_.fill(0.0f);
        residual_.fill(0.0f);
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] bool is_sto_active() const noexcept { return sto_active_; }
    [[nodiscard]] std::span<const float, NumJoints> residual_torque() const noexcept {
        return residual_;
    }

    State update(std::span<const float, NumJoints> q,
                 std::span<const float, NumJoints> q_dot,
                 std::span<const float, NumJoints> tau_measured) noexcept {
        auto [M, c_t_qdot, g] = compute_dynamics(q, q_dot);
        auto tcp = compute_forward_kinematics(q);

        /* 1. Розрахунок узагальненого імпульсу p = M * q_dot */
        std::array<float, NumJoints> p{};
        for (size_t i = 0; i < NumJoints; ++i) {
            for (size_t j = 0; j < NumJoints; ++j) {
                p[i] += M[i][j] * q_dot[j];
            }
        }

        /* 2. Інтегрування спостерігача імпульсу */
        bool collision = false;
        for (size_t i = 0; i < NumJoints; ++i) {
            float integrand = tau_measured[i] + c_t_qdot[i] - g[i] + residual_[i];
            momentum_integral_[i] += integrand * DeltaTimeSec;
            residual_[i] = cfg_.observer_gain_ki[i] * (p[i] - momentum_integral_[i]);

            if (std::abs(residual_[i]) > cfg_.collision_threshold[i]) {
                collision = true;
            }
        }

        /* 3. Перевірка безпечної швидкості (SLS) */
        bool speed_exceeded = false;
        for (size_t i = 0; i < NumJoints; ++i) {
            if (std::abs(q_dot[i]) > cfg_.max_joint_vel[i]) {
                speed_exceeded = true;
            }
        }

        /* 4. Перевірка декартової робочої зони */
        bool out_of_bounds = !cfg_.allowed_zone.contains(tcp);

        /* 5. Автомат станів */
        switch (state_) {
        case State::Normal:
            if (collision) {
                state_ = State::ControlledStopSS1;
            } else if (speed_exceeded || out_of_bounds) {
                state_ = State::WarningSls;
            }
            break;

        case State::WarningSls:
            if (collision) {
                state_ = State::ControlledStopSS1;
            } else if (!speed_exceeded && !out_of_bounds) {
                state_ = State::Normal;
            }
            break;

        case State::ControlledStopSS1:
            sto_active_ = true;
            state_ = State::StoTripped;
            break;

        case State::StoTripped:
            sto_active_ = true;
            break;
        }

        return state_;
    }

private:
    struct DynamicsResult {
        std::array<std::array<float, NumJoints>, NumJoints> M;
        std::array<float, NumJoints> c_t_qdot;
        std::array<float, NumJoints> g;
    };

    static DynamicsResult compute_dynamics(std::span<const float, NumJoints> q,
                                           std::span<const float, NumJoints> q_dot) noexcept {
        DynamicsResult res{};
        res.M[0][0] = 2.5f + 0.8f * std::cos(q[1]);
        res.M[0][1] = 0.4f * std::cos(q[1]);
        res.M[0][2] = 0.0f;

        res.M[1][0] = res.M[0][1];
        res.M[1][1] = 1.2f + 0.3f * std::cos(q[2]);
        res.M[1][2] = 0.15f * std::cos(q[2]);

        res.M[2][0] = 0.0f;
        res.M[2][1] = res.M[1][2];
        res.M[2][2] = 0.5f;

        res.c_t_qdot[0] = -0.4f * std::sin(q[1]) * q_dot[1] * q_dot[0];
        res.c_t_qdot[1] =  0.4f * std::sin(q[1]) * q_dot[0] * q_dot[0];
        res.c_t_qdot[2] =  0.0f;

        res.g[0] = 0.0f;
        res.g[1] = 9.81f * 1.5f * std::cos(q[0] + q[1]);
        res.g[2] = 9.81f * 0.5f * std::cos(q[0] + q[1] + q[2]);
        return res;
    }

    static std::array<float, 3> compute_forward_kinematics(std::span<const float, NumJoints> q) noexcept {
        constexpr float l1 = 0.4f, l2 = 0.35f, l3 = 0.15f;
        float a1 = q[0], a2 = q[0] + q[1], a3 = q[0] + q[1] + q[2];
        return {
            l1 * std::cos(a1) + l2 * std::cos(a2) + l3 * std::cos(a3),
            l1 * std::sin(a1) + l2 * std::sin(a2) + l3 * std::sin(a3),
            0.2f
        };
    }

    Config cfg_;
    State state_;
    bool sto_active_;
    std::array<float, NumJoints> momentum_integral_{};
    std::array<float, NumJoints> residual_{};
};

} // namespace safety
