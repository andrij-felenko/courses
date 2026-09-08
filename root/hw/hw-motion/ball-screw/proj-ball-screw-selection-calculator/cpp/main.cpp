#include "ball_screw_dimensioner.hpp"
#include <iostream>
#include <iomanip>

int main() {
    BallScrewParams specs;
    specs.nominal_diameter_mm = 25.0;
    specs.lead_mm = 10.0;
    specs.root_diameter_mm = 21.8;
    specs.length_mm = 950.0;
    specs.dynamic_rating_C_N = 21200.0;
    specs.static_rating_C0_N = 44500.0;
    specs.mounting = MountingScheme::FixedSupported;

    std::vector<DutyPhase> duty_cycle = {
        {0.25, 2400.0, 1850.0}, // Розгін каретки (високе прискорення)
        {1.80, 2400.0,  620.0}, // Робочий хід (фрезерування заготовки)
        {0.25, 1200.0,  450.0}, // Сповільнення
        {1.50, 3000.0,  320.0}  // Швидке холосте повернення
    };

    BallScrewDimensioner calculator(specs);
    double temp_rise_C = 12.0;
    DimensioningReport r = calculator.evaluate(duty_cycle, temp_rise_C, 20000.0);

    std::cout << "=== РОЗРАХУНОК КУЛЬКОВОЇ ГВИНТОВОЇ ПЕРЕДАЧІ (ШВП) ===\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Еквівалентна осьова сила Fm:  " << r.equivalent_force_N << " H\n";
    std::cout << "Еквівалентна швидкість nm:    " << r.equivalent_speed_rpm << " об/хв\n";
    std::cout << "Розрахунковий ресурс L10h:    " << r.life_hours << " годин\n";
    std::cout << "Критична частота n_cr:        " << r.critical_speed_rpm << " об/хв (макс: " << r.max_operating_speed_rpm << ")\n";
    std::cout << "Критична сила вигину F_cr:    " << r.buckling_force_N << " H (макс: " << r.max_axial_force_N << ")\n";
    std::cout << "Статичний коефіцієнт запасу:  " << r.static_safety_factor << "\n";
    std::cout << "Теплове видовження гвинта:    " << r.thermal_expansion_um << " мкм\n";
    std::cout << "Зусилля термопопереднатягу:   " << r.thermal_prestretch_N << " H\n";
    std::cout << "Статус верифікації:\n";
    std::cout << "  - Швидкість: " << (r.speed_safe ? "[ПРОЙДЕНО]" : "[ПЕРЕВИЩЕНО]") << "\n";
    std::cout << "  - Вигин:     " << (r.buckling_safe ? "[ПРОЙДЕНО]" : "[НЕБЕЗПЕКА]") << "\n";
    std::cout << "  - Ресурс:    " << (r.life_adequate ? "[ДОСТАТНІЙ]" : "[ЗАМАЛИЙ]") << "\n";

    return 0;
}
