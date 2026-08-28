#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string_view>
#include <expected>

// Термодинамічна модель газу Ван-дер-Ваальса (параметри для азоту N2)
struct VdWGas {
    double a{0.137};   // Па·м⁶/моль²
    double b{3.87e-5}; // м³/моль
    double R{8.31446}; // Дж/(моль·К)
    double Cv_ideal{2.5 * 8.31446}; // Двохатомний газ (5/2 R)

    // Обчислення тиску P(T, V)
    [[nodiscard]] constexpr double pressure(double T, double V) const noexcept {
        return (R * T) / (V - b) - a / (V * V);
    }

    // Похідна (∂P/∂T)_V аналітична
    [[nodiscard]] constexpr double dPdT_analyt(double V) const noexcept {
        return R / (V - b);
    }
};

// Результат чисельної перевірки співвідношення Максвелла
struct MaxwellCheckResult {
    double dPdT_num;
    double dSdV_num;
    double abs_error;
    double internal_pressure;
};

class ThermoSolver {
private:
    VdWGas gas_;
    double step_T_{1e-4};
    double step_V_{1e-6};

public:
    explicit ThermoSolver(VdWGas gas) : gas_(gas) {}

    // Чисельна похідна (∂P/∂T)_V центральною різницею
    [[nodiscard]] double compute_dPdT(double T, double V) const noexcept {
        const double P_plus  = gas_.pressure(T + step_T_, V);
        const double P_minus = gas_.pressure(T - step_T_, V);
        return (P_plus - P_minus) / (2.0 * step_T_);
    }

    // Чисельне виведення (∂S/∂V)_T через Максвелла (∂S/∂V)_T = (∂P/∂T)_V
    [[nodiscard]] double compute_dSdV(double T, double V) const noexcept {
        return compute_dPdT(T, V);
    }

    // Верифікація Максвелла та обчислення (∂U/∂V)_T
    [[nodiscard]] std::expected<MaxwellCheckResult, std::string_view> 
    verify_maxwell(double T, double V) const noexcept {
        if (T <= 0.0 || V <= gas_.b) {
            return std::unexpected("Некоректний термодинамічний стан: T <= 0 або V <= b");
        }

        const double dPdT_num = compute_dPdT(T, V);
        const double dSdV_num = compute_dSdV(T, V);
        const double dPdT_exact = gas_.dPdT_analyt(V);

        const double abs_err = std::abs(dPdT_num - dPdT_exact);
        const double P_val = gas_.pressure(T, V);
        const double int_press = T * dPdT_num - P_val; // (∂U/∂V)_T

        return MaxwellCheckResult{
            .dPdT_num = dPdT_num,
            .dSdV_num = dSdV_num,
            .abs_error = abs_err,
            .internal_pressure = int_press
        };
    }

    // Сітковий розрахунок ефекту Джоуля — Томсона μ_JT(T, V)
    void compute_joule_thomson_grid(double T_start, double T_end, int steps_T, double V_val) const {
        std::cout << std::setw(10) << "T (K)" 
                  << std::setw(15) << "P (Па)" 
                  << std::setw(18) << "(∂U/∂V)_T (Па)" 
                  << std::setw(18) << "a/V² (Теорія)" 
                  << std::setw(15) << "μ_JT (К/Па)" << "\n";
        std::cout << std::string(76, '-') << "\n";

        const double dT = (T_end - T_start) / steps_T;
        for (int i = 0; i <= steps_T; ++i) {
            const double T = T_start + i * dT;
            const double P = gas_.pressure(T, V_val);
            const double dPdT = compute_dPdT(T, V_val);
            const double int_press = T * dPdT - P;
            const double exact_int_press = gas_.a / (V_val * V_val);

            // Обчислення (∂V/∂T)_P через (-∂P/∂T)_V / (∂P/∂V)_T
            const double dPdV = (gas_.pressure(T, V_val + step_V_) - gas_.pressure(T, V_val - step_V_)) / (2.0 * step_V_);
            const double dVdT_p = -dPdT / dPdV;

            const double Cp = gas_.Cv_ideal + T * (dPdT * dPdT) / (-dPdV);
            const double mu_JT = (1.0 / Cp) * (T * dVdT_p - V_val);

            std::cout << std::fixed << std::setprecision(2)
                      << std::setw(10) << T 
                      << std::scientific << std::setprecision(4)
                      << std::setw(15) << P 
                      << std::setw(18) << int_press 
                      << std::setw(18) << exact_int_press 
                      << std::setw(15) << mu_JT << "\n";
        }
    }
};

int main() {
    VdWGas N2_gas{.a = 0.137, .b = 3.87e-5}; // Азот
    Thermosolver solver(N2_gas);

    const double T_test = 300.0; // 300 K
    const double V_test = 1.0e-3; // 1 літр/моль

    auto res = solver.verify_maxwell(T_test, V_test);
    if (res) {
        std::cout << "--- Результати верифікації співвідношення Максвелла ---\n";
        std::cout << "(∂P/∂T)_V чисельне : " << res->dPdT_num << " Па/К\n";
        std::cout << "(∂S/∂V)_T чисельне : " << res->dSdV_num << " Дж/(м³·К)\n";
        std::cout << "Абсолютна похибка  : " << res->abs_error << " Па/К\n";
        std::cout << "(∂U/∂V)_T калоричне: " << res->internal_pressure << " Па\n\n";
    }

    std::cout << "--- Сітка залежностей для азоту (V = 0.001 м³/моль) ---\n";
    solver.compute_joule_thomson_grid(200.0, 600.0, 5, V_test);

    return 0;
}
