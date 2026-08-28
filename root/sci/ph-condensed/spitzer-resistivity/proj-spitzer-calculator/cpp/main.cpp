#include <iostream>
#include <cmath>
#include <numbers>
#include <optional>
#include <iomanip>

namespace plasma {

struct PlasmaState {
    double T_e_eV;   // Температура електронів, еВ
    double n_e_m3;   // Густина електронів, м^-3
    double Z_eff;    // Ефективний заряд іонів
    double E_ext;    // Зовнішнє електричне поле, В/м
};

struct SpitzerResults {
    double debye_length_m;      // Радіус Дебая, м
    double coulomb_log;         // Кулонівський логарифм ln(Lambda)
    double eta_parallel_ohm_m;  // Поздовжній питомий опір Spitzer, Ом*м
    double eta_perp_ohm_m;      // Поперечний питомий опір, Ом*м
    double sigma_parallel_S_m;  // Поздожня провідність, См/м
    double dreicer_field_V_m;   // Поле Дрейсера E_D, В/м
    double runaway_ratio;       // Відношення E_ext / E_D
    bool is_runaway_dominated;  // Прапор генерації тікаючих електронів
};

class SpitzerCalculator {
public:
    // Фундаментальні фізичні константи (SI)
    static constexpr double e = 1.602176634e-19;       // Заряд електрона, Кл
    static constexpr double m_e = 9.1093837015e-31;     // Маса електрона, кг
    static constexpr double eps0 = 8.8541878128e-12;    // Електрична стала, Ф/м
    static constexpr double kB = 1.380649e-23;          // Константа Больцмана, Дж/К
    static constexpr double hbar = 1.054571817e-34;     // Приведена стала Планка, Дж*с

    static std::optional<SpitzerResults> calculate(const PlasmaState& state) {
        if (state.T_e_eV <= 0.0 || state.n_e_m3 <= 0.0 || state.Z_eff < 1.0) {
            return std::nullopt;
        }

        const double T_e_J = state.T_e_eV * e;
        const double v_th = std::sqrt(2.0 * T_e_J / m_e);

        // 1. Радіус Дебая
        const double lambda_D = std::sqrt((eps0 * T_e_J) / (state.n_e_m3 * e * e));

        // 2. Мінімальний прицільний параметр b_min = max(b_cl, b_qm)
        const double b_cl = (state.Z_eff * e * e) / (4.0 * std::numbers::pi * eps0 * m_e * v_th * v_th);
        const double b_qm = hbar / (2.0 * m_e * v_th);
        const double b_min = std::max(b_cl, b_qm);

        // 3. Кулонівський логарифм
        double ln_lambda = std::log(lambda_D / b_min);
        if (ln_lambda < 2.0) {
            ln_lambda = 2.0; // Нижній поріг для слабонеідеальної плазми
        }

        // 4. Множник Спітцера-Гярма gamma(Z)
        const double gamma_Z = (0.457 * state.Z_eff + 0.582) / (state.Z_eff + 1.079);
        const double gamma_1 = (0.457 * 1.0 + 0.582) / (1.0 + 1.079);

        // Питомий опір лоренцівської плазми
        const double eta_lorentz = (std::numbers::pi * state.Z_eff * e * e * std::sqrt(m_e) * ln_lambda) /
                                  (2.0 * std::pow(4.0 * std::numbers::pi * eps0, 2) * std::pow(T_e_J, 1.5));

        const double eta_parallel = eta_lorentz * (gamma_Z / gamma_1);
        const double eta_perp = 1.96 * eta_parallel; // Для Z=1
        const double sigma_parallel = 1.0 / eta_parallel;

        // 5. Критичне електричне поле Дрейсера E_D
        const double E_D = (e * e * e * state.n_e_m3 * state.Z_eff * ln_lambda) /
                           (4.0 * std::numbers::pi * std::pow(eps0, 2) * T_e_J);

        const double ratio = state.E_ext / E_D;
        const bool runaway = (ratio > 0.02);

        return SpitzerResults{
            .debye_length_m = lambda_D,
            .coulomb_log = ln_lambda,
            .eta_parallel_ohm_m = eta_parallel,
            .eta_perp_ohm_m = eta_perp,
            .sigma_parallel_S_m = sigma_parallel,
            .dreicer_field_V_m = E_D,
            .runaway_ratio = ratio,
            .is_runaway_dominated = runaway
        };
    }
};

} // namespace plasma

int main() {
    using namespace plasma;

    // Параметри гарячої плазми токамака ITER
    PlasmaState iter_core{
        .T_e_eV = 10000.0,  // 10 кеВ
        .n_e_m3 = 1e20,     // 10^20 м^-3
        .Z_eff = 1.3,       // Легка домішка вуглецю/берилію
        .E_ext = 0.05       // 0.05 В/м
    };

    auto res = SpitzerCalculator::calculate(iter_core);
    if (!res) {
        std::cerr << "Помилка розрахунку параметрів плазми!\n";
        return 1;
    }

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "=== Розрахунок провідності плазми Spitzer (ITER Core) ===\n";
    std::cout << "Радіус Дебая:             " << res->debye_length_m << " м\n";
    std::cout << "Кулонівський логарифм:    " << res->coulomb_log << "\n";
    std::cout << "Опір eta_parallel:       " << res->eta_parallel_ohm_m << " Ом*м\n";
    std::cout << "Опір міді (300 K):        1.7000e-08 Ом*м\n";
    std::cout << "Поздовжня провідність:    " << res->sigma_parallel_S_m << " См/м\n";
    std::cout << "Поле Дрейсера E_D:        " << res->dreicer_field_V_m << " В/м\n";
    std::cout << "Відношення E / E_D:       " << res->runaway_ratio << "\n";
    std::cout << "Режим тікання:            " << (res->is_runaway_dominated ? "АКТИВНИЙ" : "НІ") << "\n";

    return 0;
}
