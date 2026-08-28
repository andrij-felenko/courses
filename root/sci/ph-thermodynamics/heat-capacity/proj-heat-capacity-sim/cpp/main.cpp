#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <string>
#include <span>

// Використання математичних констант C++20
constexpr double R_GAS = 8.314462618;
constexpr double PI = std::numbers::pi;

struct MaterialParams {
    std::string name;
    double debye_temp;       // Θ_D, K
    double einstein_temp;    // T_E, K
    double sommerfeld_gamma; // γ, J/(mol*K^2)
};

// Підінтегральна функція Дебая
constexpr auto debye_integrand = [](double x) noexcept -> double {
    if (x < 1e-6) return x * x;
    if (x > 80.0) return 0.0;
    double exp_x = std::exp(x);
    double denom = exp_x - 1.0;
    return (x * x * x * x * exp_x) / (denom * denom);
};

// Обчислення дебаївського інтеграла методом Сімпсона
double compute_debye_integral(double x_max, int num_steps = 200) {
    if (x_max < 1e-4) {
        return (x_max * x_max * x_max) / 3.0;
    }
    if (x_max > 40.0) {
        return (4.0 * std::pow(PI, 4.0)) / 15.0;
    }

    if (num_steps % 2 != 0) num_steps++;
    double h = x_max / num_steps;
    double sum = debye_integrand(0.0) + debye_integrand(x_max);

    for (int i = 1; i < num_steps; ++i) {
        double x = i * h;
        double weight = (i % 2 == 0) ? 2.0 : 4.0;
        sum += weight * debye_integrand(x);
    }

    return sum * (h / 3.0);
}

// Модель Ейнштейна
double heat_capacity_einstein(double T, double T_E) {
    if (T <= 0.0) return 0.0;
    double x = T_E / T;
    if (x > 80.0) return 0.0;
    if (x < 1e-4) return 3.0 * R_GAS;

    double exp_x = std::exp(x);
    double denom = exp_x - 1.0;
    return 3.0 * R_GAS * (x * x * exp_x) / (denom * denom);
}

// Модель Дебая
double heat_capacity_debye(double T, double Θ_D) {
    if (T <= 0.0) return 0.0;
    double x_max = Θ_D / T;
    if (x_max < 1e-4) {
        return 3.0 * R_GAS * (1.0 - (1.0 / 20.0) * x_max * x_max);
    }
    double integral = compute_debye_integral(x_max);
    double factor = 9.0 * R_GAS * std::pow(T / Θ_D, 3.0);
    return factor * integral;
}

// Електронна теплоємність Зоммерфельда
constexpr double heat_capacity_electronic(double T, double gamma) noexcept {
    return gamma * T;
}

// Обертальна теплоємність газу з квантовою сумою
double heat_capacity_rotational(double T, double T_rot) {
    if (T <= 0.0) return 0.0;
    double y = T_rot / T;
    if (y > 10.0) return 0.0;

    double z = 0.0, z1 = 0.0, z2 = 0.0;
    for (int j = 0; j < 50; ++j) {
        double ej = j * (j + 1) * y;
        if (ej > 80.0) break;
        double w = (2 * j + 1) * std::exp(-ej);
        z += w;
        z1 += w * ej;
        z2 += w * ej * ej;
    }

    double mean_e = z1 / z;
    double mean_e2 = z2 / z;
    double var_e = mean_e2 - mean_e * mean_e;
    return R_GAS * var_e;
}

// Лінійна регресія (МНК) для C/T від T^2
std::pair<double, double> fit_low_temp_capacity(std::span<const double> T_arr,
                                                std::span<const double> C_arr) {
    const size_t n = T_arr.size();
    double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0;

    for (size_t i = 0; i < n; ++i) {
        double x = T_arr[i] * T_arr[i];
        double y = C_arr[i] / T_arr[i];
        sum_x += x;
        sum_y += y;
        sum_xx += x * x;
        sum_xy += x * y;
    }

    double delta = n * sum_xx - sum_x * sum_x;
    double gamma = (sum_y * sum_xx - sum_x * sum_xy) / delta;
    double A = (n * sum_xy - sum_x * sum_y) / delta;

    double debye_temp = std::pow((12.0 * std::pow(PI, 4.0) * R_GAS) / (5.0 * A), 1.0 / 3.0);
    return {gamma, debye_temp};
}

