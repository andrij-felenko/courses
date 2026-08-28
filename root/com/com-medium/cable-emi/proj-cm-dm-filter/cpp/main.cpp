#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <iomanip>

struct ModeSignals {
    std::vector<double> dm;
    std::vector<double> cm;
};

/* Клас аналізатора модального розкладу та цифрової фільтрації */
class DifferentialLineProcessor {
public:
    /* Розділення виміряних сигналів на протифазну та синфазну компоненти */
    static ModeSignals decompose(std::span<const double> va, std::span<const double> vb) {
        const size_t n = std::min(va.size(), vb.size());
        ModeSignals result;
        result.dm.reserve(n);
        result.cm.reserve(n);

        for (size_t i = 0; i < n; ++i) {
            result.dm.push_back(va[i] - vb[i]);
            result.cm.push_back(0.5 * (va[i] + vb[i]));
        }
        return result;
    }

    /* Адаптивне придушення синфазної завади методом LMS (Widrow-Hoff) */
    static std::vector<double> cancelInterference(
        std::span<const double> v_dm,
        std::span<const double> v_cm,
        double mu = 0.01)
    {
        const size_t n = std::min(v_dm.size(), v_cm.size());
        std::vector<double> clean_dm;
        clean_dm.reserve(n);

        double w = 0.0; /* ваговий коефіцієнт проникнення завади CM -> DM */
        for (size_t i = 0; i < n; ++i) {
            double estimated_leak = w * v_cm[i];
            double error = v_dm[i] - estimated_leak;
            clean_dm.push_back(error);
            w += mu * error * v_cm[i];
        }
        return clean_dm;
    }

    /* Обчислення наведеної напруги за передавальним імпедансом екрана Z_T */
    static constexpr double transferImpedanceVoltage(
        double shield_current_rms,
        double z_transfer_ohm_per_m,
        double cable_length_m) noexcept
    {
        return shield_current_rms * z_transfer_ohm_per_m * cable_length_m;
    }
};

int main() {
    constexpr size_t sampleCount = 1000;
    constexpr double f_sig = 1000.0;    // 1 кГц корисний сигнал
    constexpr double f_emi = 50000.0;   // 50 кГц синфазна завада від ШІМ
    constexpr double fs = 500000.0;     // 500 кГц частота квантування АЦП
    constexpr double alpha_leak = 0.05; // 5% асиметрія провідників лінії

    std::vector<double> va(sampleCount);
    std::vector<double> vb(sampleCount);

    for (size_t i = 0; i < sampleCount; ++i) {
        double t = static_cast<double>(i) / fs;
        double sig_dm = 1.0 * std::sin(2.0 * std::numbers::pi * f_sig * t);
        double emi_cm = 3.0 * std::sin(2.0 * std::numbers::pi * f_emi * t);

        va[i] = (0.5 * sig_dm) + emi_cm;
        vb[i] = (-0.5 * sig_dm) + emi_cm * (1.0 - alpha_leak);
    }

    auto modes = DifferentialLineProcessor::decompose(va, vb);
    auto clean_dm = DifferentialLineProcessor::cancelInterference(modes.dm, modes.cm, 0.01);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Індекс | V_a (В)  | V_b (В)  | V_DM вихідна | V_CM завада | V_DM очищена\n";
    std::cout << "--------------------------------------------------------------------\n";
    for (size_t i = 0; i < 5; ++i) {
        std::cout << std::setw(6) << i << " | "
                  << std::setw(8) << va[i] << " | "
                  << std::setw(8) << vb[i] << " | "
                  << std::setw(12) << modes.dm[i] << " | "
                  << std::setw(11) << modes.cm[i] << " | "
                  << std::setw(12) << clean_dm[i] << "\n";
    }

    return 0;
}
