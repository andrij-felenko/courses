#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <complex>

struct SourceParameters {
    double width_mm{2.0};
    double height_mm{2.0};
    double distance_R_mm{1000.0};
    double wavelength_nm{500.0};
};

struct CoherenceDataPoint {
    double slit_separation_mm;
    double degree_of_coherence;
    double fringe_visibility;
};

// Сучасний клас C++20 для розрахунку просторової когерентності за теоремою Ван Ціттерта — Церніке
class SpatialCoherenceSimulator {
private:
    SourceParameters params_;
    double wavelength_mm_;

public:
    explicit SpatialCoherenceSimulator(const SourceParameters& params)
        : params_(params), wavelength_mm_(params.wavelength_nm * 1e-6) {}

    // Обчислення просторової когерентності методом 2D чисельного інтегрування
    [[nodiscard]] double evaluate_coherence(double dx_mm, double dy_mm, std::size_t integration_steps = 120) const {
        std::complex<double> integral_sum{0.0, 0.0};
        double total_power{0.0};

        const double step_x = params_.width_mm / static_cast<double>(integration_steps);
        const double step_y = params_.height_mm / static_cast<double>(integration_steps);
        const double k = 2.0 * std::numbers::pi / wavelength_mm_;

        for (std::size_t ix = 0; ix < integration_steps; ++ix) {
            const double xi = -params_.width_mm / 2.0 + (static_cast<double>(ix) + 0.5) * step_x;
            for (std::size_t iy = 0; iy < integration_steps; ++iy) {
                const double eta = -params_.height_mm / 2.0 + (static_cast<double>(iy) + 0.5) * step_y;

                const double phase = k * (dx_mm * xi + dy_mm * eta) / params_.distance_R_mm;
                const double cell_area = step_x * step_y;
                
                // Рівномірний розподіл інтенсивності джерела I(xi, eta) = 1.0
                constexpr double intensity = 1.0;
                integral_sum += intensity * std::exp(std::complex<double>{0.0, -phase}) * cell_area;
                total_power += intensity * cell_area;
            }
        }

        return std::abs(integral_sum) / total_power;
    }

    // Генерація повного профілю просторової когерентності
    [[nodiscard]] std::vector<CoherenceDataPoint> generate_profile(double max_d_mm, std::size_t points_count) const {
        std::vector<CoherenceDataPoint> profile;
        profile.reserve(points_count);

        const double step = max_d_mm / static_cast<double>(points_count - 1);
        for (std::size_t i = 0; i < points_count; ++i) {
            const double d = static_cast<double>(i) * step;
            const double gamma_val = evaluate_coherence(d, 0.0);
            profile.push_back({
                .slit_separation_mm = d,
                .degree_of_coherence = gamma_val,
                .fringe_visibility = gamma_val
            });
        }
        return profile;
    }
};

int main() {
    const SourceParameters config{.width_mm = 1.5, .height_mm = 1.5, .distance_R_mm = 1200.0, .wavelength_nm = 632.8};
    const SpatialCoherenceSimulator simulator(config);
    
    const auto coherence_results = simulator.generate_profile(0.6, 13);

    std::cout << "--- Просторова когерентність (Обчислення на C++20) ---\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Відстань d (мм) | |gamma_12| | Видність V\n";
    std::cout << "--------------------------------------\n";

    for (const auto& entry : coherence_results) {
        std::cout << "   " << std::setw(6) << entry.slit_separation_mm 
                  << "       | " << entry.degree_of_coherence 
                  << " | " << entry.fringe_visibility << "\n";
    }

    return 0;
}