int main() {
    const MaterialParams copper{.name = "Мідь (Cu)",
                                .debye_temp = 343.0,
                                .einstein_temp = 240.0,
                                .sommerfeld_gamma = 0.000695};

    std::cout << "=== МОДЕЛЮВАННЯ ТЕПЛОЄМНОСТІ МАТЕРІАЛУ: " << copper.name << " ===\n";
    std::cout << std::setfill('-') << std::setw(65) << "" << std::setfill(' ') << "\n";
    std::cout << std::setw(7) << "T (K)" << " | "
              << std::setw(10) << "C_Einstein" << " | "
              << std::setw(10) << "C_Debye" << " | "
              << std::setw(10) << "C_Electron" << " | "
              << std::setw(15) << "C_Total(Deb+El)" << "\n";
    std::cout << std::setfill('-') << std::setw(65) << "" << std::setfill(' ') << "\n";

    const std::vector<double> test_temps{1.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 300.0, 500.0};

    std::cout << std::fixed << std::setprecision(4);
    for (double T : test_temps) {
        double c_einst = heat_capacity_einstein(T, copper.einstein_temp);
        double c_deb   = heat_capacity_debye(T, copper.debye_temp);
        double c_el    = heat_capacity_electronic(T, copper.sommerfeld_gamma);
        double c_tot   = c_deb + c_el;

        std::cout << std::setw(7) << std::setprecision(1) << T << " | "
                  << std::setw(10) << std::setprecision(4) << c_einst << " | "
                  << std::setw(10) << std::setprecision(4) << c_deb << " | "
                  << std::setw(10) << std::setprecision(5) << c_el << " | "
                  << std::setw(15) << std::setprecision(4) << c_tot << "\n";
    }

    std::cout << "\n=== ОБЕРТАЛЬНА ТЕПЛОЄМНОСТЬ ГАЗУ ВОДНЮ H2 (T_rot = 85.4 K) ===\n";
    std::cout << " T (K) | C_rot / R | C_rot (Дж/(моль*К))\n";
    std::cout << "-------+-----------+--------------------\n";
    const std::vector<double> h2_temps{10.0, 30.0, 50.0, 85.4, 150.0, 300.0};
    for (double T : h2_temps) {
        double crot = heat_capacity_rotational(T, 85.4);
        std::cout << std::setw(6) << T << " | "
                  << std::setw(9) << crot / R_GAS << " | "
                  << std::setw(18) << crot << "\n";
    }

    std::cout << "\n=== МНК ОБРОБКА НИЗЬКОТЕМПЕРАТУРНИХ ДАНИХ (1 K - 5 K) ===\n";
    const std::vector<double> exp_T{1.0, 2.0, 3.0, 4.0, 5.0};
    std::vector<double> exp_C(exp_T.size());
    double true_A = (12.0 * std::pow(PI, 4.0) * R_GAS) / (5.0 * std::pow(copper.debye_temp, 3.0));

    for (size_t i = 0; i < exp_T.size(); ++i) {
        exp_C[i] = copper.sommerfeld_gamma * exp_T[i] + true_A * std::pow(exp_T[i], 3.0);
    }

    auto [calc_gamma, calc_debye] = fit_low_temp_capacity(exp_T, exp_C);

    std::cout << "Відновлений gamma:  " << std::setprecision(6) << calc_gamma << " Дж/(моль*К^2)\n";
    std::cout << "Відновлена Theta_D: " << std::setprecision(2) << calc_debye << " K\n";

    return 0;
}
