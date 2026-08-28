#include <array>
#include <cmath>
#include <numbers>
#include <optional>

namespace autopilot::navigation {

constexpr float PI = std::numbers::pi_v<float>;
constexpr float TWO_PI = 2.0f * PI;

/* Нормалізація кута в діапазон [-pi, +pi] */
[[nodiscard]] constexpr float wrap_pi(float angle) noexcept {
    while (angle > PI) angle -= TWO_PI;
    while (angle < -PI) angle += TWO_PI;
    return angle;
}

struct WindVector2D {
    float north{0.0f};  // м/с
    float east{0.0f};   // м/с

    [[nodiscard]] float speed() const noexcept {
        return std::hypot(north, east);
    }

    [[nodiscard]] float direction_rad() const noexcept {
        return wrap_pi(std::atan2(east, north));
    }
};

struct CrabSolution {
    float heading_cmd_rad{0.0f};   // Уставка курсу psi
    float crab_angle_rad{0.0f};    // Кут крабування alpha_c
    float ground_speed_exp{0.0f};  // Очікувана шляхова швидкість V_g
    bool  is_solvable{true};       // Чи подолано бічний знос
};

class WindEstimatorEKF {
public:
    WindEstimatorEKF() noexcept {
        reset();
    }

    void reset() noexcept {
        state_ = {0.0f, 0.0f, 1.0f}; // W_N=0, W_E=0, k_scale=1.0
        P_ = {};
        P_[0][0] = 25.0f;   // Дисперсія W_N (5 м/с)^2
        P_[1][1] = 25.0f;   // Дисперсія W_E (5 м/с)^2
        P_[2][2] = 0.04f;   // Дисперсія k_scale (0.2)^2
    }

    // Прогноз стану (часова екстраполяція)
    void predict(float dt) noexcept {
        if (dt <= 0.0f) return;
        P_[0][0] += Q_wind_ * dt;
        P_[1][1] += Q_wind_ * dt;
        P_[2][2] += Q_scale_ * dt;
    }

    // Комплексування вимірювання повітряної швидкості
    bool fuse_airspeed(float tas_measured,
                       float vg_north,
                       float vg_east,
                       float heading_rad,
                       float pitch_rad) noexcept {
        if (tas_measured <= 1.0f) return false;

        const float k_scale = state_[2];
        const float tas_scaled = k_scale * tas_measured;

        // Вектор повітряної швидкості за різницею: v_a = V_g - W
        const float diff_n = vg_north - state_[0];
        const float diff_e = vg_east - state_[1];
        const float pred_tas = std::hypot(diff_n, diff_e);

        if (pred_tas < 0.1f) return false;

        // Інновація (нев'язка вимірювання)
        const float innov = tas_scaled - pred_tas;

        // Градієнт функції спостереження (Якобіан H)
        const std::array<float, 3> H = {
            -diff_n / pred_tas,
            -diff_e / pred_tas,
            tas_measured
        };

        // Обчислення P * H^T
        std::array<float, 3> PHt{};
        for (std::size_t i = 0; i < 3; ++i) {
            PHt[i] = P_[i][0] * H[0] + P_[i][1] * H[1] + P_[i][2] * H[2];
        }

        // Інноваційна коваріація S = H * P * H^T + R
        const float S = H[0] * PHt[0] + H[1] * PHt[1] + H[2] * PHt[2] + R_tas_;
        if (S <= 0.0001f) return false;

        // Коефіцієнт Калмана K = PHt / S
        std::array<float, 3> K{};
        for (std::size_t i = 0; i < 3; ++i) {
            K[i] = PHt[i] / S;
            state_[i] += K[i] * innov;
        }

        // Обмеження калібрувального коефіцієнта трубки Піто
        state_[2] = std::clamp(state_[2], 0.7f, 1.3f);

        // Оновлення коваріації Joseph-подібним виразом: P = (I - K*H) * P
        std::array<std::array<float, 3>, 3> I_KH{};
        for (std::size_t i = 0; i < 3; ++i) {
            for (std::size_t j = 0; j < 3; ++j) {
                const float delta = (i == j) ? 1.0f : 0.0f;
                I_KH[i][j] = delta - K[i] * H[j];
            }
        }

        std::array<std::array<float, 3>, 3> P_next{};
        for (std::size_t i = 0; i < 3; ++i) {
            for (std::size_t j = 0; j < 3; ++j) {
                float sum = 0.0f;
                for (std::size_t k = 0; k < 3; ++k) {
                    sum += I_KH[i][k] * P_[k][j];
                }
                P_next[i][j] = sum;
            }
        }
        P_ = P_next;
        return true;
    }

    [[nodiscard]] WindVector2D wind() const noexcept {
        return WindVector2D{state_[0], state_[1]};
    }

    [[nodiscard]] float airspeed_scale() const noexcept {
        return state_[2];
    }

private:
    std::array<float, 3> state_{0.0f, 0.0f, 1.0f}; // [W_N, W_E, k_scale]
    std::array<std::array<float, 3>, 3> P_{};      // Коваріація
    float Q_wind_{0.1f};                            // Процесний шум вітру
    float Q_scale_{1e-5f};                          // Дрейф масштабу
    float R_tas_{1.5f};                             // Шум датчика швидкості
};

// Аналітичний розрахунок уставки курсу та кута крабування
[[nodiscard]] CrabSolution calculate_crab_solution(float track_cmd_rad,
                                                   float tas,
                                                   const WindVector2D& wind) noexcept {
    CrabSolution solution{};

    if (tas < 1.0f) {
        solution.heading_cmd_rad = track_cmd_rad;
        solution.is_solvable = false;
        return solution;
    }

    // Бокова та поздовжня складові вітру відносно лінії шляху
    const float w_cross = wind.north * std::sin(track_cmd_rad) - wind.east * std::cos(track_cmd_rad);
    const float w_along = wind.north * std::cos(track_cmd_rad) + wind.east * std::sin(track_cmd_rad);

    const float sin_crab = w_cross / tas;

    if (std::abs(sin_crab) >= 1.0f) {
        // Зрив наведення: боковий вітер перевищує повітряну швидкість
        solution.is_solvable = false;
        solution.crab_angle_rad = (sin_crab > 0.0f) ? (PI * 0.5f) : (-PI * 0.5f);
        solution.heading_cmd_rad = wrap_pi(track_cmd_rad - solution.crab_angle_rad);
        solution.ground_speed_exp = 0.0f;
        return solution;
    }

    solution.crab_angle_rad = std::asin(sin_crab);
    solution.heading_cmd_rad = wrap_pi(track_cmd_rad - solution.crab_angle_rad);
    solution.ground_speed_exp = tas * std::cos(solution.crab_angle_rad) + w_along;
    solution.is_solvable = (solution.ground_speed_exp > 0.0f);

    return solution;
}

} // namespace autopilot::navigation
