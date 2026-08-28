// main.cpp — Приклад використання C++ модуля
#include <iostream>
#include <iomanip>
#include "psychrometrics.hpp"

int main() {
    using namespace physics::thermal;

    struct TestCase {
        double temp;
        double rh;
        const char* name;
    };

    TestCase tests[] = {
        {25.0, 50.0, "Стандартна кімната"},
        {30.0, 80.0, "Вологі тропіки"},
        {10.0, 90.0, "Туманний ранок"},
        {-5.0, 70.0, "Морозне повітря"}
    };

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "--- ТЕСТУВАННЯ МОДУЛЯ ТОЧКИ РОСИ ---\n";

    AntiCondensationController controller(2.0, 4.0);

    for (const auto& t : tests) {
        auto res = Psychrometrics::compute(t.temp, t.rh);
        if (!res) {
            std::cerr << "Помилка вхідних даних для " << t.name << "\n";
            continue;
        }

        double surface_temp = res->dew_point_c + 1.5; // Імітація прохолодної оптики
        bool heater = controller.update(surface_temp, res->dew_point_c);

        std::cout << "Сценарій: " << t.name << "\n"
                  << "  T_air: " << res->air_temp_c << " °C, RH: " << res->rel_humidity_pct << " %\n"
                  << "  p_sat: " << res->sat_vapor_press_kpa << " кПа, p_v: " << res->vapor_press_kpa << " кПа\n"
                  << "  Точка роси (T_d): " << res->dew_point_c << " °C\n"
                  << "  Точка інею (T_f): " << res->frost_point_c << " °C\n"
                  << "  T_поверхні: " << surface_temp << " °C -> Нагрівач: " 
                  << (heater ? "УВІМКНЕНО" : "ВИМКНЕНО") << "\n\n";
    }

    return 0;
}
