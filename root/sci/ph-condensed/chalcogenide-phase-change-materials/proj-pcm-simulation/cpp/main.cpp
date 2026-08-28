#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <algorithm>
#include <stdexcept>
#include <span>

namespace pcm {

struct PcmParams {
    double length = 50e-9;
    double temp_bg = 300.0;
    double temp_melt = 873.0;
    double temp_glass = 473.0;
    double cp_base = 1.25e6;
    double latent_heat = 1.3e5;
    double density = 6150.0;
    double kappa_amo = 0.2;
    double kappa_cry = 0.5;
    double rho_amo = 1.0e-2;
    double rho_cry = 1.0e-5;
    double avrami_n = 3.0;
    double jmak_k0 = 1.0e11;
    double activation_energy = 2.4e-19;
};

class PcmSimulator {
private:
    PcmParams params_;
    std::size_t num_nodes_;
    double dx_;
    std::vector<double> temp_;
    std::vector<double> cryst_fraction_;

    [[nodiscard]] double get_effective_cp(double temp) const noexcept {
        constexpr double dt_melt = 5.0;
        if (std::abs(temp - params_.temp_melt) <= dt_melt) {
            double cp_latent = (params_.density * params_.latent_heat) / (2.0 * dt_melt);
            return params_.cp_base + cp_latent;
        }
        return params_.cp_base;
    }

    [[nodiscard]] double calc_jmak_k(double temp) const noexcept {
        if (temp < params_.temp_glass || temp >= params_.temp_melt) {
            return 0.0;
        }
        constexpr double kb = 1.380649e-23;
        double dt_norm = (temp - params_.temp_glass) / (params_.temp_melt - params_.temp_glass);
        double shape = 4.0 * dt_norm * (1.0 - dt_norm);
        return params_.jmak_k0 * std::exp(-params_.activation_energy / (kb * temp)) * shape;
    }

public:
    explicit PcmSimulator(std::size_t num_nodes, PcmParams params = {})
        : params_(params), num_nodes_(num_nodes) {
        if (num_nodes < 3) {
            throw std::invalid_argument("Кількість вузлів сітки повинна бути >= 3");
        }
        dx_ = params_.length / static_cast<double>(num_nodes - 1);
        temp_.assign(num_nodes, params_.temp_bg);
        cryst_fraction_.assign(num_nodes, 1.0); /* Початковий стан: кристалічний */
    }

    void simulate_step(double current_density, double dt) {
        std::vector<double> next_temp = temp_;

        /* 1. Динаміка фазового стану (JMAK та плавлення) */
        for (std::size_t i = 0; i < num_nodes_; ++i) {
            if (temp_[i] >= params_.temp_melt) {
                cryst_fraction_[i] = 0.0; /* Аморфізація через плавлення */
            } else {
                double x_curr = cryst_fraction_[i];
                if (x_curr < 0.999) {
                    double k_val = calc_jmak_k(temp_[i]);
                    if (k_val > 0.0) {
                        double n_av = params_.avrami_n;
                        double one_minus_x = std::max(1.0 - x_curr, 1e-6);
                        double ln_term = std::max(-std::log(one_minus_x), 1e-6);
                        double dx_dt = n_av * std::pow(k_val, 1.0 / n_av) * one_minus_x * std::pow(ln_term, (n_av - 1.0) / n_av);
                        cryst_fraction_[i] = std::min(1.0, cryst_fraction_[i] + dx_dt * dt);
                    }
                }
            }
        }

        /* 2. Дифузія тепла та Джоулів розігрів */
        for (std::size_t i = 1; i < num_nodes_ - 1; ++i) {
            double x_frac = cryst_fraction_[i];
            double kappa = x_frac * params_.kappa_cry + (1.0 - x_frac) * params_.kappa_amo;
            double rho = x_frac * params_.rho_cry + (1.0 - x_frac) * params_.rho_amo;
            double cp_eff = get_effective_cp(temp_[i]);

            double d2t_dx2 = (temp_[i + 1] - 2.0 * temp_[i] + temp_[i - 1]) / (dx_ * dx_);
            double joule_heat = current_density * current_density * rho;

            next_temp[i] = temp_[i] + (dt / cp_eff) * (kappa * d2t_dx2 + joule_heat);
        }

        temp_ = std::move(next_temp);
    }

    [[nodiscard]] std::span<const double> get_temperatures() const noexcept { return temp_; }
    [[nodiscard]] std::span<const double> get_crystallinity() const noexcept { return cryst_fraction_; }
};

} // namespace pcm

int main() {
    try {
        pcm::PcmParams params;
        pcm::PcmSimulator sim(51, params);

        std::cout << "--- Симуляція теплового профілю PCRAM (C++) ---\n";
        constexpr double j_reset = 1.5e11;
        constexpr double dt = 1e-13;

        for (int step = 0; step < 50000; ++step) {
            sim.simulate_step(j_reset, dt);
        }

        auto temps = sim.get_temperatures();
        auto cryst = sim.get_crystallinity();

        std::cout << "Температура в центрі комірки: " << temps[25] << " K\n";
        std::cout << "Кристалічність у центрі: " << cryst[25] << "\n";

    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
