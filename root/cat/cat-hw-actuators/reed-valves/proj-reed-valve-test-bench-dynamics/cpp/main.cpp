#include <iostream>
#include <vector>
#include <iomanip>
#include "reed_valve.hpp"

int main() {
    try {
        std::cout << "=== Аналіз роботи пелюсткового клапана мікрогідравліки ===" << std::endl;

        // Ініціалізація аналізатора: коеф. витрати 0.65, площа 1.5e-5 м^2, густина оливи 850 кг/м^3
        ReedValveAnalyzer analyzer(0.65, 1.5e-5, 850.0);
        SignalFilter filter(0.2); // Фільтр з коефіцієнтом згладжування 0.2

        // Симульовані зашумлені дані перепаду тиску на клапані (Па) за кілька тактів стендових випробувань
        std::vector<double> raw_pressures = {12000.0, 45000.0, 110000.0, 95000.0, 60000.0, 20000.0, 5000.0};
        std::vector<double> filtered_pressures;
        filtered_pressures.reserve(raw_pressures.size());

        std::cout << "\nПотокова фільтрація сигналів тиску:" << std::endl;
        for (size_t i = 0; i < raw_pressures.size(); ++i) {
            double filtered = filter.update(raw_pressures[i]);
            filtered_pressures.push_back(filtered);
            std::cout << "Вимір " << i + 1 << ": Сирий = " << std::setw(8) << raw_pressures[i] 
                      << " Па | Відфільтрований = " << std::setw(8) << std::fixed << std::setprecision(1) << filtered << " Па" << std::endl;
        }

        // Розрахунок інтегрального зворотного об'єму витоку за крок часу dt = 0.01 с
        double dt = 0.01;
        double backflow_volume = analyzer.calculateIntegralBackflow(filtered_pressures, dt);

        // Оцінка оптимальної резонансної жорсткості пелюстки при частоті 50 Гц
        double max_p = *std::max_element(filtered_pressures.begin(), filtered_pressures.end());
        double optimal_stiffness = analyzer.estimateOptimalStiffness(max_p, 50.0);

        std::cout << "\n--- Результати гідравлічного розрахунку ---" << std::endl;
        std::cout << "Інтегральний зворотний об'єм витоку: " << std::scientific << std::setprecision(4) << backflow_volume << " м^3" << std::endl;
        std::cout << "Оціночна оптимальна жорсткість пелюстки: " << std::fixed << std::setprecision(2) << optimal_stiffness << " Н/м" << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
