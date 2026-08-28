#include <iostream>
#include <complex>
#include <cmath>
#include <numbers>
#include <iomanip>

struct FresnelResult {
    std::complex<double> r_s;
    std::complex<double> r_p;
    std::complex<double> t_s;
    std::complex<double> t_p;
    double R_s;
    double R_p;
    double T_s;
    double T_p;
    double R_avg;
    double phase_s_deg;
    double phase_p_deg;
};

[[nodiscard]] FresnelResult calculate_fresnel(std::complex<double> n1, 
                                              std::complex<double> n2, 
                                              double theta1_deg) noexcept {
    const double theta1_rad = theta1_deg * std::numbers::pi / 180.0;
    const std::complex<double> cos_t1{std::cos(theta1_rad), 0.0};
    const std::complex<double> sin_t1{std::sin(theta1_rad), 0.0};

    const std::complex<double> sin_t2 = (n1 / n2) * sin_t1;
    std::complex<double> cos_t2 = std::sqrt(1.0 - sin_t2 * sin_t2);

    if (cos_t2.real() < 0.0) {
        cos_t2 = -cos_t2;
    }

    const auto r_s = (n1 * cos_t1 - n2 * cos_t2) / (n1 * cos_t1 + n2 * cos_t2);
    const auto t_s = (2.0 * n1 * cos_t1) / (n1 * cos_t1 + n2 * cos_t2);

    const auto r_p = (n2 * cos_t1 - n1 * cos_t2) / (n2 * cos_t1 + n1 * cos_t2);
    const auto t_p = (2.0 * n1 * cos_t1) / (n2 * cos_t1 + n1 * cos_t2);

    const double R_s = std::norm(r_s);
    const double R_p = std::norm(r_p);
    const double R_avg = 0.5 * (R_s + R_p);

    const double phase_s_deg = std::arg(r_s) * 180.0 / std::numbers::pi;
    const double phase_p_deg = std::arg(r_p) * 180.0 / std::numbers::pi;

    const std::complex<double> factor = (n2 * cos_t2) / (n1 * cos_t1);
    double real_factor = factor.real();
    if (real_factor < 0.0) real_factor = 0.0;

    const double T_s = real_factor * std::norm(t_s);
    const double T_p = real_factor * std::norm(t_p);

    return {r_s, r_p, t_s, t_p, R_s, R_p, T_s, T_p, R_avg, phase_s_deg, phase_p_deg};
}

int main() {
    using namespace std::complex_literals;

    std::cout << std::fixed << std::setprecision(4);

    const std::complex<double> n_air{1.0, 0.0};
    const std::complex<double> n_glass{1.5, 0.0};

    const auto res_glass = calculate_fresnel(n_air, n_glass, 45.0);

    std::cout << "=== Межа Повітря -> Скло (45 deg) ===\n";
    std::cout << "R_s: " << res_glass.R_s << " (" << res_glass.R_s * 100.0 << "%)\n";
    std::cout << "R_p: " << res_glass.R_p << " (" << res_glass.R_p * 100.0 << "%)\n";
    std::cout << "R_avg: " << res_glass.R_avg << " (" << res_glass.R_avg * 100.0 << "%)\n";

    const std::complex<double> n_gold = 0.18 + 3.43i;
    const auto res_gold = calculate_fresnel(n_air, n_gold, 0.0);

    std::cout << "\n=== Межа Повітря -> Золото при 0 deg ===\n";
    std::cout << "R: " << res_gold.R_s << " (" << res_gold.R_s * 100.0 << "%)\n";

    return 0;
}
