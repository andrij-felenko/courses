// henon_demo.cpp — Приклад використання C++20 API <henon/map.hpp>
#include <iostream>
#include <henon/map.hpp>

int main() {
    henon::Map map(1.4, 0.3);

    // 1. Розрахунок нерухомих точок
    auto fp = map.fixed_points();
    if (fp.is_real) {
        std::cout << "C++: Нерухома точка p1 = (" << fp.p1.x << ", " << fp.p1.y << ")\n";
    }

    // 2. Розрахунок показника Ляпунова
    auto lyap_res = map.lyapunov({0.1, 0.1}, 1000, 100000);
    if (lyap_res) {
        std::cout << "C++: lambda_1 = " << lyap_res->lambda_1 
                  << ", D_KY = " << lyap_res->kaplan_yorke << '\n';
    }

    return 0;
}
