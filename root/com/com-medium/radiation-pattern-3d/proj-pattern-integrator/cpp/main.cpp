#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

struct PatternResults {
    double p_rad{0.0};
    double u_max{0.0};
    double directivity{1.0};
    double directivity_dbi{0.0};
    double beam_solid_angle{4.0 * std::numbers::pi};
};

class RadiationPattern3D {
public:
    RadiationPattern3D(std::size_t num_theta, std::size_t num_phi)
        : num_theta_(num_theta), num_phi_(num_phi),
          delta_theta_(std::numbers::pi / static_cast<double>(num_theta - 1)),
          delta_phi_((2.0 * std::numbers::pi) / static_cast<double>(num_phi - 1)),
          grid_(num_theta, std::vector<double>(num_phi, 0.0)) {}

    void set_intensity(std::size_t i, std::size_t j, double value) {
        grid_.at(i).at(j) = value;
    }

    [[nodiscard]] double get_intensity(std::size_t i, std::size_t j) const {
        return grid_.at(i).at(j);
    }

    [[nodiscard]] PatternResults compute_directivity() const {
        PatternResults res;
        double p_sum = 0.0;
        double max_u = 0.0;

        for (std::size_t i = 0; i < num_theta_; ++i) {
            const double theta = static_cast<double>(i) * delta_theta_;
            const double sin_th = std::sin(theta);
            const double w_theta = (i == 0 || i == num_theta_ - 1) ? 0.5 : 1.0;

            for (std::size_t j = 0; j < num_phi_; ++j) {
                const double u_val = grid_[i][j];
                max_u = std::max(max_u, u_val);

                const double w_phi = (j == 0 || j == num_phi_ - 1) ? 0.5 : 1.0;
                const double d_omega = sin_th * (w_theta * delta_theta_) * (w_phi * delta_phi_);
                p_sum += u_val * d_omega;
            }
        }

        res.p_rad = p_sum;
        res.u_max = max_u;
        if (p_sum > 1e-12 && max_u > 0.0) {
            res.directivity = (4.0 * std::numbers::pi * max_u) / p_sum;
            res.directivity_dbi = 10.0 * std::log10(res.directivity);
            res.beam_solid_angle = (4.0 * std::numbers::pi) / res.directivity;
        }
        return res;
    }

private:
    std::size_t num_theta_;
    std::size_t num_phi_;
    double delta_theta_;
    double delta_phi_;
    std::vector<std::vector<double>> grid_;
};

int main() {
    constexpr std::size_t n_th = 181;
    constexpr std::size_t n_ph = 361;

    RadiationPattern3D pattern(n_th, n_ph);

    // Симуляція 3D-діаграми напівхвильового диполя
    for (std::size_t i = 0; i < n_th; ++i) {
        const double theta = static_cast<double>(i) * (std::numbers::pi / static_cast<double>(n_th - 1));
        const double sin_th = std::sin(theta);
        const double u_val = sin_th * sin_th * sin_th;
        for (std::size_t j = 0; j < n_ph; ++j) {
            pattern.set_intensity(i, j, u_val);
        }
    }

    const auto res = pattern.compute_directivity();

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "--- Результати 3D-інтегрування диполя (C++) ---\n";
    std::cout << "Повна потужність P_rad: " << res.p_rad << " Вт\n";
    std::cout << "Макс. інтенсивність U_max: " << res.u_max << " Вт/ср\n";
    std::cout << "КСД (Directivity):        " << res.directivity << " (теорія: 1.643)\n";
    std::cout << "Підсилення (dBi):         " << res.directivity_dbi << " дБі (теорія: 2.15 дБі)\n";
    std::cout << "Тілесний кут Omega_A:     " << res.beam_solid_angle << " ср\n";

    return 0;
}
