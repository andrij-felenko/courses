#include "include/sir_analyzer.hpp"
#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>

int main() {
    try {
        std::cout << "=== Аналіз SIR-тестування безвідмивного флюсу FVS-7 (IPC-TM-650) ===" << std::endl;

        flux_testing::SirTimeSeriesAnalyzer analyzer("FVS-7 No-Clean Flux", 1.0e8);

        std::vector<flux_testing::SirSample> test_data;
        
        for (int i = 0; i <= 24; ++i) {
            double t = i * 7.0;
            double base_r = 5.0e10;
            
            if (t < 24.0) {
                base_r = 5.0e10 - (t / 24.0) * 3.0e10;
            } else {
                base_r = 3.5e10 + std::sin(t / 10.0) * 5.0e9;
            }

            if (i == 10) {
                base_r = 4.0e7; // Помилковий аномальний імпульсний викид
            }

            test_data.push_back({t, 100.0, base_r});
        }

        std::cout << "[1] Завантаження " << test_data.size() << " вимірювань часового ряду SIR..." << std::endl;
        analyzer.add_samples(test_data);

        std::cout << "[2] Виконання медіанної фільтрації та виявлення мінімумів..." << std::endl;
        flux_testing::SirReport report = analyzer.generate_report(3);

        std::cout << std::scientific << std::setprecision(3);
        std::cout << "\n--------------------------------------------------" << std::endl;
        std::cout << "Підсумковий звіт чистоти матеріалу: " << report.flux_name << std::endl;
        std::cout << "--------------------------------------------------" << std::endl;
        std::cout << "Оброблено точок вимірювання : " << report.total_samples << std::endl;
        std::cout << "Початковий опір SIR (t=0h)  : " << report.initial_sir_ohms << " Ом (" << report.initial_sir_ohms / 1.0e9 << " ГОм)" << std::endl;
        std::cout << "Фінальний опір SIR (t=168h) : " << report.final_sir_ohms << " Ом (" << report.final_sir_ohms / 1.0e9 << " ГОм)" << std::endl;
        std::cout << "Глобальний мінімум опору    : " << report.global_min_ohms << " Ом (" << report.global_min_ohms / 1.0e9 << " ГОм)" << std::endl;
        std::cout << "Нормативний поріг IPC-TM-650: " << report.ipc_threshold_ohms << " Ом (100 МОм)" << std::endl;
        
        std::cout << std::defaultfloat;
        std::cout << "\nЛокальні мінімуми опору (просідання понад 15%): " << report.local_minima.size() << std::endl;
        for (const auto& min_pt : report.local_minima) {
            std::cout << "  - Час: " << std::fixed << std::setprecision(1) << min_pt.timestamp_hours 
                      << " год | Опір: " << std::scientific << std::setprecision(3) << min_pt.resistance_ohms 
                      << " Ом | Глибина: " << std::fixed << std::setprecision(1) << min_pt.depth_ratio << "%" << std::endl;
        }

        std::cout << "\n=== ВИСНОВОК ЩОДО НАДІЙНОСТІ ФЛЮСУ FVS-7 ===" << std::endl;
        std::cout << "Статус IPC-TM-650         : " << (report.is_ipc_compliant ? "[ ПРИЙНЯТО / PASS ]" : "[ ВІДХИЛЕНО / FAIL ]") << std::endl;
        std::cout << "Ризик дендритоутворення   : " << (report.dendrite_growth_risk ? "ВИСОКИЙ (виявлено деградацію)" : "ВІДСУТНІЙ (ізоляція стабільна)") << std::endl;

        if (report.is_ipc_compliant && !report.dendrite_growth_risk) {
            std::cout << "\nФлюс FVS-7 успішно підтвердив клас безвідмивного матеріалу. Залишки безпечні." << std::endl;
        } else {
            std::cout << "\nУВАГА! Виявлено ризик електрохімічної корозії або іонного забруднення." << std::endl;
        }

    } catch (const std::exception& ex) {
        std::cerr << "[ПОМИЛКА] " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
