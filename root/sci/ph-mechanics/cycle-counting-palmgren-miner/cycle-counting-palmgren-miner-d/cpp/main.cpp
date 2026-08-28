#include <iostream>
#include <vector>
#include <cmath>
#include <span>
#include <optional>
#include <iomanip>

namespace fatigue {

enum class MeanStressModel {
    Goodman,
    Gerber,
    Soderberg
};

struct Cycle {
    double range;  // Розмах напруження Delta sigma
    double mean;   // Середнє напруження sigma_m
    double count;  // 1.0 для повного циклу, 0.5 для напівциклу
};

struct MaterialProperties {
    double ultimate_strength;   // Межа міцності sigma_u, МПа
    double yield_strength;      // Межа плинності sigma_y, МПа
    double reference_stress;    // Опорне напруження sigma_ref, МПа
    double reference_cycles;    // Опорна кількість циклів N_ref
    double basquin_exponent;    // Показник нахилу m
};

class RainflowCounter {
public:
    // Витягування точок реверсу (екстремумів) із неперервного сигналу
    static std::vector<double> extract_reversals(std::span<const double> signal) {
        if (signal.size() < 2) {
            return {};
        }

        std::vector<double> reversals;
        reversals.reserve(signal.size());
        reversals.push_back(signal[0]);

        for (size_t i = 1; i + 1 < signal.size(); ++i) {
            const double d1 = signal[i] - reversals.back();
            const double d2 = signal[i + 1] - signal[i];

            if (std::abs(d1) < 1e-9) {
                continue;
            }

            if ((d1 > 0.0 && d2 < 0.0) || (d1 < 0.0 && d2 > 0.0)) {
                reversals.push_back(signal[i]);
            }
        }

        reversals.push_back(signal.back());
        return reversals;
    }

    // Чотириточковий стековий алгоритм Rainflow за ASTM E1049
    static std::vector<Cycle> count_cycles(std::span<const double> reversals) {
        std::vector<Cycle> cycles;
        if (reversals.size() < 3) {
            return cycles;
        }

        std::vector<double> stack;
        stack.reserve(reversals.size());

        for (const double pt : reversals) {
            stack.push_back(pt);

            while (stack.size() >= 4) {
                const size_t n = stack.size();
                const double s_a = stack[n - 4];
                const double s_b = stack[n - 3];
                const double s_c = stack[n - 2];
                const double s_d = stack[n - 1];

                const double x1 = std::abs(s_b - s_a);
                const double y  = std::abs(s_c - s_b);
                const double x2 = std::abs(s_d - s_c);

                if (y <= x1 && y <= x2) {
                    cycles.push_back(Cycle{
                        .range = y,
                        .mean = 0.5 * (s_b + s_c),
                        .count = 1.0
                    });

                    // Вилучаємо середні точки B та C
                    stack[n - 3] = stack[n - 1];
                    stack.pop_back();
                    stack.pop_back();
                } else {
                    break;
                }
            }
        }

        // Обробка залишку стеку (напівцикли за ASTM E1049)
        for (size_t i = 0; i + 1 < stack.size(); ++i) {
            cycles.push_back(Cycle{
                .range = std::abs(stack[i + 1] - stack[i]),
                .mean = 0.5 * (stack[i] + stack[i + 1]),
                .count = 0.5
            });
        }

        return cycles;
    }
};

class FatigueDamageEstimator {
public:
    explicit FatigueDamageEstimator(MaterialProperties mat)
        : mat_(mat) {}

    // Приведення асиметричного циклу до еквівалентної амплітуди при R = -1
    [[nodiscard]] double equivalent_amplitude(double amplitude, double mean, 
                                            MeanStressModel model = MeanStressModel::Goodman) const {
        if (mean <= 0.0) {
            // Стискальне середнє напруження не знижує границю витривалості
            return amplitude;
        }

        switch (model) {
            case MeanStressModel::Goodman:
                if (mean >= mat_.ultimate_strength) return 1e9;
                return amplitude / (1.0 - mean / mat_.ultimate_strength);

            case MeanStressModel::Gerber: {
                const double ratio = mean / mat_.ultimate_strength;
                if (ratio >= 1.0) return 1e9;
                return amplitude / (1.0 - ratio * ratio);
            }

            case MeanStressModel::Soderberg:
                if (mean >= mat_.yield_strength) return 1e9;
                return amplitude / (1.0 - mean / mat_.yield_strength);
        }
        return amplitude;
    }

    // Гранична кількість циклів до руйнування за Басквіном
    [[nodiscard]] double cycles_to_failure(double eq_amplitude) const {
        if (eq_amplitude <= 0.0) {
            return 1e30;
        }
        return mat_.reference_cycles * std::pow(mat_.reference_stress / eq_amplitude, mat_.basquin_exponent);
    }

    // Розрахунок сумарного пошкодження за правилом Пальмгрена - Майнера
    [[nodiscard]] double compute_damage(std::span<const Cycle> cycles, 
                                       MeanStressModel model = MeanStressModel::Goodman) const {
        double total_damage = 0.0;
        for (const auto& cycle : cycles) {
            const double amp = cycle.range * 0.5;
            const double eq_amp = equivalent_amplitude(amp, cycle.mean, model);
            const double n_fail = cycles_to_failure(eq_amp);

            if (n_fail > 0.0) {
                total_damage += cycle.count / n_fail;
            }
        }
        return total_damage;
    }

private:
    MaterialProperties mat_;
};

} // namespace fatigue

int main() {
    // Вхідний масив відліків напруження (МПа)
    const std::vector<double> stress_signal = {
        0.0, 120.0, -40.0, 180.0, 40.0, 140.0, 
        20.0, 260.0, -80.0, 200.0, 60.0, 160.0, 0.0
    };

    const fatigue::MaterialProperties duralumin = {
        .ultimate_strength = 470.0,  // sigma_u = 470 МПа
        .yield_strength    = 325.0,  // sigma_y = 325 МПа
        .reference_stress  = 180.0,  // sigma_ref = 180 МПа
        .reference_cycles  = 1.0e6,  // N_ref = 10^6
        .basquin_exponent  = 6.5     // m = 6.5
    };

    // 1. Витягування поворотних точок
    const auto reversals = fatigue::RainflowCounter::extract_reversals(stress_signal);

    // 2. Підрахунок циклів Rainflow за ASTM E1049
    const auto cycles = fatigue::RainflowCounter::count_cycles(reversals);

    // 3. Розрахунок втомного пошкодження
    const fatigue::FatigueDamageEstimator estimator(duralumin);
    const double damage = estimator.compute_damage(cycles, fatigue::MeanStressModel::Goodman);
    const double blocks_to_failure = (damage > 0.0) ? (1.0 / damage) : 1e30;

    std::cout << std::scientific << std::setprecision(6);
    std::cout << "=== Результати Rainflow та розрахунку ресурсу (Modern C++20) ===\n";
    std::cout << "Відліків сигналу: " << stress_signal.size() << " | Точок реверсу: " << reversals.size() << "\n";
    std::cout << "Виявлено циклів та напівциклів: " << cycles.size() << "\n";
    std::cout << "Пошкодження за блок D: " << damage << "\n";
    std::cout << std::fixed << std::setprecision(1);
    std::cout << "Прогнозований ресурс: " << blocks_to_failure << " блоків навантаження\n";

    return 0;
}
