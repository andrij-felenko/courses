#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>

// Фізичні константи
constexpr double KB = 8.617333262145e-5; // Константа Больцмана, еВ/К
constexpr double EPS_0 = 8.8541878128e-12; // Електрична стала, Ф/м
constexpr double ELEMENTARY_CHARGE = 1.602176634e-19; // Кл

// Результат моделювання точки ВАХ
struct IVPoint {
    double voltage;     // Напруга, В
    double current;     // Струм, А
    double resistance;  // Динамічний опір, Ом
    double temperature; // Температура (для термистора), К
};

// 1. Симуляція ZnO Варистора
std::vector<IVPoint> simulate_varistor(double un_voltage, double alpha, 
                                        double r_grain, double u_min, 
                                        double u_max, int steps) {
    std::vector<IVPoint> curve;
    curve.reserve(steps);
    
    const double du = (u_max - u_min) / (steps - 1);
    const double i_ref = 1e-3; // 1 мА
    
    for (int i = 0; i < steps; ++i) {
        double u = u_min + i * du;
        
        // Струм через міжкристалічний бар'єр
        double i_barrier = i_ref * std::pow(u / un_voltage, alpha);
        
        // Враховуємо послідовний опір зерен (падіння U_grain = I * R_grain)
        double i_total = i_barrier;
        for (int iter = 0; iter < 10; ++iter) {
            double u_barrier = u - i_total * r_grain;
            if (u_barrier < 0) u_barrier = 0;
            i_total = i_ref * std::pow(u_barrier / un_voltage, alpha);
        }
        
        double r_dyn = (i_total > 1e-12) ? (u / i_total) : 1e12;
        curve.push_back({u, i_total, r_dyn, 298.15});
    }
    return curve;
}

// 2. Симуляція NTC Термистора з саморозігрівом
std::vector<IVPoint> simulate_ntc_thermistor(double r25, double b_val, 
                                              double delta_mW_K, double t_amb_C,
                                              double i_min, double i_max, int steps) {
    std::vector<IVPoint> curve;
    curve.reserve(steps);
    
    const double t_amb_K = t_amb_C + 273.15;
    const double delta_W_K = delta_mW_K * 1e-3; // переведення в Вт/К
    const double di = (i_max - i_min) / (steps - 1);
    
    for (int idx = 0; idx < steps; ++idx) {
        double current = i_min + idx * di;
        
        // Ітераційний розв'язок теплового балансу: T = T_amb + (I^2 * R(T)) / delta
        double t_body = t_amb_K;
        double r_ntc = r25;
        
        for (int iter = 0; iter < 30; ++iter) {
            r_ntc = r25 * std::exp(b_val * (1.0 / t_body - 1.0 / 298.15));
            double p_heat = current * current * r_ntc;
            t_body = 0.5 * t_body + 0.5 * (t_amb_K + p_heat / delta_W_K);
        }
        
        double voltage = current * r_ntc;
        curve.push_back({voltage, current, r_ntc, t_body});
    }
    return curve;
}

// 3. Симуляція ефекту Пуля — Френкеля у діелектрику
std::vector<IVPoint> simulate_poole_frenkel(double thickness_nm, double eps_r,
                                             double e_trap_ev, double e_min_MV_cm,
                                             double e_max_MV_cm, int steps) {
    std::vector<IVPoint> curve;
    curve.reserve(steps);
    
    const double d_m = thickness_nm * 1e-9;
    const double de = (e_max_MV_cm - e_min_MV_cm) / (steps - 1);
    
    const double beta_pf_J = std::sqrt(std::pow(ELEMENTARY_CHARGE, 3) / 
                                      (M_PI * eps_r * EPS_0));
    const double beta_pf_eV = beta_pf_J / ELEMENTARY_CHARGE;
    
    const double temp_K = 298.15;
    const double j0 = 1e-6; // А/м^2
    
    for (int i = 0; i < steps; ++i) {
        double e_field_MV_cm = e_min_MV_cm + i * de;
        double e_field_V_m = e_field_MV_cm * 1e8; // В/м
        
        double delta_e_ev = beta_pf_eV * std::sqrt(e_field_V_m);
        double eff_trap_ev = e_trap_ev - delta_e_ev;
        
        double current_density = j0 * (e_field_V_m / 1e6) * 
                                 std::exp(-eff_trap_ev / (KB * temp_K));
        
        double voltage = e_field_V_m * d_m;
        double r_eff = (current_density > 1e-15) ? (voltage / current_density) : 1e15;
        
        curve.push_back({voltage, current_density, r_eff, temp_K});
    }
    return curve;
}

int main() {
    std::cout << "=== СИМУЛЯЦІЯ НЕОМІЧНИХ ВАХ (C++20) ===\n\n";

    // 1. Моделювання ZnO Варистора (U_N = 430V, Alpha = 35)
    std::cout << "--- 1. Варистор ZnO (U_N = 430В, alpha = 35) ---\n";
    std::cout << std::setw(10) << "U [В]" << std::setw(14) << "I [А]" 
              << std::setw(16) << "R [Ом]" << "\n";
    
    auto varistor_iv = simulate_varistor(430.0, 35.0, 0.5, 300.0, 480.0, 7);
    for (const auto& pt : varistor_iv) {
        std::cout << std::setw(10) << std::fixed << std::setprecision(1) << pt.voltage
                  << std::setw(14) << std::scientific << std::setprecision(3) << pt.current
                  << std::setw(16) << std::scientific << std::setprecision(3) << pt.resistance
                  << "\n";
    }

    // 2. Моделювання NTC Термистора (R25 = 10кОм, B = 3950K)
    std::cout << "\n--- 2. NTC Термистор (R25 = 10кОм, Саморозігрів) ---\n";
    std::cout << std::setw(12) << "I [мА]" << std::setw(12) << "U [В]" 
              << std::setw(14) << "R [Ом]" << std::setw(12) << "T [°C]" << "\n";
              
    auto ntc_iv = simulate_ntc_thermistor(10000.0, 3950.0, 5.0, 25.0, 0.0002, 0.003, 7);
    for (const auto& pt : ntc_iv) {
        std::cout << std::setw(12) << std::fixed << std::setprecision(2) << pt.current * 1000.0
                  << std::setw(12) << std::fixed << std::setprecision(2) << pt.voltage
                  << std::setw(14) << std::fixed << std::setprecision(1) << pt.resistance
                  << std::setw(12) << std::fixed << std::setprecision(1) << pt.temperature - 273.15
                  << "\n";
    }

    // 3. Моделювання Пуля - Френкеля для Si3N4 (Товщина 10 нм, eps_r = 3.8, E_trap = 1.2 еВ)
    std::cout << "\n--- 3. Струм витоку Пуля - Френкеля у Si3N4 (10 нм) ---\n";
    std::cout << std::setw(10) << "U [В]" << std::setw(16) << "J [А/м^2]" 
              << std::setw(16) << "R_eff [Ом*м^2]" << "\n";
              
    auto pf_iv = simulate_poole_frenkel(10.0, 3.8, 1.2, 0.5, 3.0, 6);
    for (const auto& pt : pf_iv) {
        std::cout << std::setw(10) << std::fixed << std::setprecision(2) << pt.voltage
                  << std::setw(16) << std::scientific << std::setprecision(3) << pt.current
                  << std::setw(16) << std::scientific << std::setprecision(3) << pt.resistance
                  << "\n";
    }

    return 0;
}
