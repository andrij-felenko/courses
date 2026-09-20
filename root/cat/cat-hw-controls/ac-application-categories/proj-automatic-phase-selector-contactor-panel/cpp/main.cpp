#include "contactor_timer.hpp"
#include <iostream>

int main() {
    ContactorPinConfig phase_a{ 4, 5 };
    ContactorPinConfig phase_b{ 6, 7 };
    ContactorTimer controller(phase_a, phase_b, 150);

    controller.begin();
    std::cout << "Ініціалізація селектора фаз з дедтаймом 150 мс." << std::endl;

    controller.selectPhase(1);
    while (controller.getActivePhase() != 1) {
        controller.update();
    }
    std::cout << "Активна фаза 1." << std::endl;

    controller.selectPhase(2);
    while (controller.getActivePhase() != 2) {
        controller.update();
    }
    std::cout << "Безпечно переключено на фазу 2 після згасання дуги." << std::endl;

    return 0;
}
