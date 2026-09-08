#include "cardan_kinematics.hpp"
#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>

int main() {
    using namespace cardan;

    std::cout << "========================================================================\n";
    std::cout << "REAL-TIME CARDAN DRIVETRAIN KINEMATICS & DYNAMICS (C++17)\n";
    std::cout << "========================================================================\n\n";

    constexpr double rpm = 1500.0;
    constexpr double omega1 = rpm * (TWO_PI / 60.0);
    constexpr double beta_deg = 12.0;
    constexpr double beta = beta_deg * (PI / 180.0);
    constexpr double j_load = 0.02; // кг*м^2

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Input speed: " << rpm << " RPM (" << omega1 << " rad/s)\n";
    std::cout << "Joint angle: beta = " << beta_deg << " deg\n";
    std::cout << "Load inertia: J_load = " << j_load << " kg*m^2\n\n";

    // 1. Одиночний шарнір
    std::cout << "1. SINGLE HOOKE JOINT TEST (1 kHz control cycle over 1 revolution):\n";
    constexpr int steps = 360;
    double w_min_s = 1e9, w_max_s = -1e9, a_max_s = 0.0, t_dyn_max_s = 0.0;

    for (int i = 0; i < steps; ++i) {
        const double phi1 = i * (TWO_PI / steps);
        const ShaftState s = CardanKinematics<double>::evaluate_single_joint(phi1, omega1, beta, j_load);
        if (s.omega < w_min_s) w_min_s = s.omega;
        if (s.omega > w_max_s) w_max_s = s.omega;
        if (std::abs(s.alpha) > a_max_s) a_max_s = std::abs(s.alpha);
        if (std::abs(s.torque_dyn) > t_dyn_max_s) t_dyn_max_s = std::abs(s.torque_dyn);
    }

    const double pulsation_s = (w_max_s - w_min_s) / omega1 * 100.0;
    std::cout << "   Output speed range: [" << w_min_s << " ... " << w_max_s << "] rad/s\n";
    std::cout << "   Speed ripple (pulsation): " << pulsation_s << " %\n";
    std::cout << "   Peak angular acceleration: " << a_max_s << " rad/s^2\n";
    std::cout << "   Peak dynamic torque: +/-" << t_dyn_max_s << " N*m\n\n";

    // 2. Здвоєний кардан у Z-схемі (повна компенсація)
    std::cout << "2. DOUBLE CARDAN IN Z-CONFIGURATION (gamma = 0 deg):\n";
    DrivetrainConfig cfg_z{beta, beta, 0.0, j_load};
    double w_min_z = 1e9, w_max_z = -1e9, t_dyn_max_z = 0.0;

    for (int i = 0; i < steps; ++i) {
        const double phi1 = i * (TWO_PI / steps);
        const ShaftState s = CardanKinematics<double>::evaluate_double_drivetrain(phi1, omega1, cfg_z);
        if (s.omega < w_min_z) w_min_z = s.omega;
        if (s.omega > w_max_z) w_max_z = s.omega;
        if (std::abs(s.torque_dyn) > t_dyn_max_z) t_dyn_max_z = std::abs(s.torque_dyn);
    }

    const double pulsation_z = (w_max_z - w_min_z) / omega1 * 100.0;
    std::cout << "   Output speed range: [" << w_min_z << " ... " << w_max_z << "] rad/s\n";
    std::cout << "   Speed ripple: " << std::setprecision(6) << pulsation_z << " % (fully cancelled)\n";
    std::cout << "   Peak dynamic torque: " << t_dyn_max_z << " N*m\n\n";

    // 3. Здвоєний кардан із розфазуванням вилок на 90 градусів (помилка складання)
    std::cout << std::setprecision(2);
    std::cout << "3. MISPHASED DOUBLE CARDAN (gamma = 90 deg, assembly defect):\n";
    DrivetrainConfig cfg_bad{beta, beta, PI / 2.0, j_load};
    double w_min_b = 1e9, w_max_b = -1e9, t_dyn_max_b = 0.0;

    for (int i = 0; i < steps; ++i) {
        const double phi1 = i * (TWO_PI / steps);
        const ShaftState s = CardanKinematics<double>::evaluate_double_drivetrain(phi1, omega1, cfg_bad);
        if (s.omega < w_min_b) w_min_b = s.omega;
        if (s.omega > w_max_b) w_max_b = s.omega;
        if (std::abs(s.torque_dyn) > t_dyn_max_b) t_dyn_max_b = std::abs(s.torque_dyn);
    }

    const double pulsation_b = (w_max_b - w_min_b) / omega1 * 100.0;
    std::cout << "   Output speed range: [" << w_min_b << " ... " << w_max_b << "] rad/s\n";
    std::cout << "   Speed ripple: " << pulsation_b << " % (DOUBLED RIPPLE)\n";
    std::cout << "   Peak dynamic torque: +/-" << t_dyn_max_b << " N*m\n";
    std::cout << "========================================================================\n";

    return 0;
}
