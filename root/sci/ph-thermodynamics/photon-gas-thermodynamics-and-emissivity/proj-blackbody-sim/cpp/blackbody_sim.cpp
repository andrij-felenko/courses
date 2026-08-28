// blackbody_sim.cpp — Ідіоматична реалізація чисельного аналізу спектрів на C++20.
// Компіляція: g++ -O2 -std=c++20 blackbody_sim.cpp -o blackbody_sim

#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <iomanip>

namespace blackbody {

// Константи CODATA 2018 у constexpr
constexpr double h_planck = 6.626'070'15e-34;  // Дж*с
constexpr double c_light  = 2.997'924'58e8;    // м/с
constexpr double k_boltz  = 1.380'649e-23;     // Дж/К
constexpr double stefan_b = 5.670'374'419e-8;  // Вт/(м^2*К^4)

enum class CalculationError {
    InvalidTemperature,
    InvalidWavelength,
    Overflow
};

// Обчислення спектральної випромінювальної здатності Планка R(lambda, T)
[[nodiscard]] constexpr auto planck_radiance(double lambda_m, double temp_k) 
    -> std::expected<double, CalculationError> 
{
    if (temp_k <= 0.0) {
        return std::unexpected(CalculationError::InvalidTemperature);
    }
    if (lambda_m <= 0.0) {
        return std::unexpected(CalculationError::InvalidWavelength);
    }

    const double arg = (h_planck * c_light) / (lambda_m * k_boltz * temp_k);
    if (arg > 700.0) {
        return 0.0; // Експоненційний спад до нуля при малих довжинах хвиль
    }

    const double denom = std::exp(arg) - 1.0;
    if (denom <= 0.0) {
        return std::unexpected(CalculationError::Overflow);
    }

    const double num = 2.0 * std::numbers::pi * h_planck * c_light * c_light;
    const double lambda5 = std::pow(lambda_m, 5);
    return num / (lambda5 * denom);
}

// Чисельне інтегрування за методом Симпсона
[[nodiscard]] auto integrate_spectrum(double temp_k, double lam_start, double lam_end, std::size_t intervals = 10000) 
    -> double 
{
    if (intervals % 2 != 0) {
        intervals++;
    }
    
    const double step = (lam_end - lam_start) / static_cast<double>(intervals);
    double sum = planck_radiance(lam_start, temp_k).value_or(0.0) 
               + planck_radiance(lam_end, temp_k).value_or(0.0);

    for (std::size_t i = 1; i < intervals; ++i) {
        const double lam = lam_start + static_cast<double>(i) * step;
        const double weight = (i % 2 == 0) ? 2.0 : 4.0;
        sum += weight * planck_radiance(lam, temp_k).value_or(0.0);
    }

    return (step / 3.0) * sum;
}

// Знаходження піку випромінювання (закон Віна) методом Ньютона
[[nodiscard]] auto wien_peak_wavelength(double temp_k) -> double {
    double x = 4.96511423;
    for (int iter = 0; iter < 10; ++iter) {
        const double f = 5.0 * (1.0 - std::exp(-x)) - x;
        const double df = 5.0 * std::exp(-x) - 1.0;
        x -= f / df;
    }
    return (h_planck * c_light) / (k_boltz * temp_k * x);
}

// Оцінка температури зорі за відношенням інтенсивностей на двох хвилях R(lambda1) / R(lambda2)
[[nodiscard]] auto estimate_color_temperature(double lambda1, double lambda2, double ratio_measured) -> double {
    double t_low = 1000.0;
    double t_high = 40000.0;
    
    for (int iter = 0; iter < 30; ++iter) {
        double t_mid = 0.5 * (t_low + t_high);
        double r1 = planck_radiance(lambda1, t_mid).value_or(1.0);
        double r2 = planck_radiance(lambda2, t_mid).value_or(1.0);
        double ratio_sim = r1 / r2;
        
        if (ratio_sim < ratio_measured) {
            t_low = t_mid;
        } else {
            t_high = t_mid;
        }
    }
    return 0.5 * (t_low + t_high);
}

} // namespace blackbody

int main() {
    constexpr double temp_sun = 5778.0;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== C++20 МОДЕЛЮВАННЯ СПЕКТРА ЧОРНОГО ТІЛА ===\n\n";

    const double peak_lam = blackbody::wien_peak_wavelength(temp_sun);
    std::cout << "1. Пік випромінювання Віна для T = " << temp_sun << " K: "
              << peak_lam * 1e9 << " нм\n\n";

    // Аналіз по точках
    const std::vector<double> sample_wavelengths_nm{300.0, 400.0, 500.0, 600.0, 700.0, 1000.0};
    std::cout << "2. Спектральні значення R(lambda):\n";
    for (double lam_nm : sample_wavelengths_nm) {
        auto radiance = blackbody::planck_radiance(lam_nm * 1e-9, temp_sun);
        if (radiance) {
            std::cout << "   λ = " << std::setw(5) << lam_nm << " нм -> R = "
                      << std::scientific << *radiance << " Вт/(м^2*м)\n" << std::fixed;
        }
    }

    // Інтегрування
    const double integrated_flux = blackbody::integrate_spectrum(temp_sun, 1e-9, 50e-6);
    const double theoretical_flux = blackbody::stefan_b * std::pow(temp_sun, 4);

    std::cout << "\n3. Перевірка закону Стефана-Больцмана:\n";
    std::cout << "   Чисельний інтеграл: " << std::scientific << integrated_flux << " Вт/м^2\n";
    std::cout << "   Теоретичний потік: " << theoretical_flux << " Вт/м^2\n";
    std::cout << "   Точність: " << std::fixed << (100.0 * (1.0 - integrated_flux / theoretical_flux)) << "%\n";

    // Тест визначення температури зорі
    constexpr double lam_blue = 440e-9;  // B-фільтр
    constexpr double lam_red  = 640e-9;  // R-фільтр
    double r_blue = blackbody::planck_radiance(lam_blue, temp_sun).value_or(1.0);
    double r_red  = blackbody::planck_radiance(lam_red, temp_sun).value_or(1.0);
    double measured_ratio = r_blue / r_red;

    double estimated_temp = blackbody::estimate_color_temperature(lam_blue, lam_red, measured_ratio);
    std::cout << "\n4. Метод колірної температури (оцінка за виміряним відношенням B/R):\n";
    std::cout << "   Задана T = " << temp_sun << " K, відновлена T = " << estimated_temp << " K\n";

    return 0;
}
