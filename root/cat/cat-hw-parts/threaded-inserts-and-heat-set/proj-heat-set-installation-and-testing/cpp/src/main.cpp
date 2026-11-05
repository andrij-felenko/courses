#include "PulloutTestRig.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "Ініціалізація стенда випробування нарізних втулок на виривання (C++17)...\n";

    LoadCell load_cell("Тензодатчик CZL601 (100 кг / 1000 Н)", 415.0);
    PulloutTestRig test_rig(load_cell, 128);

    std::cout << "Запуск тестової сесії: тарування тензомосту та моніторинг зусилля...\n\n";
    test_rig.startSession();

    std::cout << "Час (с) | Поточне F (Н) | Пік F (Н) | Фаза деформації\n";
    std::cout << "--------------------------------------------------------------------\n";

    int cycle = 0;
    while (!test_rig.isTestFinished() && cycle < 85) {
        test_rig.update();
        cycle++;

        if (cycle % 5 == 0 || test_rig.getState() == PulloutTestRig::State::PulloutFailure) {
            std::cout << " " << std::fixed << std::setprecision(2) << (cycle * 0.05) << " с | "
                      << std::setw(13) << std::setprecision(1) << test_rig.getCurrentForce() << " | "
                      << std::setw(9) << std::setprecision(1) << test_rig.getPeakForce() << " | "
                      << test_rig.getStateName() << "\n";
        }
    }

    test_rig.printReport();
    return 0;
}
