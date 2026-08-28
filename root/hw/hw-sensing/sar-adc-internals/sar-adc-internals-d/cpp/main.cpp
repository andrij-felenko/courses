#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <array>
#include <span>
#include <iomanip>

class SarAdcSimulator {
public:
    static constexpr unsigned int Bits = 12;
    static constexpr unsigned int TotalCodes = 1U << Bits;

    struct Config {
        double vref = 3.3;             // Опорна напруга, В
        double c_unit = 25e-15;        // Базова одинична ємність 25 фФ
        double r_src = 10000.0;        // Опір джерела сигналу, Ом
        double r_switch = 1500.0;      // Опір внутрішнього ключа, Ом
        double t_acq = 1.2e-6;         // Час вікна вибірки, с
        double comp_offset = 0.0004;   // Напруга зсуву компаратора (400 мкВ)
        double comp_noise_rms = 1.5e-4;// Шум компаратора (150 мкВ)
        double cap_mismatch_std = 0.002;// Технологічний розкид ємності (0.2%)
        double temp_k = 300.0;         // Температура 300 К
    };

    explicit SarAdcSimulator(const Config& cfg)
        : config_(cfg),
          rng_(std::random_device{}()) {
        initializeCapacitorArray();
    }

    [[nodiscard]] unsigned int convert(double v_in) {
        // 1. Динаміка заряду вхідної комутованої ємності
        const double tau = (config_.r_src + config_.r_switch) * total_capacitance_;
        const double settling_factor = 1.0 - std::exp(-config_.t_acq / tau);
        double v_sampled = v_in * settling_factor;

        // 2. Додавання замороженого теплового шуму kT/C
        constexpr double kb = 1.380649e-23;
        const double kt_c_rms = std::sqrt((kb * config_.temp_k) / total_capacitance_);
        std::normal_distribution<double> kt_dist(0.0, kt_c_rms);
        v_sampled += kt_dist(rng_);

        // 3. Фіксація заряду та інверсія потенціалу вузла
        double v_x = -v_sampled;
        unsigned int digital_code = 0;

        // 4. Порозрядне бінарне зважування (SAR FSM)
        std::normal_distribution<double> comp_noise_dist(0.0, config_.comp_noise_rms);
        const double c_tot_weights = static_cast<double>(TotalCodes);

        for (int bit = static_cast<int>(Bits) - 1; bit >= 0; --bit) {
            const double v_step = config_.vref * (cap_weights_[bit] / c_tot_weights);
            const double v_x_probe = v_x + v_step;

            const double threshold = config_.comp_offset + comp_noise_dist(rng_);

            if (v_x_probe < threshold) {
                digital_code |= (1U << bit);
                v_x = v_x_probe; // Зберегти розряд
            }
        }

        return digital_code;
    }

    [[nodiscard]] double codeToVoltage(unsigned int code) const noexcept {
        return (static_cast<double>(code) * config_.vref) / static_cast<double>(TotalCodes - 1);
    }

private:
    void initializeCapacitorArray() {
        double accumulated_c = 0.0;
        for (size_t i = 0; i < Bits; ++i) {
            const double ideal_weight = static_cast<double>(1U << i);
            const double sigma = config_.cap_mismatch_std / std::sqrt(ideal_weight);
            std::normal_distribution<double> mismatch_dist(0.0, sigma);

            cap_weights_[i] = ideal_weight * (1.0 + mismatch_dist(rng_));
            accumulated_c += cap_weights_[i] * config_.c_unit;
        }
        accumulated_c += 1.0 * config_.c_unit; // Dummy capacitor 1C
        total_capacitance_ = accumulated_c;
    }

    Config config_;
    std::mt19937 rng_;
    std::array<double, Bits> cap_weights_{};
    double total_capacitance_{0.0};
};

int main() {
    SarAdcSimulator::Config cfg;
    SarAdcSimulator adc(cfg);

    std::cout << "=== Поведінкова модель SAR АЦП 12-біт (C++20) ===\n";
    constexpr std::array<double, 5> test_voltages{0.0, 0.825, 1.650, 2.475, 3.300};

    std::cout << std::fixed << std::setprecision(4);
    for (double v : test_voltages) {
        unsigned int code = adc.convert(v);
        double reconstructed = adc.codeToVoltage(code);
        double error_mv = (reconstructed - v) * 1000.0;

        std::cout << "Вхід: " << std::setw(6) << v << " В -> "
                  << "Код: " << std::setw(4) << code << " -> "
                  << "Відновлено: " << std::setw(6) << reconstructed << " В "
                  << "(Похибка: " << std::showpos << std::setw(6) << std::setprecision(2)
                  << error_mv << " мВ)\n"
                  << std::noshowpos << std::setprecision(4);
    }
    return 0;
}
