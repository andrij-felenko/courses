#include <iostream>
#include <cmath>
#include <format>

struct MemsParams {
    double length_um;       // Довжина балки, мкм
    double thickness_um;    // Товщина балки, мкм
    double width_um;        // Ширина балки, мкм
    double target_depth_um; // Цільова глибина травлення, мкм
    double etch_rate_um_min;// Швидкість травлення DRIE, мкм/хв
    double cycle_time_s;    // Час одного циклу Bosch, с
};

void calculate_mems(const MemsParams& p) {
    constexpr double E = 169e9;    // Модуль Юнга кремнію, Па
    constexpr double rho = 2330.0; // Густина кремнію, кг/м^3

    // Переведення в метри
    const double L = p.length_um * 1e-6;
    const double t = p.thickness_um * 1e-6;

    // Розрахунок резонансної частоти
    const double f0 = 0.1615 * (t / (L * L)) * std::sqrt(E / rho);

    // Розрахунок параметрів травлення
    const double total_time_min = p.target_depth_um / p.etch_rate_um_min;
    const double total_time_s = total_time_min * 60.0;
    const int num_cycles = static_cast<int>(std::ceil(total_time_s / p.cycle_time_s));
    const double depth_per_cycle_nm = (p.target_depth_um * 1000.0) / num_cycles;

    std::cout << std::format("Резонансна частота f0: {:.2f} кГц\n", f0 / 1000.0);
    std::cout << std::format("Загальний час травлення: {:.2f} хв\n", total_time_min);
    std::cout << std::format("Кількість циклів Bosch: {}\n", num_cycles);
    std::cout << std::format("Глибина за цикл: {:.1f} нм\n", depth_per_cycle_nm);
}

int main() {
    constexpr MemsParams params{
        .length_um = 300.0,
        .thickness_um = 10.0,
        .width_um = 20.0,
        .target_depth_um = 50.0,
        .etch_rate_um_min = 4.5,
        .cycle_time_s = 3.5
    };
    calculate_mems(params);
    return 0;
}
