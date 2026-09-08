#pragma once

#include <cmath>
#include <cstddef>
#include <string_view>

namespace cardan {

// Математичні константи
inline constexpr double PI = 3.14159265358979323846;
inline constexpr double TWO_PI = 2.0 * PI;

/**
 * @brief Структура кінематичного стану вала в певний момент часу
 */
struct ShaftState {
    double phi{0.0};       // Поточний кут повороту (рад)
    double omega{0.0};     // Миттєва кутова швидкість (рад/с)
    double alpha{0.0};     // Миттєве кутове прискорення (рад/с²)
    double torque_dyn{0.0};// Динамічний крутний момент від інерції J*alpha (Н·м)
};

/**
 * @brief Геометрична конфігурація двозв'язного карданного валопроводу
 */
struct DrivetrainConfig {
    double beta1{0.0};     // Кут зламу шарніра 1 (рад)
    double beta2{0.0};     // Кут зламу шарніра 2 (рад)
    double gamma{0.0};     // Кут взаємного розфазування вилок проміжного вала (рад)
    double j_load{0.0};    // Момент інерції навантаження на вихідному валу (кг·м²)
};

/**
 * @brief Шаблонний клас високопродуктивного розрахунку кінематики карданних передач реального часу
 */
template <typename T = double>
class CardanKinematics {
public:
    using value_type = T;

    /**
     * @brief Розрахунок кута повороту відомого вала одиночного шарніра Гука:
     * tan(phi2) = tan(phi1) * cos(beta)
     */
    static constexpr T single_joint_phi2(T phi1, T beta) noexcept {
        const T cos_b = std::cos(beta);
        const T sin_p = std::sin(phi1);
        const T cos_p = std::cos(phi1);

        const T turns = std::floor(phi1 / static_cast<T>(TWO_PI));
        const T phi1_rem = phi1 - turns * static_cast<T>(TWO_PI);

        T phi2_rem = std::atan2(std::sin(phi1_rem) * cos_b, std::cos(phi1_rem));
        if (phi2_rem < static_cast<T>(0.0)) {
            phi2_rem += static_cast<T>(TWO_PI);
        }

        return turns * static_cast<T>(TWO_PI) + phi2_rem;
    }

    /**
     * @brief Миттєве передавальне відношення одиночного шарніра:
     * i(phi1) = omega2 / omega1 = cos(beta) / (1 - sin²(beta) * sin²(phi1))
     */
    static constexpr T single_joint_ratio(T phi1, T beta) noexcept {
        const T cos_b = std::cos(beta);
        const T sin_b = std::sin(beta);
        const T sin_p = std::sin(phi1);
        const T denom = static_cast<T>(1.0) - (sin_b * sin_p) * (sin_b * sin_p);

        // Захист від ділення на нуль при вироджених кутах
        if (denom < static_cast<T>(1e-9)) {
            return cos_b / static_cast<T>(1e-9);
        }
        return cos_b / denom;
    }

    /**
     * @brief Аналітичне кутове прискорення відомого вала при сталій вхідній швидкості omega1:
     * alpha2 = omega1² * cos(beta) * sin²(beta) * sin(2*phi1) / (1 - sin²(beta)*sin²(phi1))²
     */
    static constexpr T single_joint_alpha2(T phi1, T omega1, T beta) noexcept {
        const T cos_b = std::cos(beta);
        const T sin_b = std::sin(beta);
        const T sin_p = std::sin(phi1);
        const T sin_2p = std::sin(static_cast<T>(2.0) * phi1);

        const T denom = static_cast<T>(1.0) - (sin_b * sin_p) * (sin_b * sin_p);
        if (denom < static_cast<T>(1e-9)) {
            return static_cast<T>(0.0);
        }

        const T num = (omega1 * omega1) * cos_b * (sin_b * sin_b) * sin_2p;
        return num / (denom * denom);
    }

    /**
     * @brief Повний розрахунок стану одиночного шарніра Гука в реальному часі
     */
    static constexpr ShaftState evaluate_single_joint(
        T phi1,
        T omega1,
        T beta,
        T j_load
    ) noexcept {
        ShaftState state{};
        state.phi = single_joint_phi2(phi1, beta);
        state.omega = omega1 * single_joint_ratio(phi1, beta);
        state.alpha = single_joint_alpha2(phi1, omega1, beta);
        state.torque_dyn = j_load * state.alpha;
        return state;
    }

    /**
     * @brief Розрахунок стану вихідного вала двозв'язної карданної передачі (Z- та W-схеми)
     */
    static ShaftState evaluate_double_drivetrain(
        T phi1,
        T omega1,
        const DrivetrainConfig& cfg
    ) noexcept {
        ShaftState state{};

        // Шарнір 1: вхідний вал -> проміжний вал
        const T phi2 = single_joint_phi2(phi1, cfg.beta1);
        const T ratio1 = single_joint_ratio(phi1, cfg.beta1);
        const T omega2 = omega1 * ratio1;

        // Шарнір 2: проміжний вал -> вихідний вал
        // Базовий зсув pi/2 відповідає копланарним вилкам проміжного вала (повна компенсація при gamma = 0)
        const T phi2_fork = phi2 + static_cast<T>(PI / 2.0) + cfg.gamma;
        state.phi = single_joint_phi2(phi2_fork, cfg.beta2);
        const T ratio2 = single_joint_ratio(phi2_fork, cfg.beta2);
        state.omega = omega2 * ratio2;

        // Високоточне симетричне числове диференціювання швидкості вихідного вала
        constexpr T dt = static_cast<T>(1e-6);
        const T phi1_fwd = phi1 + omega1 * dt;
        const T phi2_fwd = single_joint_phi2(phi1_fwd, cfg.beta1);
        const T w2_fwd = omega1 * single_joint_ratio(phi1_fwd, cfg.beta1);
        const T w_out_fwd = w2_fwd * single_joint_ratio(phi2_fwd + static_cast<T>(PI / 2.0) + cfg.gamma, cfg.beta2);

        const T phi1_bwd = phi1 - omega1 * dt;
        const T phi2_bwd = single_joint_phi2(phi1_bwd, cfg.beta1);
        const T w2_bwd = omega1 * single_joint_ratio(phi1_bwd, cfg.beta1);
        const T w_out_bwd = w2_bwd * single_joint_ratio(phi2_bwd + static_cast<T>(PI / 2.0) + cfg.gamma, cfg.beta2);

        state.alpha = (w_out_fwd - w_out_bwd) / (static_cast<T>(2.0) * dt);
        state.torque_dyn = cfg.j_load * state.alpha;

        return state;
    }
};

} // namespace cardan
