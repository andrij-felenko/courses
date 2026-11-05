#include "service_calculator.hpp"
#include <iostream>

int main() {
    std::cout << "Ініціалізація системи моніторингу вузлів тертя (C++17)...\n";

    ServiceCalculator calculator;

    // Конфігурація кінематичних вузлів принтера CoreXY
    calculator.addNode(std::make_unique<LeadScrewNode>("Ось Z (Гвинт T8 POM)", LeadScrewNode::NutMaterial::POM));
    calculator.addNode(std::make_unique<LinearRailNode>("Ось X (Рейка MGN12)", 350.0));
    calculator.addNode(std::make_unique<LinearRailNode>("Ось Y (Рейка MGN12)", 350.0));

    std::cout << "Початкова діагностика нової кінематики:\n";
    calculator.printStatusReport();

    // Симуляція активного друку протягом кількох тижнів
    std::cout << "\nСимуляція 400 годин роботи 3D-принтера...\n";

    // Вісь X та Y роблять великий пробіг на високих швидкостях (150 мм/с)
    for (int day = 1; day <= 30; day++) {
        calculator.logMotion("Ось X (Рейка MGN12)", 25000.0, 150.0); // 25 м на добу
        calculator.logMotion("Ось Y (Рейка MGN12)", 22000.0, 150.0); // 22 м на добу
        calculator.logMotion("Ось Z (Гвинт T8 POM)", 12000.0, 8.0);   // 12 м на добу з Z-hop
    }

    std::cout << "\nДіагностика після напрацювання серії замовлень:\n";
    calculator.printStatusReport();

    // Перевірка списку тривог
    auto alerts = calculator.getNodesRequiringService();
    if (!alerts.empty()) {
        std::cout << "\nВиявлено критичний знос мастильного шару у вузлах:\n";
        for (const auto& name : alerts) {
            std::cout << " -> " << name << "\n";
        }

        std::cout << "\nПроведення регламентного обслуговування змазкою SI-180...\n";
        for (const auto& name : alerts) {
            calculator.serviceNode(name);
            std::cout << "  Вузол \"" << name << "\" промито IPA 99.8% та нанесено нову змазку.\n";
        }

        std::cout << "\nПідсумковий звіт після завершення сервісних робіт:\n";
        calculator.printStatusReport();
    }

    return 0;
}
