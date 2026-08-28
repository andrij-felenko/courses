#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <expected>
#include <span>
#include <iomanip>

namespace blackbody {

// Фізичні константи C++20
constexpr double h_planck = 6.62607015e-34;
constexpr double c_light  = 2.99792458e8;
constexpr double k_boltz  = 1.380649e-23;
constexpr double sigma_sb = 5.670374e-8;

enum class CalculationError {
    InvalidTemperature,
    InvalidWavelength,
    ConvergenceFailed
};

// Обчислення спектральної яскравості у стилі C++20
[[nodiscard]] constexpr double spectral_radiance(double lambda_m, double temp_k) noexcept {
    if (lambda_m <= 0.0 || temp_k <= 0.0) {
        return 0.0;
    }

    constexpr double c1 = 2.0 * h_planck * c_light * c_light;
    constexpr double c2 = (h_planck * c_light) / k_boltz;

    const double x = c2 / (lambda_m * temp_k);
    if (x > 700.0) {
        return 0.0;
    }

    const double denom = std::expm1(x);
    if (denom <= 0.0) {
        return 0.0;
    }

    const double lambda5 = std::pow(lambda_m, 5);
    return c1 / (lambda5 * denom);
}

// Генерація спектрального сімейства точок
[[nodiscard]] std::vector<std::pair<double, double>> generate_spectrum(
    double temp_k, double lambda_min, double lambda_max, std::size_t points) 
{
    std::vector<std::pair<double, double>> result;
    result.reserve(points);

    const double step = (lambda_max - lambda_min) / static_cast<double>(points - 1);
    for (std::size_t i = 0; i < points; ++i) {
        double lam = lambda_min + static_cast<double>(i) * step;
        result.emplace_back(lam, spectral_radiance(lam, temp_k));
    }
    return result;
}

// Чисельне інтегрування за методом Гаусса-Лежандра (2 точки на відрізок)
[[nodiscard]] double integrate_gauss(double temp_k, double a, double b, std::size_t intervals) {
    const double h = (b - a) / static_cast<double>(intervals);
    constexpr double x1 = -0.5773502691896257; // 1 / sqrt(3)
    constexpr double x2 =  0.5773502691896257;

    double total_integral = 0.0;
    for (std::size_t i = 0; i < intervals; ++i) {
        double t_a = a + static_cast<double>(i) * h;
        double t_b = t_a + h;
        double mid = (t_a + t_b) / 2.0;
        double half_h = h / 2.0;

        double lam1 = mid + half_h * x1;
        double lam2 = mid + half_h * x2;

        total_integral += half_h * (spectral_radiance(lam1, temp_k) + spectral_radiance(lam2, temp_k));
    }
    return total_integral;
}

} // namespace blackbody

int main() {
    constexpr double temp_sun = 5778.0;
    std::cout << std::setprecision(6) << std::fixed;
    std::cout << "--- Симуляція спектра чорного тіла (C++20) ---\n";

    double radiance_int = blackbody::integrate_gauss(temp_sun, 1.0e-8, 1.0e-5, 5000);
    double emittance = std::numbers::pi * radiance_int;
    double expected_emittance = blackbody::sigma_sb * std::pow(temp_sun, 4);

    std::cout << "Обчислена потужність: " << emittance << " Вт/м²\n";
    std::cout << "Закон Стефана-Больцмана: " << expected_emittance << " Вт/м²\n";
    std::cout << "Точність збігу: " << (100.0 - std::abs(emittance - expected_emittance) / expected_emittance * 100.0) << "%\n";

    return 0;
}
