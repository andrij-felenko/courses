#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>
#include <numbers>

enum class FlowRegime {
    Continuum,
    Slip,
    Transition,
    FreeMolecular
};

constexpr double BOLTZMANN_K = 1.380649e-23; // Дж/К

struct GasProperties {
    std::string_view name;
    double molecular_diameter_m; // Ефективний діаметр молекули (м)
    double molar_mass_kg_mol;    // Молярна маса (кг/моль)
};

// Типові константи для поширених газів
constexpr GasProperties GAS_AIR{"Air (N2/O2)", 0.37e-9, 0.02897};
constexpr GasProperties GAS_HE {"Helium",       0.22e-9, 0.00400};
constexpr GasProperties GAS_N2 {"Nitrogen",     0.375e-9, 0.02801};
constexpr GasProperties GAS_CH4{"Methane",      0.380e-9, 0.01604};

struct KnudsenAnalysis {
    double mean_free_path_m;
    double knudsen_number;
    FlowRegime regime;
    double flow_enhancement_factor; // Відношення реальної витрати до в'язкісної (1st order)
    double flow_enhancement_2nd;   // Відношення реальної витрати до в'язкісної (2nd order)
};

constexpr std::string_view regime_to_string(FlowRegime regime) noexcept {
    switch (regime) {
        case FlowRegime::Continuum:     return "Суцільний (Continuum, Kn < 0.01)";
        case FlowRegime::Slip:          return "З ковзанням (Slip, 0.01 <= Kn < 0.1)";
        case FlowRegime::Transition:    return "Перехідний (Transition, 0.1 <= Kn < 10)";
        case FlowRegime::FreeMolecular: return "Вільномолекулярний (Free-Molecular, Kn >= 10)";
    }
    return "Невідомий";
}

FlowRegime classify_knudsen(double kn) noexcept {
    if (kn < 0.01) return FlowRegime::Continuum;
    if (kn < 0.1)  return FlowRegime::Slip;
    if (kn < 10.0) return FlowRegime::Transition;
    return FlowRegime::FreeMolecular;
}

KnudsenAnalysis analyze_gas_flow(
    double temperature_K,
    double pressure_Pa,
    double char_length_m,
    const GasProperties& gas = GAS_AIR,
    double accommodation_coef = 1.0
) {
    const double d = gas.molecular_diameter_m;
    // λ = k_B * T / (sqrt(2) * pi * d^2 * P)
    const double lambda = (BOLTZMANN_K * temperature_K) /
                          (std::numbers::sqrt2 * std::numbers::pi * d * d * pressure_Pa);
    
    const double kn = lambda / char_length_m;
    const FlowRegime regime = classify_knudsen(kn);

    // Поправка пропускної здатності для круглої труби за умов ковзання першого та другого порядків
    const double sigma = accommodation_coef;
    const double flow_factor_1st = 1.0 + 6.0 * ((2.0 - sigma) / sigma) * kn;
    const double flow_factor_2nd = flow_factor_1st + 12.0 * 0.25 * kn * kn;

    return {lambda, kn, regime, flow_factor_1st, flow_factor_2nd};
}

int main() {
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=========================================================\n";
    std::cout << "  Аналізатор числа Кнудсена та режимів розрідженого газу\n";
    std::cout << "=========================================================\n\n";

    // Сценарій 1: Головка жорсткого диска (HDD), зазор L = 10 нм за 1 атм
    std::cout << "--- Сценарій 1: Зазор головки HDD (L = 10 нм, P = 1 атм) ---\n";
    auto res1 = analyze_gas_flow(298.15, 101325.0, 10e-9, GAS_AIR);
    std::cout << "Середній вільний пробіг λ: " << res1.mean_free_path_m * 1e9 << " нм\n";
    std::cout << "Число Кнудсена Kn:          " << res1.knudsen_number << "\n";
    std::cout << "Режим течії:                " << regime_to_string(res1.regime) << "\n";
    std::cout << "Підсилення витрати (1-й порядок): " << res1.flow_enhancement_factor << "\n";
    std::cout << "Підсилення витрати (2-й порядок): " << res1.flow_enhancement_2nd << "\n\n";

    // Сценарій 2: МЕМС-мікроканал (L = 50 мкм, P = 1 атм)
    std::cout << "--- Сценарій 2: МЕМС мікроканал (L = 50 мкм, P = 1 атм) ---\n";
    auto res2 = analyze_gas_flow(298.15, 101325.0, 50e-6, GAS_AIR);
    std::cout << "Середній вільний пробіг λ: " << res2.mean_free_path_m * 1e6 << " мкм\n";
    std::cout << "Число Кнудсена Kn:          " << res2.knudsen_number << "\n";
    std::cout << "Режим течії:                " << regime_to_string(res2.regime) << "\n";
    std::cout << "Підсилення витрати (Q/Q_visc): " << res2.flow_enhancement_factor << "\n\n";

    // Сценарій 3: Сланцева нанопора метану (L = 10 нм, P = 25 МПа)
    std::cout << "--- Сценарій 3: Нанопора сланцю (L = 10 нм, P = 25 МПа, Метан) ---\n";
    auto res3 = analyze_gas_flow(323.15, 25e6, 10e-9, GAS_CH4);
    std::cout << "Середній вільний пробіг λ: " << res3.mean_free_path_m * 1e9 << " нм\n";
    std::cout << "Число Кнудсена Kn:          " << res3.knudsen_number << "\n";
    std::cout << "Режим течії:                " << regime_to_string(res3.regime) << "\n";
    std::cout << "Підсилення витрати (Q/Q_visc): " << res3.flow_enhancement_factor << "\n\n";

    // Сценарій 4: Вакуумна труба (L = 10 см, P = 0.1 Па ~ 10^-3 мм рт. ст.)
    std::cout << "--- Сценарій 4: Вакуумна лінія (L = 10 см, P = 0.1 Па) ---\n";
    auto res4 = analyze_gas_flow(298.15, 0.1, 0.10, GAS_AIR);
    std::cout << "Середній вільний пробіг λ: " << res4.mean_free_path_m * 1e2 << " см\n";
    std::cout << "Число Кнудсена Kn:          " << res4.knudsen_number << "\n";
    std::cout << "Режим течії:                " << regime_to_string(res4.regime) << "\n";
    std::cout << "Підсилення витрати (Q/Q_visc): " << res4.flow_enhancement_factor << "\n";

    return 0;
}
