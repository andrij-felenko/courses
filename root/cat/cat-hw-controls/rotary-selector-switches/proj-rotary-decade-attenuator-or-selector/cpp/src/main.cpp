#include "attenuator_calculator.hpp"
#include <iostream>
#include <iomanip>

int main() {
    // Параметри 12-позиційного галетного перемикача для регулятора гучності
    const size_t positions = 12;
    const double input_impedance_ohm = 10000.0; // 10 кОм вхідний опір
    const double max_attenuation_db = 50.0;     // 50 дБ діапазон регулювання

    std::cout << "========================================================================================\n";
    std::cout << "  РОЗРАХУНОК РЕЗИСТИВНОЇ МАТРИЦІ АТЕНЮАТОРА ДЛЯ ГАЛЕТНОГО ПЕРЕМИКАЧА (" << positions << " ПОЗИЦІЙ)\n";
    std::cout << "  Вхідний опір: " << input_impedance_ohm << " Ом, Макс. ослаблення: " << max_attenuation_db << " дБ\n";
    std::cout << "========================================================================================\n\n";

    AttenuatorCalculator calc(positions, input_impedance_ohm, max_attenuation_db);
    calc.calculate(AttenuationScale::Logarithmic);

    const auto& steps = calc.get_steps();

    // Заголовок підсумкової таблиці
    std::cout << std::setw(4)  << "Поз"
              << std::setw(10) << "Ціль(дБ)"
              << std::setw(12) << "R_сер_Ідеал"
              << std::setw(12) << "R_шунт_Ідеал"
              << std::setw(11) << "R_сер_E24"
              << std::setw(11) << "R_шунт_E24"
              << std::setw(11) << "R_сер_E96"
              << std::setw(11) << "R_шунт_E96"
              << std::setw(10) << "Пох_E96(дБ)" << "\n";
    std::cout << std::string(92, '-') << "\n";

    std::cout << std::fixed << std::setprecision(2);

    double max_error_e96 = 0.0;
    for (const auto& step : steps) {
        std::cout << std::setw(4)  << step.position
                  << std::setw(10) << step.target_attenuation_db
                  << std::setw(12) << step.r_series_ideal
                  << std::setw(12) << step.r_shunt_ideal
                  << std::setw(11) << step.r_series_e24
                  << std::setw(11) << step.r_shunt_e24
                  << std::setw(11) << step.r_series_e96
                  << std::setw(11) << step.r_shunt_e96
                  << std::setw(10) << step.error_db_e96 << "\n";

        if (step.error_db_e96 > max_error_e96) {
            max_error_e96 = step.error_db_e96;
        }
    }

    std::cout << std::string(92, '-') << "\n";
    std::cout << "Максимальне відхилення ослаблення при використанні ряду E96: " 
              << max_error_e96 << " дБ\n";
    std::cout << "Специфікацію згенеровано успішно.\n";

    return 0;
}
