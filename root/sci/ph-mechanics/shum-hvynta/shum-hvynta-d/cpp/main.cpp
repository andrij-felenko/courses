#include <iostream>
#include <cmath>
#include <numbers>
#include <algorithm>

namespace aeroacoustics {

// Обчислення циліндричної функції Бесселя першого роду J_n(x)
[[nodiscard]] constexpr double bessel_j(int n, double x) noexcept {
    if (x == 0.0) return (n == 0) ? 1.0 : 0.0;
    const double half_x = 0.5 * x;
    double term = 1.0;
    for (int i = 1; i <= n; ++i) term *= (half_x / static_cast<double>(i));
    double sum = term;
    const double half_x_sq = half_x * half_x;
    for (int k = 1; k < 50; ++k) {
        term *= -half_x_sq / (static_cast<double>(k) * static_cast<double>(n + k));
        sum += term;
        if (std::abs(term) < 1e-14 * std::abs(sum)) break;
    }
    return sum;
}

// Розрахунок RMS звукового тиску гармоніки Гутіна
[[nodiscard]] double compute_gutin_pressure(int harmonic_m, int num_blades_B, 
                                           double rpm, double thrust_N, 
                                           double torque_Nm, double radius_m, 
                                           double distance_m, double theta_deg) noexcept {
    constexpr double kSoundSpeed = 343.0; // м/с
    const double n_rps = rpm / 60.0;
    const double omega = 2.0 * std::numbers::pi * n_rps;
    const double r_eff = 0.80 * radius_m;
    const double m_eff = (omega * r_eff) / kSoundSpeed;
    
    const double theta_rad = theta_deg * std::numbers::pi / 180.0;
    const double sin_theta = std::sin(theta_rad);
    const double cos_theta = std::cos(theta_rad);
    
    const int order = harmonic_m * num_blades_B;
    const double arg_bessel = static_cast<double>(order) * m_eff * sin_theta;
    const double j_val = bessel_j(order, arg_bessel);
    
    const double bracket = -thrust_N * cos_theta + (kSoundSpeed * torque_Nm) / (omega * r_eff * r_eff);
    const double factor = (static_cast<double>(order) * omega) / 
                          (2.0 * std::numbers::sqrt2 * std::numbers::pi * kSoundSpeed * distance_m);
                          
    return std::abs(factor * bracket * j_val);
}

} // namespace aeroacoustics
