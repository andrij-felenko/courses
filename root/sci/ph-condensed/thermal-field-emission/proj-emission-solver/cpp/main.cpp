#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <iomanip>
#include <expected>
#include <span>

// Фундаментальні фізичні константи (SI)
namespace constants {
    constexpr double e = 1.602176634e-19;       // Заряд електрона, C
    constexpr double m = 9.1093837015e-31;      // Маса електрона, kg
    constexpr double h = 6.62607015e-34;        // Стала Планка, J*s
    constexpr double k_B = 1.380649e-23;        // Стала Больцмана, J/K
    constexpr double eps0 = 8.8541878128e-12;   // Електрична стала, F/m
    
    // Теоретична константа Річардсона (A / (m^2 * K^2))
    constexpr double A_0 = (4.0 * M_PI * m * e * k_B * k_B) / (h * h * h);
    
    // Константи Фаулера-Нордгейма
    constexpr double A_FN = (e * e * e) / (8.0 * M_PI * h); // A * eV / V^2
    constexpr double B_FN = (8.0 * M_PI * std::sqrt(2.0 * m)) / (3.0 * h * e); // V / (m * eV^(3/2))
}

// Результати розрахунку емісії
struct EmissionResult {
    double field_V_m;          // Прикладне макрополе, V/m
    double local_field_V_m;    // Локальне поле E_local = beta * E, V/m
    double J_richardson;       // Термоелектронний струм (Річардсон), A/m^2
    double J_schottky;          // Струм з урахуванням ефекту Шотткі, A/m^2
    double J_fowler_nordheim;  // Струм автоелектронної емісії, A/m^2
    std::string dominant_mode; // Домінуючий механізм
};

// Клас калькулятора емісійних процесів
class EmissionCalculator {
public:
    EmissionCalculator(double work_function_eV, double field_enhancement_beta = 1.0)
        : phi_eV_(work_function_eV),
          phi_J_(work_function_eV * constants::e),
          beta_(field_enhancement_beta) {}

    // Обчислення зниження бар'єру Шотткі (eV)
    [[nodiscard]] double schottky_lowering_eV(double E_local) const noexcept {
        if (E_local <= 0.0) return 0.0;
        const double delta_phi_J = std::sqrt((constants::e * constants::e * constants::e * E_local) /
                                             (4.0 * M_PI * constants::eps0));
        return delta_phi_J / constants::e;
    }

    // Безрозмірний параметр Шотткі y = Delta_Phi / Phi
    [[nodiscard]] double nordheim_y(double E_local) const noexcept {
        return schottky_lowering_eV(E_local) / phi_eV_;
    }

    // Апроксимація функції Нордгейма v(y)
    [[nodiscard]] static double nordheim_v(double y) noexcept {
        if (y <= 0.0) return 1.0;
        if (y >= 1.0) return 0.0;
        return 1.0 - y * y + (y * y / 3.0) * std::log(y + 1e-12);
    }

    // Струм Річардсона-Дешмана
    [[nodiscard]] double calculate_richardson(double T_kelvin) const noexcept {
        if (T_kelvin <= 0.0) return 0.0;
        return constants::A_0 * T_kelvin * T_kelvin * std::exp(-phi_J_ / (constants::k_B * T_kelvin));
    }

    // Струм з урахуванням ефекту Шотткі
    [[nodiscard]] double calculate_schottky(double T_kelvin, double E_macro) const noexcept {
        if (T_kelvin <= 0.0) return 0.0;
        const double E_local = E_macro * beta_;
        const double d_phi_J = schottky_lowering_eV(E_local) * constants::e;
        const double J_0 = calculate_richardson(T_kelvin);
        return J_0 * std::exp(d_phi_J / (constants::k_B * T_kelvin));
    }

    // Струм Фаулера-Нордгейма (автоемісія)
    [[nodiscard]] double calculate_fowler_nordheim(double E_macro) const noexcept {
        const double E_local = E_macro * beta_;
        if (E_local <= 1e6) return 0.0; // Істотний тунельний струм лише у сильних полях

        const double y = nordheim_y(E_local);
        if (y >= 1.0) return 1e12; // Повний розпад бар'єру

        const double v_y = nordheim_v(y);
        const double phi_pow_15 = std::pow(phi_eV_, 1.5);
        
        const double exponent = - (constants::B_FN * phi_pow_15 * v_y) / E_local;
        const double prefactor = (constants::A_FN * E_local * E_local) / phi_eV_;

        return prefactor * std::exp(exponent);
    }

    // Повний аналіз для заданого поля та температури
    [[nodiscard]] EmissionResult analyze(double E_macro, double T_kelvin) const noexcept {
        const double J_rd = calculate_richardson(T_kelvin);
        const double J_sch = calculate_schottky(T_kelvin, E_macro);
        const double J_fn = calculate_fowler_nordheim(E_macro);

        std::string mode = "Термоелектронна";
        if (J_fn > J_sch) {
            mode = "Автоелектронна (тунельна)";
        } else if (J_sch > 10.0 * J_rd) {
            mode = "Ефект Шотткі";
        }

        return EmissionResult{
            .field_V_m = E_macro,
            .local_field_V_m = E_macro * beta_,
            .J_richardson = J_rd,
            .J_schottky = J_sch,
            .J_fowler_nordheim = J_fn,
            .dominant_mode = mode
        };
    }

private:
    double phi_eV_;
    double phi_J_;
    double beta_;
};

int main() {
    std::cout << "=== Симуляція емісійних струмів (Вольфрам: Phi = 4.5 eV) ===\n\n";

    constexpr double tungsten_phi = 4.5;
    constexpr double beta = 100.0; // Підсилення на вістрі
    EmissionCalculator calc(tungsten_phi, beta);

    constexpr double T = 1500.0; // Температура катода 1500 K
    std::vector<double> fields_MV_m = {0.1, 0.5, 1.0, 5.0, 10.0, 20.0, 50.0};

    std::cout << std::setw(12) << "Поле (MV/m)"
              << std::setw(15) << "E_loc (GV/m)"
              << std::setw(16) << "J_Schottky(A/m2)"
              << std::setw(16) << "J_FN (A/m2)"
              << std::setw(28) << "Домінуючий режим" << "\n";
    std::cout << std::string(87, '-') << "\n";

    for (double E_MV : fields_MV_m) {
        double E_V_m = E_MV * 1e6;
        auto res = calc.analyze(E_V_m, T);

        std::cout << std::setw(12) << std::fixed << std::setprecision(1) << E_MV
                  << std::setw(15) << std::setprecision(3) << res.local_field_V_m / 1e9
                  << std::setw(16) << std::scientific << std::setprecision(2) << res.J_schottky
                  << std::setw(16) << std::scientific << std::setprecision(2) << res.J_fowler_nordheim
                  << std::setw(28) << res.dominant_mode << "\n";
    }

    return 0;
}
