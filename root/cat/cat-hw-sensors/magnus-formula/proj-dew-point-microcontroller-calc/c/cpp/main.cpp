#include <iostream>
#include <iomanip>
#include "DewPointCalculator.hpp"
#include "HeaterController.hpp"

int main() {
    float temp = 15.0f;
    float humidity = 80.0f;

    DewPointCalculator calc(DewPointCalculator::Method::Math);
    HeaterController heater(2.0f, 3.0f);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Поточна температура: " << temp << "°C, Вологість: " << humidity << "%\n";

    float dewPoint = calc.calculate(temp, humidity);
    std::cout << "Точка роси: " << dewPoint << "°C\n";

    heater.update(temp, dewPoint);
    std::cout << "Стан нагрівача: " << (heater.isOn() ? "УВІМКНЕНО" : "ВИМКНЕНО") << "\n";

    temp = 18.0f;
    heater.update(temp, dewPoint);
    std::cout << "Температура після нагрівання: " << temp << "°C\n";
    std::cout << "Стан нагрівача: " << (heater.isOn() ? "УВІМКНЕНО" : "ВИМКНЕНО") << "\n";

    return 0;
}
