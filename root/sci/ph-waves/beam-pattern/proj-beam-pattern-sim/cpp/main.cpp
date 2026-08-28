#include <iostream>
#include <vector>
#include <cmath>
#include <complex>
#include <span>
#include <string_view>
#include <algorithm>
#include <numbers>
#include <iomanip>
#include <expected>

struct TransducerConfig {
    double freq_hz{40000.0};
    double sound_speed{1500.0};
    double aperture_d{0.15};
    std::size_t num_elements{16};
    double elem_spacing{0.01875}; // lambda / 2
    double steer_angle_deg{0.0};
};

struct BeamMetrics {
    double beamwidth_3db_deg{0.0};
    double sll_db{-100.0};
    double first_null_deg{0.0};
};

struct SimulationResult {
    std::vector<double> angles_deg;
    std::vector<double> pattern_db;
    BeamMetrics metrics;
};

class BeamPatternSimulator {
public:
    static double bessel_j1(double x) noexcept {
        const double ax = std::abs(x);
        if (ax < 3.75) {
            const double y = (x / 3.75) * (x / 3.75);
            return x * (0.5 + y * (-0.56249985 + y * (0.21093573 + 
                         y * (-0.03954289 + y * (0.00443319 + y * -0.00031761)))));
        }
        const double y = 3.75 / ax;
        const double f1 = 0.79788456 + y * (-0.00000077 + y * (-0.00552740 + 
                    y * (0.00095120 + y * (-0.00066738 + y * 0.00015649))));
        const double theta1 = ax - 2.35619449 + y * (0.04166397 + y * (-0.00003954 + 
                        y * (0.00262573 + y * (-0.00054125 + y * 0.00029333))));
        const double ans = (1.0 / std::sqrt(ax)) * f1 * std::cos(theta1);
        return (x < 0.0) ? -ans : ans;
    }

    static std::expected<SimulationResult, std::string_view>
    simulate(const TransducerConfig& config, std::size_t num_points = 361) {
        if (num_points < 2 || config.freq_hz <= 0.0 || config.sound_speed <= 0.0) {
            return std::unexpected("Некоректні вхідні параметри симуляції");
        }

        SimulationResult res;
        res.angles_deg.resize(num_points);
        res.pattern_db.resize(num_points);

        const double lambda = config.sound_speed / config.freq_hz;
        const double k = 2.0 * std::numbers::pi / lambda;
        const double steer_rad = config.steer_angle_deg * std::numbers::pi / 180.0;

        double max_val = 0.0;
        std::size_t peak_idx = 0;

        for (std::size_t i = 0; i < num_points; ++i) {
            const double theta_deg = -90.0 + (180.0 * static_cast<double>(i) / static_cast<double>(num_points - 1));
            res.angles_deg[i] = theta_deg;
            const double theta_rad = theta_deg * std::numbers::pi / 180.0;

            double r_val = 0.0;
            if (config.num_elements > 1) {
                const double psi = k * config.elem_spacing * (std::sin(theta_rad) - std::sin(steer_rad));
                if (std::abs(psi) < 1e-6) {
                    r_val = 1.0;
                } else {
                    const double num = std::sin(static_cast<double>(config.num_elements) * psi / 2.0);
                    const double den = static_cast<double>(config.num_elements) * std::sin(psi / 2.0);
                    r_val = std::abs(num / den);
                }
            } else {
                const double radius = config.aperture_d / 2.0;
                const double v = k * radius * std::sin(theta_rad);
                r_val = (std::abs(v) < 1e-6) ? 1.0 : std::abs(2.0 * bessel_j1(v) / v);
            }

            if (r_val > max_val) {
                max_val = r_val;
                peak_idx = i;
            }

            res.pattern_db[i] = 20.0 * std::log10(std::max(r_val, 1e-4));
        }

        // Нормалізація дБ відносно піку
        const double max_db = res.pattern_db[peak_idx];
        for (auto& val : res.pattern_db) {
            val -= max_db;
        }

        // Знаходження параметрів променя
        double left_3db = res.angles_deg.front();
        double right_3db = res.angles_deg.back();

        for (std::size_t i = peak_idx; i > 0; --i) {
            if (res.pattern_db[i] <= -3.0) {
                left_3db = res.angles_deg[i];
                break;
            }
        }
        for (std::size_t i = peak_idx; i < num_points; ++i) {
            if (res.pattern_db[i] <= -3.0) {
                right_3db = res.angles_deg[i];
                break;
            }
        }
        res.metrics.beamwidth_3db_deg = right_3db - left_3db;

        // Пошук SLL
        double sll_max = -100.0;
        bool in_main = true;
        for (std::size_t i = peak_idx; i < num_points - 1; ++i) {
            if (in_main) {
                if (res.pattern_db[i + 1] > res.pattern_db[i] && res.pattern_db[i] < -15.0) {
                    in_main = false;
                }
            } else {
                sll_max = std::max(sll_max, res.pattern_db[i]);
            }
        }
        res.metrics.sll_db = sll_max;

        return res;
    }
};

int main() {
    TransducerConfig array_cfg{
        .freq_hz = 100000.0,       // 100 кГц
        .sound_speed = 1500.0,     // Вода
        .aperture_d = 0.1,
        .num_elements = 16,        // Фазований масив 16 елементів
        .elem_spacing = 0.0075,    // lambda / 2
        .steer_angle_deg = 20.0    // Відхилення променя на 20 градусів
    };

    auto sim_res = BeamPatternSimulator::simulate(array_cfg);

    if (sim_res) {
        const auto& data = sim_res.value();
        std::cout << "=== Результати симуляції фазованої решітки (C++) ===\n";
        std::cout << "Частота: " << array_cfg.freq_hz / 1000.0 << " кГц, Елементів: " 
                  << array_cfg.num_elements << "\n";
        std::cout << "Кут сканування: " << array_cfg.steer_angle_deg << "°\n";
        std::cout << "Ширина променя (-3 dB): " << std::fixed << std::setprecision(2) 
                  << data.metrics.beamwidth_3db_deg << "°\n";
        std::cout << "Рівень бічних пелюсток (SLL): " << data.metrics.sll_db << " dB\n";

        std::cout << "\nПрофіль діаграми (вибіркові кути):\n";
        for (std::size_t i = 0; i < data.angles_deg.size(); i += 36) {
            std::cout << "  Кут " << std::setw(6) << data.angles_deg[i] 
                      << "° : " << std::setw(6) << data.pattern_db[i] << " dB\n";
        }
    } else {
        std::cerr << "Помилка: " << sim_res.error() << "\n";
    }

    return 0;
}
