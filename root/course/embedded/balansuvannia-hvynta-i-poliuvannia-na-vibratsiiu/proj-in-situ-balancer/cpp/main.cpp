#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <optional>
#include <iomanip>

struct BalanceCorrection {
    float mass_mg;
    float angle_deg;
};

class InSituDynamicBalancer {
public:
    explicit InSituDynamicBalancer(float sample_rate_hz)
        : sample_rate_{sample_rate_hz} {}

    // Виділення вектора 1x RPM синхронним квадратурним інтегруванням
    [[nodiscard]] std::complex<float> extractHarmonicVector(
        std::span<const float> samples, float rotation_freq_hz) const {
        
        if (samples.empty() || rotation_freq_hz <= 0.0f) {
            return {0.0f, 0.0f};
        }

        const float dt = 1.0f / sample_rate_;
        const float omega = 2.0f * std::numbers::pi_v<float> * rotation_freq_hz;
        const size_t n = samples.size();

        float sum_cos = 0.0f;
        float sum_sin = 0.0f;

        for (size_t i = 0; i < n; ++i) {
            const float t = static_cast<float>(i) * dt;
            const float phase = omega * t;
            // Вікно Ганна
            const float window = 0.5f * (1.0f - std::cos(2.0f * std::numbers::pi_v<float> * static_cast<float>(i) / static_cast<float>(n - 1)));
            const float val = samples[i] * window;

            sum_cos += val * std::cos(phase);
            sum_sin += val * std::sin(phase);
        }

        const float scale = 4.0f / static_cast<float>(n);
        return {sum_cos * scale, sum_sin * scale};
    }

    // Векторний розрахунок компенсації
    [[nodiscard]] std::optional<BalanceCorrection> computeCorrection(
        std::complex<float> base_vec_v0,
        std::complex<float> trial_vec_v1,
        float trial_mass_mg,
        float trial_angle_deg) const {

        const auto delta_v = trial_vec_v1 - base_vec_v0;
        if (std::abs(delta_v) < 1e-6f) {
            return std::nullopt; // Відсутній вимірний відгук
        }

        const float rad_t = trial_angle_deg * (std::numbers::pi_v<float> / 180.0f);
        const std::complex<float> u_trial = std::polar(trial_mass_mg, rad_t);

        // Чутливість системи S = delta_V / U_trial
        const auto sensitivity = delta_v / u_trial;

        // Коригувальний дисбаланс U_corr = -V0 / S
        const auto u_corr = -base_vec_v0 / sensitivity;

        float angle_deg = std::arg(u_corr) * (180.0f / std::numbers::pi_v<float>);
        if (angle_deg < 0.0f) {
            angle_deg += 360.0f;
        }

        return BalanceCorrection{
            .mass_mg = std::abs(u_corr),
            .angle_deg = angle_deg
        };
    }

private:
    float sample_rate_;
};

int main() {
    constexpr float sample_rate = 8000.0f;
    constexpr float rpm_freq = 200.0f; // 12000 RPM
    constexpr size_t num_samples = 2048;

    std::vector<float> run0(num_samples);
    std::vector<float> run1(num_samples);

    // Моделювання базового прогону (12 м/с², 40 град)
    for (size_t i = 0; i < num_samples; ++i) {
        float t = static_cast<float>(i) / sample_rate;
        float phase0 = 2.0f * std::numbers::pi_v<float> * rpm_freq * t + 40.0f * (std::numbers::pi_v<float> / 180.0f);
        run0[i] = 12.0f * std::cos(phase0) + 1.2f * std::sin(2.0f * std::numbers::pi_v<float> * 600.0f * t);
    }

    // Моделювання прогону з пробним вантажем 100 мг на 0 град (6.5 м/с², 110 град)
    for (size_t i = 0; i < num_samples; ++i) {
        float t = static_cast<float>(i) / sample_rate;
        float phase1 = 2.0f * std::numbers::pi_v<float> * rpm_freq * t + 110.0f * (std::numbers::pi_v<float> / 180.0f);
        run1[i] = 6.5f * std::cos(phase1) + 1.1f * std::sin(2.0f * std::numbers::pi_v<float> * 600.0f * t);
    }

    InSituDynamicBalancer balancer(sample_rate);
    auto v0 = balancer.extractHarmonicVector(run0, rpm_freq);
    auto v1 = balancer.extractHarmonicVector(run1, rpm_freq);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Базовий вектор V0:    |" << std::abs(v0) << "| m/s^2, кут: "
              << (std::arg(v0) * 180.0f / std::numbers::pi_v<float>) << " deg\n";
    std::cout << "Вектор з вантажем V1: |" << std::abs(v1) << "| m/s^2, кут: "
              << (std::arg(v1) * 180.0f / std::numbers::pi_v<float>) << " deg\n";

    if (auto result = balancer.computeCorrection(v0, v1, 100.0f, 0.0f)) {
        std::cout << "\n=== РЕЗУЛЬТАТ БАЛАНСУВАННЯ ===\n";
        std::cout << "1. Зніміть пробний вантаж.\n";
        std::cout << "2. Закріпіть постійний вантаж:\n";
        std::cout << "   -> Маса: " << result->mass_mg << " мг\n";
        std::cout << "   -> Кут:  " << result->angle_deg << " градусів\n";
    } else {
        std::cerr << "Помилка розрахунку: відгук системи нижче рівня шуму.\n";
    }

    return 0;
}
