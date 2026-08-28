#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

class AcousticFDTD1D {
public:
    struct MediumProps {
        double impedance; // Pa*s/m
        double speed;     // m/s
    };

    AcousticFDTD1D(std::size_t grid_size, double dx, double dt)
        : grid_size_(grid_size), dx_(dx), dt_(dt),
          p_(grid_size, 0.0), v_(grid_size, 0.0),
          rho_(grid_size, 1000.0), K_(grid_size, 2.25e9), c_(grid_size, 1500.0) {}

    void setup_interfaces(MediumProps m1, MediumProps m2, bool add_quarter_wave_layer) {
        const std::size_t interface_pos = grid_size_ / 2;
        const double rho1 = m1.impedance / m1.speed;
        const double K1 = m1.impedance * m1.speed;

        const double rho2 = m2.impedance / m2.speed;
        const double K2 = m2.impedance * m2.speed;

        const double z_match = std::sqrt(m1.impedance * m2.impedance);
        const double rho_m = z_match / m1.speed;
        const double K_m = z_match * m1.speed;

        const double freq = 1.0e6; // 1 MHz
        const double lambda_m = m1.speed / freq;
        const std::size_t layer_cells = std::max<std::size_t>(1, static_cast<std::size_t>((lambda_m / 4.0) / dx_));

        for (std::size_t i = 0; i < grid_size_; ++i) {
            if (i < interface_pos) {
                rho_[i] = rho1;
                K_[i] = K1;
                c_[i] = m1.speed;
            } else if (add_quarter_wave_layer && i < (interface_pos + layer_cells)) {
                rho_[i] = rho_m;
                K_[i] = K_m;
                c_[i] = m1.speed;
            } else {
                rho_[i] = rho2;
                K_[i] = K2;
                c_[i] = m2.speed;
            }
        }
    }

    void step(std::size_t current_step) {
        const double p0_old = p_[0];
        const double p1_old = p_[1];
        const double pN1_old = p_[grid_size_ - 1];
        const double pN2_old = p_[grid_size_ - 2];

        // Update velocity v
        for (std::size_t i = 0; i < grid_size_ - 1; ++i) {
            const double rho_avg = 0.5 * (rho_[i] + rho_[i + 1]);
            v_[i] -= (dt_ / (rho_avg * dx_)) * (p_[i + 1] - p_[i]);
        }

        // Update pressure p
        for (std::size_t i = 1; i < grid_size_ - 1; ++i) {
            p_[i] -= (dt_ * K_[i] / dx_) * (v_[i] - v_[i - 1]);
        }

        // Mur 1st Order Absorbing Boundary Conditions
        const double gamma0 = (c_[0] * dt_ - dx_) / (c_[0] * dt_ + dx_);
        p_[0] = p1_old + gamma0 * (p_[1] - p0_old);

        const double gammaN = (c_[grid_size_ - 1] * dt_ - dx_) / (c_[grid_size_ - 1] * dt_ + dx_);
        p_[grid_size_ - 1] = pN2_old + gammaN * (p_[grid_size_ - 2] - pN1_old);

        // Gaussian pulse injection
        const double t = current_step * dt_;
        const double t0 = 35.0 * dt_;
        const double spread = 10.0 * dt_;
        const double src = std::exp(-0.5 * std::pow((t - t0) / spread, 2));
        p_[100] += src;
    }

    [[nodiscard]] double get_pressure(std::size_t idx) const {
        return p_.at(idx);
    }

private:
    std::size_t grid_size_;
    double dx_;
    double dt_;
    std::vector<double> p_;
    std::vector<double> v_;
    std::vector<double> rho_;
    std::vector<double> K_;
    std::vector<double> c_;
};

int main() {
    constexpr std::size_t grid_size = 1000;
    constexpr double dx = 0.0001; // 0.1 mm
    constexpr double dt = 3.0e-8; // 30 ns
    constexpr std::size_t total_steps = 1400;

    AcousticFDTD1D direct_sim(grid_size, dx, dt);
    AcousticFDTD1D matched_sim(grid_size, dx, dt);

    const AcousticFDTD1D::MediumProps water_like{1.5e6, 1500.0};
    const AcousticFDTD1D::MediumProps bone_like{6.0e6, 1500.0};

    direct_sim.setup_interfaces(water_like, bone_like, false);
    matched_sim.setup_interfaces(water_like, bone_like, true);

    for (std::size_t step = 0; step < total_steps; ++step) {
        direct_sim.step(step);
        matched_sim.step(step);
    }

    const double direct_reflected = std::abs(direct_sim.get_pressure(300));
    const double matched_reflected = std::abs(matched_sim.get_pressure(300));

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Результати C++ FDTD моделювання ===\n";
    std::cout << "Амплітуда відбиття (без узгодження): " << direct_reflected << '\n';
    std::cout << "Амплітуда відбиття (з чвертьхвильовим шаром): " << matched_reflected << '\n';
    std::cout << "Приглушення відбитої хвилі: "
              << (1.0 - matched_reflected / direct_reflected) * 100.0 << "%\n";

    return 0;
}
