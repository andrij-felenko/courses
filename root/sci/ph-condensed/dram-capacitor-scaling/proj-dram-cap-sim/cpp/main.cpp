#include <iostream>
#include <iomanip>
#include <cmath>
#include <string>
#include <vector>
#include <stdexcept>

// Фізичні константи
constexpr double EPSILON_0 = 8.8541878176e-12; // Ф/м
constexpr double Q_E       = 1.602176634e-19;  // Кл
constexpr double K_B       = 1.380649e-23;     // Дж/К
constexpr double T_KELVIN  = 358.15;           // 85 °C

struct MaterialProps {
    std::string name;
    double k_rel;
    double e_g_ev;
    double phi_b_ev;
    double k_opt;
};

struct SimResult {
    int node_nm;
    int aspect_ratio;
    std::string material;
    double d_phys_nm;
    double eot_nm;
    double c_cell_ff;
    double j_leak_a_cm2;
    bool meets_target;
};

SimResult simulateDramCell(int node_nm, int aspect_ratio, const MaterialProps& mat, double d_phys_nm, double v_dd) {
    double f_m = node_nm * 1e-9;
    double d_m = d_phys_nm * 1e-9;
    double d_pillar = f_m * 0.7;
    double h_m = d_pillar * aspect_ratio;

    // Геометрична площа циліндра
    double a_cap = M_PI * d_pillar * h_m + M_PI * std::pow(d_pillar / 2.0, 2);

    // Ємність і EOT
    double c_farads = (EPSILON_0 * mat.k_rel * a_cap) / d_m;
    double c_ff = c_farads * 1e15;
    double eot_nm = d_phys_nm * (3.9 / mat.k_rel);

    // Струм витоку Пула-Френкеля
    double e_field = v_dd / d_m;
    double phi_t_j = 1.0 * Q_E;
    double beta_pf = std::sqrt(Q_E / (M_PI * EPSILON_0 * mat.k_opt));
    double delta_phi = Q_E * beta_pf * std::sqrt(e_field);

    double exp_factor = - (phi_t_j - delta_phi) / (K_B * T_KELVIN);
    double c_0 = 1.0e-4;
    double j_pf = (c_0 * e_field * std::exp(exp_factor)) / 100.0;

    return { node_nm, aspect_ratio, mat.name, d_phys_nm, eot_nm, c_ff, j_pf, c_ff >= 25.0 };
}

int main() {
    std::vector<MaterialProps> materials = {
        {"ONO",  5.5, 6.0, 2.1, 2.20},
        {"ZrO2", 35.0, 5.8, 1.4, 4.84},
        {"ZAZ",  32.0, 5.8, 1.4, 4.50},
        {"TiO2", 80.0, 3.2, 0.8, 6.25}
    };

    struct Scenario { int node; int ar; int mat_idx; double dp; double v; };
    std::vector<Scenario> scenarios = {
        {90, 12, 0, 5.0, 1.2},
        {45, 25, 1, 6.0, 1.1},
        {22, 35, 2, 5.0, 1.0},
        {14, 45, 2, 4.2, 0.8},
        {10, 50, 3, 3.8, 0.7}
    };

    std::cout << std::string(86, '=') << "\n";
    std::cout << std::left << std::setw(8) << "Вузол" << " | "
              << std::setw(6) << "AR" << " | "
              << std::setw(9) << "Матеріал" << " | "
              << std::setw(8) << "d_phys" << " | "
              << std::setw(8) << "EOT" << " | "
              << std::setw(10) << "C_cell" << " | "
              << std::setw(12) << "Виток J_PF" << " | "
              << "Статус (>=25fF)\n";
    std::cout << std::string(86, '=') << "\n";

    for (const auto& sc : scenarios) {
        auto res = simulateDramCell(sc.node, sc.ar, materials[sc.mat_idx], sc.dp, sc.v);
        std::cout << std::right << std::setw(3) << res.node_nm << " нм   | "
                  << std::setw(4) << res.aspect_ratio << ":1 | "
                  << std::left << std::setw(9) << res.material << " | "
                  << std::right << std::fixed << std::setprecision(1) << std::setw(6) << res.d_phys_nm << "нм | "
                  << std::setprecision(2) << std::setw(6) << res.eot_nm << "нм | "
                  << std::setw(7) << res.c_cell_ff << " fF | "
                  << std::scientific << std::setprecision(2) << std::setw(10) << res.j_leak_a_cm2 << " | "
                  << (res.meets_target ? "В НОРМІ" : "НЕДОСТАТНЬО") << "\n";
    }
    std::cout << std::string(86, '=') << "\n";
    return 0;
}
