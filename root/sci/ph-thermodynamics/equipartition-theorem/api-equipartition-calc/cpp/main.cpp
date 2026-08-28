#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <iomanip>

namespace StatisticalPhysics {

constexpr double kBoltzmann = 1.380649e-23; // Дж/К
constexpr double kAvogadro  = 6.02214076e23; // моль^-1
constexpr double kGasConstant = kBoltzmann * kAvogadro; // Дж/(моль·К)

enum class MoleculeType {
    Monatomic,
    Diatomic,
    PolyatomicLinear,
    PolyatomicNonLinear
};

struct MoleculeConfig {
    MoleculeType type{MoleculeType::Diatomic};
    int degrees_trans{3};
    int degrees_rot{2};
    std::vector<double> vib_temperatures; // Θ_vib у Кельвінах
    double rot_temperature{85.4};          // Θ_rot у Кельвінах
};

class EquipartitionCalculator {
public:
    explicit EquipartitionCalculator(MoleculeConfig config)
        : config_(std::move(config)) {
        validate_config();
    }

    [[nodiscard]] double classical_molar_heat_capacity_cv() const noexcept {
        const int f_vib = static_cast<int>(config_.vib_temperatures.size());
        const double f_total_quad = config_.degrees_trans + config_.degrees_rot + 2.0 * f_vib;
        return 0.5 * f_total_quad * kGasConstant;
    }

    [[nodiscard]] double quantum_molar_heat_capacity_cv(double temp_kelvin) const {
        if (temp_kelvin <= 0.0) {
            throw std::invalid_argument("Температура повинна бути строго додатною.");
        }

        // Поступальний внесок (завжди 1.5 R у класичній області)
        double cv_sum = 0.5 * config_.degrees_trans * kGasConstant;

        // Обертальний внесок (класичний при T > Θ_rot, виморожений при T < Θ_rot)
        if (config_.degrees_rot > 0) {
            if (temp_kelvin > config_.rot_temperature) {
                cv_sum += 0.5 * config_.degrees_rot * kGasConstant;
            } else {
                // Спрощене дворівневе виморожування обертань
                double ratio = config_.rot_temperature / temp_kelvin;
                cv_sum += 0.5 * config_.degrees_rot * kGasConstant * std::exp(-ratio);
            }
        }

        // Коливальний внесок Планка - Ейнштейна для кожної нормальної моди
        for (double theta_vib : config_.vib_temperatures) {
            double x = theta_vib / temp_kelvin;
            if (x > 100.0) {
                // Виморожена мода (забігання експоненціальної переповненості)
                continue;
            }
            double exp_x = std::exp(x);
            double einstein_factor = (x * x * exp_x) / ((exp_x - 1.0) * (exp_x - 1.0));
            cv_sum += kGasConstant * einstein_factor;
        }

        return cv_sum;
    }

    [[nodiscard]] double adiabatic_index_gamma(double temp_kelvin, bool use_quantum = true) const {
        double cv = use_quantum ? quantum_molar_heat_capacity_cv(temp_kelvin)
                                : classical_molar_heat_capacity_cv();
        double cp = cv + kGasConstant;
        return cp / cv;
    }

    [[nodiscard]] static double mems_cantilever_noise_rms(double stiffness, double temp_kelvin) {
        if (stiffness <= 0.0 || temp_kelvin <= 0.0) {
            throw std::invalid_argument("Жорсткість та температура повинні бути додатними.");
        }
        return std::sqrt((kBoltzmann * temp_kelvin) / stiffness);
    }

    [[nodiscard]] static double johnson_nyquist_noise_voltage(double resistance, double temp_kelvin, double bandwidth_hz) {
        if (resistance < 0.0 || temp_kelvin <= 0.0 || bandwidth_hz <= 0.0) {
            throw std::invalid_argument("Некоректні параметри для обчислення шуму Найквіста.");
        }
        return std::sqrt(4.0 * kBoltzmann * temp_kelvin * resistance * bandwidth_hz);
    }

private:
    void validate_config() const {
        if (config_.degrees_trans < 1 || config_.degrees_trans > 3) {
            throw std::invalid_argument("Поступальних ступенів вільності має бути від 1 до 3.");
        }
    }

    MoleculeConfig config_;
};

} // namespace StatisticalPhysics

int main() {
    using namespace StatisticalPhysics;

    // Конфігурація для азоту (N2): 3 поступальні, 2 обертальні, 1 коливальна мода (Θ_vib = 3371 K)
    MoleculeConfig n2_config{
        MoleculeType::Diatomic,
        3, 2, {3371.0}, 2.88
    };

    EquipartitionCalculator calc(n2_config);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Класична C_V: " << calc.classical_molar_heat_capacity_cv() << " Дж/(моль·К)\n\n";

    std::cout << "Т, K\tC_V (квантова)\tGamma\n";
    for (double T : {50.0, 300.0, 1500.0, 3000.0}) {
        double cv_q = calc.quantum_molar_heat_capacity_cv(T);
        double gamma = calc.adiabatic_index_gamma(T, true);
        std::cout << T << "\t" << cv_q << "\t\t" << gamma << "\n";
    }

    double cant_noise = EquipartitionCalculator::mems_cantilever_noise_rms(0.1, 300.0);
    std::cout << "\nТеплове тремтіння кантилевера (k=0.1 N/m, 300K): " << cant_noise * 1e9 << " нм\n";

    double noise_v = EquipartitionCalculator::johnson_nyquist_noise_voltage(1000.0, 300.0, 1e6);
    std::cout << "Шум Найквіста резистора (1 kOhm, 1 MHz, 300K): " << noise_v * 1e6 << " мкВ\n";

    return 0;
}
