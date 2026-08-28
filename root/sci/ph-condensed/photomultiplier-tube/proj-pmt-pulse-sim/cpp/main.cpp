#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <algorithm>

struct PMTConfig {
    double quantum_efficiency = 0.25; // 25% квантова ефективність
    double dynode_gain = 4.0;         // Середнє підсилення одного дінода (δ)
    std::size_t num_dynodes = 10;     // Кількість дінодів N
    double t_rise_ns = 1.2;           // Час фронту імпульсу (нс)
    double t_fall_ns = 3.5;           // Час спаду імпульсу (нс)
    double dt_ns = 0.1;               // Крок дискретизації часу (нс)
    double noise_sigma_mV = 0.5;      // Шуми електронного підсилювача (мВ)
    double cfd_fraction = 0.2;        // Частка CFD (20%)
};

class PMTSimulator {
public:
    explicit PMTSimulator(const PMTConfig& config) 
        : cfg_(config), rng_(std::random_device{}()) {}

    // Стохастична симуляція каскаду дінодів
    std::uint64_t simulate_cascade(std::size_t num_photoelectrons) {
        std::uint64_t current_electrons = num_photoelectrons;
        for (std::size_t d = 0; d < cfg_.num_dynodes; ++d) {
            if (current_electrons == 0) break;
            std::poisson_distribution<std::uint64_t> dist(current_electrons * cfg_.dynode_gain);
            current_electrons = dist(rng_);
        }
        return current_electrons;
    }

    // Генерація оцифрованого аналогового сигналу анода
    std::vector<double> generate_pulse(std::uint64_t total_anode_electrons, double total_time_ns) {
        std::size_t num_samples = static_cast<std::size_t>(total_time_ns / cfg_.dt_ns);
        std::vector<double> voltage(num_samples, 0.0);

        if (total_anode_electrons == 0) return voltage;

        constexpr double e_charge = 1.602e-19;
        double Q_coulomb = static_cast<double>(total_anode_electrons) * e_charge;
        double R_load = 50.0;
        std::normal_distribution<double> noise_dist(0.0, cfg_.noise_sigma_mV);

        for (std::size_t i = 0; i < num_samples; ++i) {
            double t = static_cast<double>(i) * cfg_.dt_ns;
            if (t > 0.0) {
                double shape = (t / cfg_.t_rise_ns) * std::exp(1.0 - t / cfg_.t_rise_ns);
                double current_A = (Q_coulomb / (cfg_.t_fall_ns * 1e-9)) * shape;
                voltage[i] = (current_A * R_load * 1e3) + noise_dist(rng_);
            } else {
                voltage[i] = noise_dist(rng_);
            }
        }
        return voltage;
    }

    // Алгоритм CFD-дискримінації для знаходження точки перетину нуля
    double find_cfd_zero_crossing(const std::vector<double>& waveform) {
        std::size_t delay_samples = static_cast<std::size_t>((cfg_.t_rise_ns * (1.0 - cfg_.cfd_fraction)) / cfg_.dt_ns);
        std::vector<double> cfd_signal(waveform.size(), 0.0);

        for (std::size_t i = 0; i < waveform.size(); ++i) {
            double delayed = (i >= delay_samples) ? waveform[i - delay_samples] : 0.0;
            double attenuated = cfg_.cfd_fraction * waveform[i];
            cfd_signal[i] = delayed - attenuated;
        }

        // Пошук нульового перетину
        for (std::size_t i = 1; i < cfd_signal.size(); ++i) {
            if (cfd_signal[i - 1] < 0.0 && cfd_signal[i] >= 0.0) {
                // Лінійна інтерполяція часу перетину
                double t1 = static_cast<double>(i - 1) * cfg_.dt_ns;
                double t2 = static_cast<double>(i) * cfg_.dt_ns;
                double y1 = cfd_signal[i - 1];
                double y2 = cfd_signal[i];
                return t1 + (0.0 - y1) * (t2 - t1) / (y2 - y1);
            }
        }
        return -1.0; // Нуль не знайдено
    }

private:
    PMTConfig cfg_;
    std::mt19937 rng_;
};

int main() {
    PMTConfig config;
    PMTSimulator sim(config);

    std::size_t primary_photons = 5;
    std::uint64_t anode_electrons = sim.simulate_cascade(primary_photons);

    std::cout << "=== Симуляція анодного імпульсу ФЕУ та CFD-таймінгу ===\n";
    std::cout << "Кількість первинних фотоелектронів: " << primary_photons << "\n";
    std::cout << "Загальний заряд на аноді (електронів): " << anode_electrons << "\n";
    std::cout << "Коефіцієнт підсилення каскаду M: " << std::scientific << static_cast<double>(anode_electrons) / primary_photons << "\n";

    auto waveform = sim.generate_pulse(anode_electrons, 25.0);
    double cfd_time = sim.find_cfd_zero_crossing(waveform);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "\nРезультат CFD дискримінації:\n";
    std::cout << "Точний час прильоту фотона (Zero-Crossing): " << cfd_time << " нс\n";

    std::cout << "\nФорма оцифрованої напруги анода (перші 10 відліків):\n";
    for (std::size_t i = 0; i < 10 && i < waveform.size(); ++i) {
        std::cout << "t = " << i * config.dt_ns << " нс: " << waveform[i] << " мВ\n";
    }

    return 0;
}
