#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <span>
#include <numbers>

struct HuygensSource {
    double x{0.0};
    double y{0.0};
    double amplitude{1.0};
    double phase_shift{0.0};
};

struct ScreenResult {
    double y{0.0};
    double intensity{0.0};
};

/**
 * Ідіоматична C++ реалізація чисельного симулятора Гюйгенса.
 */
class HuygensSimulator {
public:
    struct Config {
        double wavelength{0.5e-6};
        double slit_width{5.0e-6};
        std::size_t num_sources{200};
        double screen_distance{50e-6};
        double screen_width{80e-6};
        std::size_t num_screen_pts{400};
    };

    explicit HuygensSimulator(Config config) : config_(config) {}

    [[nodiscard]] std::vector<ScreenResult> run() const {
        const double k = 2.0 * std::numbers::pi / config_.wavelength;
        std::vector<HuygensSource> sources = generate_sources();
        std::vector<ScreenResult> results(config_.num_screen_pts);

        const double dy_scr = (config_.num_screen_pts > 1) 
            ? (config_.screen_width / static_cast<double>(config_.num_screen_pts - 1)) 
            : 0.0;
        const double start_y_scr = -config_.screen_width / 2.0;
        const double eps = std::pow(config_.wavelength / 20.0, 2);

        double max_intensity = 0.0;

        for (std::size_t i = 0; i < config_.num_screen_pts; ++i) {
            const double px = config_.screen_distance;
            const double py = start_y_scr + static_cast<double>(i) * dy_scr;
            std::complex<double> total_field{0.0, 0.0};

            for (const auto& src : sources) {
                const double dx = px - src.x;
                const double dy = py - src.y;
                const double r = std::sqrt(dx * dx + dy * dy + eps);
                const double cos_theta = dx / r;
                const double k_factor = 0.5 * (1.0 + cos_theta);

                const double phase = k * r + src.phase_shift - (std::numbers::pi / 2.0);
                const double amp = (src.amplitude / std::sqrt(r)) * k_factor;

                total_field += std::polar(amp, phase);
            }

            const double intensity = std::norm(total_field);
            results[i] = {py, intensity};
            max_intensity = std::max(max_intensity, intensity);
        }

        if (max_intensity > 0.0) {
            for (auto& res : results) {
                res.intensity /= max_intensity;
            }
        }

        return results;
    }

private:
    [[nodiscard]] std::vector<HuygensSource> generate_sources() const {
        std::vector<HuygensSource> sources(config_.num_sources);
        const double dy = (config_.num_sources > 1) 
            ? (config_.slit_width / static_cast<double>(config_.num_sources - 1)) 
            : 0.0;
        const double start_y = -config_.slit_width / 2.0;
        const double norm_amp = 1.0 / static_cast<double>(config_.num_sources);

        for (std::size_t n = 0; n < config_.num_sources; ++n) {
            sources[n] = {
                .x = 0.0,
                .y = start_y + static_cast<double>(n) * dy,
                .amplitude = norm_amp,
                .phase_shift = 0.0
            };
        }
        return sources;
    }

    Config config_;
};

int main() {
    HuygensSimulator simulator({});
    auto profile = simulator.run();

    std::cout << "C++ симуляцію успішно виконано. Отримано " << profile.size() << " точок.\n";
    std::cout << "Центральна інтенсивність I(0) = " << profile[profile.size() / 2].intensity << "\n";
    return 0;
}
