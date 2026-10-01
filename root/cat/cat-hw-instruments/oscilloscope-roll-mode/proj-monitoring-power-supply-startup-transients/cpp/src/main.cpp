#include "roll_mode_analyzer.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "=== C++ Аналізатор часових рядів осцилографа у режимі Roll Mode ===\n\n";

    // 1. Формування тестового масиву вибірок перехідного процесу живлення
    std::vector<roll_mode::Sample> psu_samples = {
        {0.0, 0.00, 0.00},
        {0.2, 7.10, 2.50}, // Перерегулювання напруги при ввімкненні
        {0.4, 4.10, 1.80}, // Просідання
        {0.6, 5.35, 2.10}, // Викид поза коридор 5% (4.75 В .. 5.25 В)
        {0.8, 5.05, 2.01}, // Вхід у коридор
        {1.0, 4.98, 2.00},
        {1.2, 5.01, 2.00}
    };

    roll_mode::RollModeAnalyzer psu_analyzer(psu_samples);
    const double steady_v = 5.00;
    const double tolerance = 5.0; // 5%

    auto stab_res = psu_analyzer.analyzeStabilization(steady_v, tolerance);
    if (stab_res.is_stabilized) {
        std::cout << "[1] Аналіз стабілізації джерела живлення:\n";
        std::cout << "    Цільова напруга: " << std::fixed << std::setprecision(2) << steady_v << " В (допуск ±" << tolerance << "%)\n";
        std::cout << "    Час виходу на режим (settling time): " << stab_res.settling_time_sec << " с\n\n";
    }

    // 2. Симуляція тривалого розряду акумулятора в режимі Roll Mode
    std::vector<roll_mode::Sample> battery_samples = {
        {0.0,    4.20, 1.50}, // Початок розряду (1.5 А)
        {600.0,  4.05, 1.48}, // Через 10 хв
        {1200.0, 3.90, 1.45}, // Через 20 хв
        {1800.0, 3.75, 1.42}, // Через 30 хв
        {2400.0, 3.50, 1.40}  // Через 40 хв
    };

    roll_mode::RollModeAnalyzer battery_analyzer(battery_samples);
    auto bati_res = battery_analyzer.calculateDischargedCapacity();

    std::cout << "[2] Оцінка розряду акумуляторної батареї:\n";
    std::cout << "    Тривалість запису: " << std::fixed << std::setprecision(1) << bati_res.total_time_sec << " с (" 
              << (bati_res.total_time_sec / 60.0) << " хв)\n";
    std::cout << "    Віддана ємність: " << std::setprecision(4) << bati_res.capacity_amp_hours << " А·год ("
              << (bati_res.capacity_amp_hours * 1000.0) << " мА·год)\n";
    std::cout << "    Віддана енергія: " << std::setprecision(4) << bati_res.energy_watt_hours << " Вт·год\n";

    return 0;
}
