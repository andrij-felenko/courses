#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <numbers>
#include <iomanip>
#include <algorithm>

struct HeterodyneConfig {
    double sample_rate{1.0e9};   // 1 ГГц частота дискретизації
    double f_if{100.0e6};        // 100 МГц проміжна частота
    double p_signal{1.0e-9};     // 1 нВт сигнальна потужність
    double p_lo{1.0e-3};         // 1 мВт потужність гетеродина
    double responsivity{0.85};   // 0.85 А/Вт чутливість фотодіода
    std::size_t num_samples{2000};
};

class HeterodyneDemodulator {
public:
    explicit HeterodyneDemodulator(HeterodyneConfig config)
        : cfg_(config), rng_(1337) {}

    void process() {
        const double dt = 1.0 / cfg_.sample_rate;
        const double i_lo = cfg_.responsivity * cfg_.p_lo;
        constexpr double q_elem = 1.602176634e-19;
        const double shot_std = std::sqrt(2.0 * q_elem * i_lo * (cfg_.sample_rate / 2.0));
        const double peak_beat = 2.0 * cfg_.responsivity * std::sqrt(cfg_.p_signal * cfg_.p_lo);

        std::normal_distribution<double> noise_dist(0.0, shot_std);

        std::vector<double> i_raw(cfg_.num_samples);
        std::vector<double> q_raw(cfg_.num_samples);

        for (std::size_t k = 0; k < cfg_.num_samples; ++k) {
            const double t = k * dt;
            const double target_phase = (t > (cfg_.num_samples * dt / 2.0)) ? std::numbers::pi / 2.0 : 0.0;

            const double beat = peak_beat * std::cos(2.0 * std::numbers::pi * cfg_.f_if * t + target_phase);
            const double i_bal = beat + noise_dist(rng_);

            i_raw[k] = i_bal * std::cos(2.0 * std::numbers::pi * cfg_.f_if * t);
            q_raw[k] = i_bal * (-std::sin(2.0 * std::numbers::pi * cfg_.f_if * t));
        }

        // Низькочастотне ковзне фільтрування
        const int win = std::max(1, static_cast<int>(cfg_.sample_rate / (cfg_.f_if * 2.0)));
        std::vector<double> phase_rec(cfg_.num_samples);

        for (std::size_t k = 0; k < cfg_.num_samples; ++k) {
            double sum_i = 0.0, sum_q = 0.0;
            int count = 0;
            for (int w = -win; w <= win; ++w) {
                int idx = static_cast<int>(k) + w;
                if (idx >= 0 && idx < static_cast<int>(cfg_.num_samples)) {
                    sum_i += i_raw[idx];
                    sum_q += q_raw[idx];
                    count++;
                }
            }
            phase_rec[k] = std::atan2(sum_q / count, sum_i / count);
        }

        print_results(phase_rec, dt);
    }

private:
    void print_results(const std::vector<double>& phase_rec, double dt) const {
        std::cout << "=== СИМУЛЯЦІЯ ОПТИЧНОГО ГЕТЕРОДИНА (C++) ===\n";
        std::cout << std::scientific << std::setprecision(2);
        std::cout << "P_signal: " << cfg_.p_signal << " W | P_LO: " << cfg_.p_lo << " W\n";
        std::cout << "Час (мкс) | Відновлена фаза | Цільова фаза\n";
        std::cout << "-------------------------------------------\n";

        const std::size_t step = cfg_.num_samples / 5;
        std::cout << std::fixed << std::setprecision(4);
        for (std::size_t k = step / 2; k < cfg_.num_samples; k += step) {
            const double t_us = (k * dt) * 1e6;
            const double target = (k * dt > (cfg_.num_samples * dt / 2.0)) ? std::numbers::pi / 2.0 : 0.0;
            std::cout << std::setw(9) << t_us << " | " << std::setw(15) << phase_rec[k]
                      << " | " << std::setw(12) << target << "\n";
        }
    }

    HeterodyneConfig cfg_;
    std::mt19937_64 rng_;
};

int main() {
    HeterodyneConfig config{};
    HeterodyneDemodulator demod(config);
    demod.process();
    return 0;
}
