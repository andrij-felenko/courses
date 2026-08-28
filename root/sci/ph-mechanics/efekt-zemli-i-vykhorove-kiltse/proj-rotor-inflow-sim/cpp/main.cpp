#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <vector>
#include <iomanip>

namespace aero {

constexpr double R_ROTOR     = 0.15;     // радіус гвинта квадрокоптера, м
constexpr double MASS        = 1.20;     // маса апарата, кг
constexpr double GRAVITY     = 9.80665;  // прискорення вільного падіння, м/с²
constexpr double RHO_AIR     = 1.225;    // густина повітря, кг/м³

enum class RotorRegime {
    NormalHover,
    GroundEffect,
    VortexRingState,
    TurbulentWake,
    WindmillBrake
};

[[nodiscard]] constexpr std::string_view regime_name(RotorRegime r) noexcept {
    switch (r) {
        case RotorRegime::NormalHover:     return "Звичайне висіння (OGE)";
        case RotorRegime::GroundEffect:    return "Екран землі (IGE)";
        case RotorRegime::VortexRingState: return "Вихорове кільце (VRS)";
        case RotorRegime::TurbulentWake:   return "Турбулентний слід";
        case RotorRegime::WindmillBrake:   return "Режим вітряка";
    }
    return "Невідомий";
}

struct VehicleState {
    double z{0.0};           // висота над землею, м
    double vx{0.0};          // горизонтальна швидкість уперед, м/с
    double vy{0.0};          // бічна швидкість управо, м/с
    double vz{0.0};          // вертикальна швидкість (додатна вгору), м/с
    double thrust_cmd{0.0};  // командна тяга моторів, Н
    RotorRegime regime{RotorRegime::NormalHover};
};

class AerodynamicSolver {
public:
    [[nodiscard]] static std::pair<double, RotorRegime> compute_inflow(
        double thrust, double z, double vx, double vy, double vz) noexcept
    {
        constexpr double disk_area = std::numbers::pi * R_ROTOR * R_ROTOR;
        if (thrust <= 0.05) {
            return {0.0, RotorRegime::NormalHover};
        }

        const double vi0 = std::sqrt(thrust / (2.0 * RHO_AIR * disk_area));
        const double v_horiz = std::hypot(vx, vy);
        const double v_hat_z = vz / vi0;
        const double v_hat_x = v_horiz / vi0;

        double vi_dimless = 1.0;
        RotorRegime reg = RotorRegime::NormalHover;

        if (v_hat_z >= 0.0) {
            // Режим висіння або набору
            const double half_vz = v_hat_z / 2.0;
            vi_dimless = -half_vz + std::sqrt(half_vz * half_vz + 1.0);
            reg = RotorRegime::NormalHover;
        } else if (v_hat_z <= -2.0) {
            // Режим вітряка / авторотації
            const double half_vz = v_hat_z / 2.0;
            const double disc = half_vz * half_vz - 1.0;
            vi_dimless = -half_vz - std::sqrt(std::max(0.0, disc));
            reg = RotorRegime::WindmillBrake;
        } else {
            // Зона VRS / рециркуляції
            if (v_hat_x < 1.0) {
                const double vi_vrs = 1.0 - 0.125 * v_hat_z - 1.125 * v_hat_z * v_hat_z - 0.5 * std::pow(v_hat_z, 3);
                const double vi_skew = 1.0 / std::sqrt(v_hat_x * v_hat_x + std::pow(v_hat_z + vi_vrs, 2) + 0.01);
                vi_dimless = vi_vrs * (1.0 - v_hat_x) + vi_skew * v_hat_x;

                if (v_hat_z >= -1.25 && v_hat_z <= -0.4) {
                    reg = RotorRegime::VortexRingState;
                } else {
                    reg = RotorRegime::TurbulentWake;
                }
            } else {
                vi_dimless = 1.0 / std::hypot(v_hat_x, v_hat_z);
                reg = RotorRegime::NormalHover;
            }
        }

        double vi = vi_dimless * vi0;

        // Корекція на ефект землі (IGE)
        if (z > 0.05 && z < 2.5 * R_ROTOR && std::abs(vz) < 0.5 && v_horiz < 1.5) {
            const double hr = z / R_ROTOR;
            const double ige_ratio = 1.0 / (0.9926 + 0.0379 / (hr * hr));
            vi *= ige_ratio;
            reg = RotorRegime::GroundEffect;
        }

        return {vi, reg};
    }

