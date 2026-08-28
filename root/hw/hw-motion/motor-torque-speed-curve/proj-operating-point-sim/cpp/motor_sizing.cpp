// motor_sizing.hpp / motor_sizing.cpp — Ідіоматичний C++20 розрахунок приводу
#include <iostream>
#include <cmath>
#include <numbers>
#include <span>
#include <vector>
#include <algorithm>

namespace motor_sim {

struct MotorParams {
    double u_nom{24.0};       // Номінальна напруга живлення, В
    double r_arm{1.2};        // Активний опір обмотки якоря, Ом
    double k_t{0.038};        // Стала крутного моменту, Н·м/А
    double k_e{0.038};        // Стала протиЕРС, В·с/рад
    double i_0{0.15};         // Струм холостого ходу, А
    double m_cont{0.12};      // Номінальний неперервний момент S1, Н·м
    double m_peak{0.45};      // Граничний піковий момент, Н·м
    double omega_max{650.0};  // Максимальна механічна швидкість, рад/с (~6200 RPM)
    double j_rotor{2.5e-5};   // Момент інерції ротора, кг·м²
};

struct LoadCharacteristics {
    double m_static{0.05};    // Постійний момент опору, Н·м
    double b_viscous{1e-4};   // Коефіцієнт в'язкого тертя, Н·м·с/рад
    double c_aero{2e-6};      // Коефіцієнт аеродинамічного опору, Н·м·с²/рад²
};

struct OperatingPoint {
    double omega_op{0.0};     // Кутова швидкість, рад/с
    double rpm_op{0.0};       // Швидкість, об/хв
    double torque_op{0.0};    // Момент на валу, Н·м
    double current_op{0.0};   // Струм якоря, А
    double p_mech{0.0};       // Корисна механічна потужність, Вт
    double p_loss{0.0};       // Джоулеві втрати I²R, Вт
    double efficiency{0.0};   // ККД
    bool is_s1_safe{false};   // Безпека неперервної роботи S1
};

struct MechanismRequirements {
    double target_omega_load{20.94}; // 200 RPM на навантаженні, рад/с
    double target_torque_load{1.8};  // 1.8 Н·м на виході
    double j_load{1.5e-3};           // Інерція навантаження, кг·м²
    double accel_time{0.15};         // Час розгону 150 мс
    double gear_efficiency{0.85};    // ККД редуктора
};

struct GearboxSelectionResult {
    double i_optimal_inertia{0.0};
    double i_min_continuous{0.0};
    double i_selected{0.0};
    double motor_req_torque{0.0};
    double motor_accel_torque{0.0};
    bool is_feasible{false};
};

class DriveCalculator {
public:
    static OperatingPoint solve_operating_point(const MotorParams& m,
                                                const LoadCharacteristics& load,
                                                double u_applied) noexcept
    {
        OperatingPoint pt;
        const double omega_0 = u_applied / m.k_e;
        double omega = omega_0 * 0.7;

        for (int iter = 0; iter < 100; ++iter) {
            const double m_motor = m.k_t * (u_applied - m.k_e * omega) / m.r_arm;
            const double m_load = load.m_static + load.b_viscous * omega + load.c_aero * omega * omega;

            const double f = m_motor - m_load;
            if (std::abs(f) < 1e-7) {
                break;
            }

            const double df = -(m.k_t * m.k_e) / m.r_arm - load.b_viscous - 2.0 * load.c_aero * omega;
            omega -= f / df;

            if (omega < 0.0) { omega = 0.0; break; }
            if (omega > omega_0) { omega = omega_0; }
        }

        pt.omega_op = omega;
        pt.rpm_op = omega * (30.0 / std::numbers::pi);
        pt.torque_op = std::max(0.0, m.k_t * (u_applied - m.k_e * omega) / m.r_arm);
        pt.current_op = m.i_0 + pt.torque_op / m.k_t;
        pt.p_mech = pt.torque_op * pt.omega_op;
        pt.p_loss = pt.current_op * pt.current_op * m.r_arm;

        const double p_elec = u_applied * pt.current_op;
        pt.efficiency = (p_elec > 1e-6) ? (pt.p_mech / p_elec) : 0.0;
        pt.is_s1_safe = (pt.torque_op <= m.m_cont) && (pt.omega_op <= m.omega_max);

        return pt;
    }

    static GearboxSelectionResult select_gearbox(const MotorParams& m,
                                                 const MechanismRequirements& req) noexcept
    {
        GearboxSelectionResult res;

        // 1. Оптимальне i за узгодженням інерції
        res.i_optimal_inertia = std::sqrt(req.j_load / m.j_rotor);

        // 2. Мінімальне i за неперервним моментом S1
        res.i_min_continuous = req.target_torque_load / (m.m_cont * req.gear_efficiency);

        res.i_selected = std::max(res.i_optimal_inertia, res.i_min_continuous);

        const double omega_motor_req = req.target_omega_load * res.i_selected;
        if (omega_motor_req > m.omega_max) {
            res.i_selected = m.omega_max / req.target_omega_load;
        }

        res.motor_req_torque = req.target_torque_load / (res.i_selected * req.gear_efficiency);

        const double alpha_load = req.target_omega_load / req.accel_time;
        const double alpha_motor = alpha_load * res.i_selected;
        const double j_reflected = req.j_load / (res.i_selected * res.i_selected);

        const double j_total_motor = m.j_rotor + j_reflected / req.gear_efficiency;
        res.motor_accel_torque = j_total_motor * alpha_motor + res.motor_req_torque;

        res.is_feasible = (res.motor_req_torque <= m.m_cont) &&
                          (res.motor_accel_torque <= m.m_peak) &&
                          (omega_motor_req <= m.omega_max);

        return res;
    }

    // Розрахунок середньоквадратичного моменту за профільним циклом
    static double compute_rms_torque(std::span<const double> torques,
                                     std::span<const double> durations) noexcept
    {
        if (torques.empty() || torques.size() != durations.size()) {
            return 0.0;
        }
        double sum_sq = 0.0;
        double total_time = 0.0;
        for (std::size_t i = 0; i < torques.size(); ++i) {
            sum_sq += torques[i] * torques[i] * durations[i];
            total_time += durations[i];
        }
        return (total_time > 0.0) ? std::sqrt(sum_sq / total_time) : 0.0;
    }
};

} // namespace motor_sim
