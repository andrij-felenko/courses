#include <iostream>
#include "libthermo_phase.hpp"

int main() {
    thermo::PhaseSystemConfig config;
    config.species_names = {"CH4", "H2O", "CO", "CO2", "H2"};
    config.num_phases = 1;
    config.is_condensed = false;
    config.num_constraints = 0;

    // Матриця 2 x 5 двох незалежних реакцій
    config.stoich_matrix = {
        {-1.0, -1.0,  1.0,  0.0,  3.0}, // CH4 + H2O ⇌ CO + 3 H2
        { 0.0, -1.0, -1.0,  1.0,  1.0}  // CO + H2O ⇌ CO2 + H2
    };

    thermo::PhaseRuleCalculator calc(1e-9);
    auto result_exp = calc.analyze(config);

    if (result_exp.has_value()) {
        const auto& res = result_exp.value();
        std::cout << "--- Аналіз фазової рівноваги (C++ API) ---\n";
        std::cout << "Ранг реакцій R: " << res.rank_reactions << "\n";
        std::cout << "Компоненти Гіббса K: " << res.gibbs_components << "\n";
        std::cout << "Ступені вільності F: " << res.degrees_of_freedom << "\n";
        std::cout << "Статус: " << res.description << "\n";
        std::cout << "Чи вілідна рівновага: " << (res.is_valid() ? "Так" : "Ні") << "\n";
    } else {
        std::cout << "Помилка обчислень: " 
                  << thermo::PhaseRuleCalculator::status_to_string(result_exp.error()) 
                  << "\n";
    }

    return 0;
}
