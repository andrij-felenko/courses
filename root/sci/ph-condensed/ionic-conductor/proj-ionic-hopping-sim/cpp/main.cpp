#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <stdexcept>

struct SimulationParameters {
    double temperature_k{500.0};
    double activation_energy_ev{0.4};
    double electric_field_v_m{1.0e5};
    double lattice_constant_m{3.0e-10};
    double attempt_frequency_hz{1.0e12};
    std::size_t ion_count{10000};
    std::size_t step_count{1000};
    double time_step_s{1.0e-9};
};

struct SimulationOutcome {
    double mean_displacement_m{0.0};
    double mean_square_displacement_m2{0.0};
    double drift_velocity_m_s{0.0};
    double diffusion_coefficient_m2_s{0.0};
    double Nernst_Einstein_ratio{0.0};
    double theoretical_ratio{0.0};
};

class IonicHoppingSimulator {
public:
    explicit IonicHoppingSimulator(SimulationParameters params)
        : params_(params), rng_(std::random_device{}()) {}

    SimulationOutcome run() {
        constexpr double kb_ev_k = 8.61733326e-5;
        constexpr double elementary_charge_e = 1.0;

        const double field_energy_shift_ev = 
            (elementary_charge_e * params_.lattice_constant_m * params_.electric_field_v_m) / 2.0;

        const double forward_barrier = params_.activation_energy_ev - field_energy_shift_ev;
        const double backward_barrier = params_.activation_energy_ev + field_energy_shift_ev;

        const double nu_forward = params_.attempt_frequency_hz * std::exp(-forward_barrier / (kb_ev_k * params_.temperature_k));
        const double nu_backward = params_.attempt_frequency_hz * std::exp(-backward_barrier / (kb_ev_k * params_.temperature_k));

        const double p_forward = nu_forward * params_.time_step_s;
        const double p_backward = nu_backward * params_.time_step_s;

        if (p_forward + p_backward >= 1.0) {
            throw std::runtime_error("Time step dt is too large for stable Monte Carlo simulation.");
        }

        std::vector<double> ion_positions(params_.ion_count, 0.0);
        std::uniform_real_distribution<double> dist(0.0, 1.0);

        for (std::size_t step = 0; step < params_.step_count; ++step) {
            for (auto& pos : ion_positions) {
                const double roll = dist(rng_);
                if (roll < p_forward) {
                    pos += params_.lattice_constant_m;
                } else if (roll < p_forward + p_backward) {
                    pos -= params_.lattice_constant_m;
                }
            }
        }

        SimulationOutcome outcome;
        double sum_x = 0.0;
        double sum_x2 = 0.0;

        for (const double pos : ion_positions) {
            sum_x += pos;
            sum_x2 += pos * pos;
        }

        const double total_time_s = params_.step_count * params_.time_step_s;
        outcome.mean_displacement_m = sum_x / static_cast<double>(params_.ion_count);
        outcome.mean_square_displacement_m2 = sum_x2 / static_cast<double>(params_.ion_count);
        outcome.drift_velocity_m_s = outcome.mean_displacement_m / total_time_s;

        const double variance = outcome.mean_square_displacement_m2 - (outcome.mean_displacement_m * outcome.mean_displacement_m);
        outcome.diffusion_coefficient_m2_s = variance / (2.0 * total_time_s);

        constexpr double kb_joules_k = 1.380649e-23;
        constexpr double charge_coulombs = 1.60217663e-19;
        outcome.theoretical_ratio = charge_coulombs / (kb_joules_k * params_.temperature_k);
        const double simulated_mobility = outcome.drift_velocity_m_s / params_.electric_field_v_m;
        outcome.Nernst_Einstein_ratio = simulated_mobility / outcome.diffusion_coefficient_m2_s;

        return outcome;
    }

private:
    SimulationParameters params_;
    std::mt19937_64 rng_;
};

int main() {
    try {
        SimulationParameters params;
        params.temperature_k = 500.0;
        params.activation_energy_ev = 0.35;
        params.electric_field_v_m = 5.0e4;
        params.ion_count = 20000;
        params.step_count = 2000;

        IonicHoppingSimulator simulator(params);
        SimulationOutcome outcome = simulator.run();

        std::cout << std::scientific << std::setprecision(4);
        std::cout << "=== Результати моделювання Monte Carlo (C++17) ===\n";
        std::cout << "Температура T:          " << params.temperature_k << " K\n";
        std::cout << "Середній зсув <x>:      " << outcome.mean_displacement_m << " м\n";
        std::cout << "Дрейфова швидкість v:   " << outcome.drift_velocity_m_s << " м/с\n";
        std::cout << "Коефіцієнт дифузії D:   " << outcome.diffusion_coefficient_m2_s << " м²/с\n";
        std::cout << "Теоретичне q/(k_B*T):   " << outcome.theoretical_ratio << " В⁻¹\n";
        std::cout << "Отримане в симуляції μ/D: " << outcome.Nernst_Einstein_ratio << " В⁻¹\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
