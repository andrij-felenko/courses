#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <string_view>
#include <iomanip>

struct FabryPerotConfig {
    double gap_d_m{0.001};        // Відстань між дзеркалами
    double ref_index{1.0};        // Показник заломлення
    double reflectivity{0.90};    // Коефіцієнт відбиття R

    [[nodiscard]] constexpr double f_coeff() const noexcept {
        const double loss = 1.0 - reflectivity;
        return (4.0 * reflectivity) / (loss * loss);
    }
};

struct EtalonMetrics {
    double fsr_frequency_hz;
    double fsr_wavelength_m;
    double finesse;
    double fwhm_wavelength_m;
};

class FabryPerotSimulator {
public:
    enum class ValidationError {
        InvalidGap,
        InvalidReflectivity,
        InvalidWavelengthRange
    };

    static std::expected<EtalonMetrics, ValidationError> compute_metrics(
        const FabryPerotConfig& cfg, double center_lambda_m) noexcept 
    {
        if (cfg.gap_d_m <= 0.0) return std::unexpected(ValidationError::InvalidGap);
        if (cfg.reflectivity <= 0.0 || cfg.reflectivity >= 1.0) {
            return std::unexpected(ValidationError::InvalidReflectivity);
        }

        constexpr double c = 299792458.0;
        EtalonMetrics m{};
        m.fsr_frequency_hz = c / (2.0 * cfg.ref_index * cfg.gap_d_m);
        m.fsr_wavelength_m = (center_lambda_m * center_lambda_m) / (2.0 * cfg.ref_index * cfg.gap_d_m);
        m.finesse = (std::numbers::pi * std::sqrt(cfg.reflectivity)) / (1.0 - cfg.reflectivity);
        m.fwhm_wavelength_m = m.fsr_wavelength_m / m.finesse;

        return m;
    }

    [[nodiscard]] static double airy_transmission(
        const FabryPerotConfig& cfg, double lambda_m, double theta_rad = 0.0) noexcept 
    {
        const double delta = (4.0 * std::numbers::pi * cfg.ref_index * cfg.gap_d_m * std::cos(theta_rad)) / lambda_m;
        const double sin_half = std::sin(delta / 2.0);
        return 1.0 / (1.0 + cfg.f_coeff() * sin_half * sin_half);
    }

    static std::vector<double> generate_spectrum(
        const FabryPerotConfig& cfg, std::span<const double> wavelengths_m) 
    {
        std::vector<double> transmission;
        transmission.reserve(wavelengths_m.size());
        for (double lambda : wavelengths_m) {
            transmission.push_back(airy_transmission(cfg, lambda));
        }
        return transmission;
    }

    // Розрахунок двомірної картини кілець на матричному детекторі N x N
    static std::vector<double> generate_2d_rings(
        const FabryPerotConfig& cfg, double lambda_m, double focal_length_m, 
        double sensor_width_m, size_t resolution_pixels) 
    {
        std::vector<double> image(resolution_pixels * resolution_pixels);
        const double pixel_size = sensor_width_m / static_cast<double>(resolution_pixels);
        const double half_size = sensor_width_m / 2.0;

        for (size_t y = 0; y < resolution_pixels; ++y) {
            const double py = (y * pixel_size) - half_size;
            for (size_t x = 0; x < resolution_pixels; ++x) {
                const double px = (x * pixel_size) - half_size;
                const double r = std::hypot(px, py);
                const double theta = std::atan2(r, focal_length_m);
                image[y * resolution_pixels + x] = airy_transmission(cfg, lambda_m, theta);
            }
        }
        return image;
    }
};

int main() {
    constexpr FabryPerotConfig config{
        .gap_d_m = 1.0e-3,       // 1.0 мм повітряний проміжок
        .ref_index = 1.0,
        .reflectivity = 0.92     // R = 92%
    };

    constexpr double lambda_center = 1550.0e-9; // 1550 нм телеком-діапазон
    auto metrics = FabryPerotSimulator::compute_metrics(config, lambda_center);

    if (!metrics) {
        std::cerr << "Помилка конфігурації еталона!\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== РЕЗОНАТОР ФАБРІ — ПЕРО (C++23) ===\n";
    std::cout << "FSR (частота): " << metrics->fsr_frequency_hz / 1e9 << " ГГц\n";
    std::cout << "FSR (довжина хвилі): " << metrics->fsr_wavelength_m * 1e9 << " нм\n";
    std::cout << "Різкість (Finesse): " << metrics->finesse << "\n";
    std::cout << "FWHM піку: " << metrics->fwhm_wavelength_m * 1e9 << " нм\n\n";

    // Створення сітки довжин хвиль
    constexpr int steps = 11;
    constexpr double start_wl = 1550.0e-9;
    constexpr double end_wl = 1551.2e-9;
    
    std::vector<double> wl_grid(steps);
    for (int i = 0; i < steps; ++i) {
        wl_grid[i] = start_wl + i * (end_wl - start_wl) / (steps - 1);
    }

    auto spectrum = FabryPerotSimulator::generate_spectrum(config, wl_grid);

    for (size_t i = 0; i < wl_grid.size(); ++i) {
        std::cout << std::setw(8) << wl_grid[i] * 1e9 << " нм | ";
        const int bars = static_cast<int>(spectrum[i] * 35.0);
        std::cout << std::string(bars, '*') << " (" << spectrum[i] * 100.0 << "%)\n";
    }

    return 0;
}