    static void step(VehicleState& s, double dt) noexcept {
        const auto [vi, regime] = compute_inflow(s.thrust_cmd, s.z, s.vx, s.vy, s.vz);
        s.regime = regime;

        double actual_thrust = s.thrust_cmd;
        if (s.regime == RotorRegime::VortexRingState) {
            actual_thrust *= 0.65; // втрата 35% тяги через тороїдальний зрив
        } else if (s.regime == RotorRegime::GroundEffect) {
            actual_thrust *= 1.18; // приріст тяги на повітряній подушці
        }

        const double weight = MASS * GRAVITY;
        const double az = (actual_thrust - weight) / MASS;
        const double ax = -0.5 * RHO_AIR * 0.05 * s.vx * std::abs(s.vx) / MASS;
        const double ay = -0.5 * RHO_AIR * 0.05 * s.vy * std::abs(s.vy) / MASS;

        s.vz += az * dt;
        s.vx += ax * dt;
        s.vy += ay * dt;
        s.z += s.vz * dt;

        if (s.z < 0.0) {
            s.z = 0.0;
            s.vz = 0.0;
        }
    }
};

} // namespace aero

int main() {
    std::cout << "=== Симуляція динаміки VRS та маневру Вюішара (C++) ===\n\n";

    // Сценарій 1: Помилкова спроба дати газ на місці
    aero::VehicleState s_panic{
        .z = 30.0, .vx = 0.0, .vy = 0.0, .vz = -3.2,
        .thrust_cmd = aero::MASS * aero::GRAVITY
    };

    std::cout << "--- Сценарій 1: Додавання газу на місці (залипання у VRS) ---\n";
    for (int step = 0; step <= 30; ++step) {
        const double time = step * 0.1;
        if (step == 5) {
            s_panic.thrust_cmd = aero::MASS * aero::GRAVITY * 1.40;
        }
        aero::AerodynamicSolver::step(s_panic, 0.1);
        if (step % 5 == 0) {
            std::cout << std::fixed << std::setprecision(1)
                      << "t=" << time << "s | z=" << std::setprecision(2) << s_panic.z
                      << "m | vz=" << std::showpos << s_panic.vz << "m/s | Режим: "
                      << std::noshowpos << aero::regime_name(s_panic.regime) << "\n";
        }
    }

    // Сценарій 2: Маневр Вюішара
    aero::VehicleState s_vuichard{
        .z = 30.0, .vx = 0.0, .vy = 0.0, .vz = -3.2,
        .thrust_cmd = aero::MASS * aero::GRAVITY
    };

    std::cout << "\n--- Сценарій 2: Маневр Вюішара (бічний зсув vy = 3.5 м/с) ---\n";
    for (int step = 0; step <= 30; ++step) {
        const double time = step * 0.1;
        if (step == 3) {
            s_vuichard.vy = 3.5;
            s_vuichard.thrust_cmd = aero::MASS * aero::GRAVITY * 1.25;
        }
        aero::AerodynamicSolver::step(s_vuichard, 0.1);
        if (step % 5 == 0) {
            std::cout << std::fixed << std::setprecision(1)
                      << "t=" << time << "s | z=" << std::setprecision(2) << s_vuichard.z
                      << "m | vz=" << std::showpos << s_vuichard.vz << "m/s | vy="
                      << s_vuichard.vy << "m/s | Режим: "
                      << std::noshowpos << aero::regime_name(s_vuichard.regime) << "\n";
        }
    }

    return 0;
}
