#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <iomanip>
#include <stdexcept>

constexpr double R_GAS = 8.314462618; // Універсальна газова стала, Дж/(моль·К)

struct StatePoint {
    std::string name;
    double pressure_pa;
    double volume_m3;
    double temp_k;
};

struct CarnotResults {
    std::vector<StatePoint> points;
    double q_h_j;
    double q_c_j;
    double work_j;
    double efficiency;
    double cop_ref;
    double cop_heat;
};

CarnotResults simulate_carnot_cycle(
    double n_moles,
    double t_h,
    double t_c,
    double p1_pa,
    double v1_m3,
    double r_v,
    double gamma = 1.4)
{
    if (t_c <= 0.0 || t_h <= 0.0) {
        throw std::invalid_argument("Температури мають бути строго додатними в Кельвінах");
    }
    if (t_c >= t_h) {
        throw std::invalid_argument("T_C має бути меншою за T_H");
    }
    if (r_v <= 1.0) {
        throw std::invalid_argument("r_v має бути більшим за 1.0");
    }

    double p1 = p1_pa;
    double v1 = v1_m3;

    double v2 = v1 * r_v;
    double p2 = p1 / r_v;

    double vol_ratio_adiabat = std::pow(t_h / t_c, 1.0 / (gamma - 1.0));
    double v3 = v2 * vol_ratio_adiabat;
    double p3 = (n_moles * R_GAS * t_c) / v3;

    double v4 = v1 * vol_ratio_adiabat;
    double p4 = (n_moles * R_GAS * t_c) / v4;

    std::vector<StatePoint> points = {
        {"1 (Початок розширення)", p1, v1, t_h},
        {"2 (Кінець ізотерми T_H)", p2, v2, t_h},
        {"3 (Кінець адіабати)", p3, v3, t_c},
        {"4 (Кінець ізотерми T_C)", p4, v4, t_c}
    };

    double q_h = n_moles * R_GAS * t_h * std::log(r_v);
    double q_c = n_moles * R_GAS * t_c * std::log(r_v);
    double work = q_h - q_c;

    double efficiency = 1.0 - (t_c / t_h);
    double cop_ref = t_c / (t_h - t_c);
    double cop_heat = t_h / (t_h - t_c);

    return CarnotResults{points, q_h, q_c, work, efficiency, cop_ref, cop_heat};
}

int main() {
    try {
        CarnotResults res = simulate_carnot_cycle(1.0, 600.0, 300.0, 1e6, 0.0025, 2.0, 1.667);

        std::cout << std::fixed << std::setprecision(3);
        std::cout << "=== ТОЧКИ СТАНУ ЦИКЛУ КАРНО ===\n";
        for (const auto& pt : res.points) {
            std::cout << "Стан " << pt.name 
                      << ": P = " << (pt.pressure_pa / 1e5) << " бар, "
                      << "V = " << (pt.volume_m3 * 1000.0) << " л, "
                      << "T = " << pt.temp_k << " K\n";
        }

        std::cout << "\n=== ЕНЕРГЕТИЧНИЙ БАЛАНС ===\n";
        std::cout << "Підведена теплота Q_H : " << res.q_h_j << " Дж\n";
        std::cout << "Скинута теплота Q_C   : " << res.q_c_j << " Дж\n";
        std::cout << "Корисна робота W      : " << res.work_j << " Дж\n";
        std::cout << "Термічний ККД η       : " << (res.efficiency * 100.0) << "%\n";
        std::cout << "COP холодильника      : " << res.cop_ref << "\n";
        std::cout << "COP теплового насоса  : " << res.cop_heat << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
