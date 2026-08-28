// C++ Implementation — Modern RAII Wave Diffraction Calculator
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <stdexcept>

class DiffractionSolver {
public:
    using Complex = std::complex<double>;

    struct Config {
        double wavelength = 632.8e-9; // Довжина хвилі (м)
        double aperture_size = 0.2e-3; // Ширина щілини (м)
        double screen_size = 0.04;     // Розмір екрана (м)
        std::size_t grid_aperture = 500;
        std::size_t grid_screen = 400;
    };

    explicit DiffractionSolver(Config cfg) : config_(cfg) {
        if (config_.wavelength <= 0.0 || config_.aperture_size <= 0.0) {
            throw std::invalid_argument("Некоректні фізичні параметри апертури!");
        }
    }

    // Обчислення дифракції Фраунгофера (далеке поле)
    [[nodiscard]] std::vector<double> computeFraunhofer(double distance_z) const {
        if (distance_z <= 0.0) {
            throw std::invalid_argument("Відстань z має бути додатною!");
        }

        std::vector<double> intensity(config_.grid_screen, 0.0);
        const double k = 2.0 * std::numbers::pi / config_.wavelength;
        const double dx_in = (config_.aperture_size * 3.0) / static_cast<double>(config_.grid_aperture);
        const double dx_out = config_.screen_size / static_cast<double>(config_.grid_screen);

        for (std::size_t i = 0; i < config_.grid_screen; ++i) {
            const double x_out = -config_.screen_size / 2.0 + static_cast<double>(i) * dx_out;
            const double sin_theta = x_out / std::hypot(x_out, distance_z);

            Complex field_sum{0.0, 0.0};
            for (std::size_t j = 0; j < config_.grid_aperture; ++j) {
                const double x_in = -(config_.aperture_size * 1.5) + static_cast<double>(j) * dx_in;
                if (std::abs(x_in) <= config_.aperture_size / 2.0) {
                    const double phase = -k * sin_theta * x_in;
                    field_sum += std::polar(1.0, phase);
                }
            }
            field_sum *= dx_in;
            intensity[i] = std::norm(field_sum) / (config_.wavelength * distance_z);
        }
        return intensity;
    }

    // Обчислення дифракції Френеля (близьке поле)
    [[nodiscard]] std::vector<double> computeFresnel(double distance_z) const {
        if (distance_z <= 0.0) {
            throw std::invalid_argument("Відстань z має бути додатною!");
        }

        std::vector<double> intensity(config_.grid_screen, 0.0);
        const double phase_coeff = std::numbers::pi / (config_.wavelength * distance_z);
        const double dx_in = (config_.aperture_size * 3.0) / static_cast<double>(config_.grid_aperture);
        const double dx_out = config_.screen_size / static_cast<double>(config_.grid_screen);

        for (std::size_t i = 0; i < config_.grid_screen; ++i) {
            const double x_out = -config_.screen_size / 2.0 + static_cast<double>(i) * dx_out;

            Complex field_sum{0.0, 0.0};
            for (std::size_t j = 0; j < config_.grid_aperture; ++j) {
                const double x_in = -(config_.aperture_size * 1.5) + static_cast<double>(j) * dx_in;
                if (std::abs(x_in) <= config_.aperture_size / 2.0) {
                    const double diff_x = x_out - x_in;
                    const double phase = phase_coeff * (diff_x * diff_x);
                    field_sum += std::polar(1.0, phase);
                }
            }
            field_sum *= dx_in;
            intensity[i] = std::norm(field_sum) / (config_.wavelength * distance_z);
        }
        return intensity;
    }

private:
    Config config_;
};

int main() {
    try {
        DiffractionSolver::Config cfg{.wavelength = 632.8e-9, .aperture_size = 0.2e-3, .screen_size = 0.04};
        DiffractionSolver solver(cfg);

        auto fraunhofer_pattern = solver.computeFraunhofer(2.0);
        auto fresnel_pattern = solver.computeFresnel(0.08);

        std::cout << "Фраунгофер I_max: " << fraunhofer_pattern[fraunhofer_pattern.size() / 2] << " Вт/м²\n";
        std::cout << "Френель I_center: " << fresnel_pattern[fresnel_pattern.size() / 2] << " Вт/м²\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
