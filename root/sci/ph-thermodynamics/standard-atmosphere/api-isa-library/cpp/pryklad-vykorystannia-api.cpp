#include <iostream>
#include <iomanip>
#include "isa.hpp"

void process_flight_telemetry(double gps_altitude_z_meters, double static_pressure_pa, double ias_knots) {
    // 1. Конвертуємо геометричну висоту GPS у геопотенціальну
    const double h_geo = isa::AtmosphereCalculator::z_to_h(gps_altitude_z_meters);

    // 2. Обчислюємо теоретичний стан атмосфери ISA
    const auto atmosphere = isa::AtmosphereCalculator::evaluate(h_geo);
    if (!atmosphere.has_value()) {
        std::cerr << "Помилка: Висота виходить за межі моделі ISA!" << std::endl;
        return;
    }

    const auto& env = atmosphere.value();

    // 3. Переводимо приладову швидкість із вузлів у м/с (1 вузол = 0.514444 м/с)
    const double cas_ms = ias_knots * 0.514444;

    // 4. Розраховуємо істинну повітряну швидкість (TAS) та число Маха
    const double tas_ms = isa::AtmosphereCalculator::cas_to_tas(cas_ms, env.density);
    const double mach = isa::AtmosphereCalculator::tas_to_mach(tas_ms, env.sound_speed);

    // 5. Розраховуємо барометричну висоту за тиском
    const auto pressure_alt = isa::AtmosphereCalculator::pressure_altitude(static_pressure_pa);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== ПОЛЬОТНА ТЕЛЕМЕТРІЯ ===" << std::endl;
    std::cout << "Геометрична висота (GPS): " << gps_altitude_z_meters << " м" << std::endl;
    std::cout << "Геопотенціальна висота:   " << h_geo << " м" << std::endl;
    std::cout << "Барометрична висота:      " << (pressure_alt.value_or(0.0)) << " м" << std::endl;
    std::cout << "Температура ISA:          " << env.temp_celsius << " °C" << std::endl;
    std::cout << "Статичний тиск:           " << env.pressure_hpa() << " гПа" << std::endl;
    std::cout << "Приладова швидкість (CAS):" << ias_knots << " вузлів (" << cas_ms << " м/с)" << std::endl;
    std::cout << "Істинна швидкість (TAS):  " << (tas_ms / 0.514444) << " вузлів (" << tas_ms << " м/с)" << std::endl;
    std::cout << "Число Маха:               " << mach << " M" << std::endl;
}
