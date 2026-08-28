#include "mcmc_engine.hpp"
#include <iostream>

int main() {
    mcmc::Config cfg{
        .num_states = 4,
        .temperature = 1.0,
        .burn_in_steps = 50'000,
        .sampling_steps = 2'000'000,
        .random_seed = 12345,
        .balance_tolerance = 1e-4
    };

    auto engine_res = mcmc::Engine::create(cfg);
    if (!engine_res) {
        std::cerr << "Помилка створення MCMC двигуна\n";
        return 1;
    }

    auto engine = std::move(*engine_res);
    const std::vector<double> energies = {0.0, 1.5, 3.0, 0.5};
    engine->set_energies(energies);

    if (engine->run() == mcmc::ErrorCode::InvalidParam) {
        return 1;
    }

    auto report = engine->verify_balance();
    std::cout << "Максимальний дисбаланс C++: " << report.max_imbalance_flux << "\n";
    std::cout << "Оцінка генерації ентропії dS/dt: " << report.entropy_production_rate << "\n";
    std::cout << "Детальний баланс підтверджено: " << (report.is_balanced ? "ТАК" : "НІ") << "\n";

    return 0;
}
