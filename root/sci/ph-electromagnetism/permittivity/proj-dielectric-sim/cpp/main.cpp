#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <iomanip>
#include <numbers>

struct DielectricPoint {
    double freq_hz;
    double omega;
    std::complex<double> eps_star;
    double tan_delta;
    double alpha_atten;
};

class DielectricSimulator {
public:
    static constexpr double c_speed = 299792458.0;

    // Ідіоматичний чисельний алгоритм на основі std::complex та std::vector
    static std::vector<DielectricPoint> simulate_debye(
        double eps_s, double eps_inf, double tau,
        double f_min, double f_max, std::size_t num_points)
    {
        std::vector<DielectricPoint> result;
        if (num_points <= 1 || f_min <= 0.0 || f_max <= f_min) {
            return result;
        }

        result.reserve(num_points);
        const double log_f_min = std::log10(f_min);
        const double log_f_max = std::log10(f_max);
        const double step = (log_f_max - log_f_min) / static_cast<double>(num_points - 1);

        for (std::size_t i = 0; i < num_points; ++i) {
            const double f = std::pow(10.0, log_f_min + static_cast<double>(i) * step);
            const double omega = 2.0 * std::numbers::pi * f;
            
            // Комплексна проникність ε*(ω) = ε_inf + (ε_s - ε_inf) / (1 + i*ω*τ)
            const std::complex<double> i_omega_tau(0.0, omega * tau);
            const std::complex<double> eps_star = eps_inf + (eps_s - eps_inf) / (1.0 + i_omega_tau);

            const double e_prime = eps_star.real();
            const double e_double_prime = -eps_star.imag(); // уявна частина як втрати
            const double tan_d = e_double_prime / e_prime;

            const double term = std::sqrt(1.0 + tan_d * tan_d);
            const double alpha = (omega / c_speed) * std::sqrt((e_prime / 2.0) * (term - 1.0));

            result.push_back({f, omega, eps_star, tan_d, alpha});
        }

        return result;
    }
};

int main() {
    // Симуляція спектра чистої води при 20°C (eps_s = 80.1, eps_inf = 4.9, tau = 9.36 ps)
    const auto data = DielectricSimulator::simulate_debye(80.1, 4.9, 9.36e-12, 1e8, 1e11, 7);

    std::cout << std::scientific << std::setprecision(3);
    std::cout << " Частота (Гц)   |   ε' (накоп)  |   ε'' (втрати) |  tan(δ)   |  α (1/м)\n";
    std::cout << "-----------------------------------------------------------------------\n";

    for (const auto& pt : data) {
        std::cout << "  " << std::setw(10) << pt.freq_hz << "  |  "
                  << std::fixed << std::setprecision(4) << std::setw(11) << pt.eps_star.real() << "  |  "
                  << std::setw(12) << -pt.eps_star.imag() << "  |  "
                  << std::setw(7) << pt.tan_delta << "  |  "
                  << std::setprecision(2) << std::setw(9) << pt.alpha_atten << "\n";
    }

    return 0;
}
