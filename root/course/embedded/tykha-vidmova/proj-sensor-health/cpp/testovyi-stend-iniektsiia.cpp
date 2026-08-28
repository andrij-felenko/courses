#include <iostream>
#include <random>
#include <iomanip>

int main() {
    const SensorGuardConfig cfg{
        .min_plausible   = -20.0f,
        .max_plausible   = 85.0f,
        .max_slew_rate   = 5.0f,
        .min_variance    = 0.0001f,
        .min_samples_var = 20
    };

    SensorHealthGuard guard{cfg};
    std::mt19937 rng(42);
    std::normal_distribution<float> noise(0.0f, 0.05f);

    std::cout << "=== 1. Здоровий сенсор із природним шумом ===\n";
    uint32_t time_ms = 0;
    for (int i = 0; i < 25; ++i) {
        const float sample = 25.0f + noise(rng);
        const auto flags = guard.update(sample, time_ms);
        time_ms += 100;
        if (i == 24) {
            std::cout << "Відлік #" << i << ": T=" << std::fixed << std::setprecision(3)
                      << sample << " C, дисперсія=" << guard.variance()
                      << ", здоровий=" << (guard.is_healthy() ? "ТАК" : "НІ") << '\n';
        }
    }

    std::cout << "\n=== 2. Зависання цифрового виходу (Stuck Value) ===\n";
    for (int i = 0; i < 30; ++i) {
        constexpr float sample = 25.000f;
        const auto flags = guard.update(sample, time_ms);
        time_ms += 100;
        if (has_flag(flags, SensorHealthFlags::ZeroVariance)) {
            std::cout << "Зафіксовано тиху відмову на кроці #" << i
                      << "! ZeroVariance виявлено, дисперсія=" << guard.variance() << '\n';
            break;
        }
    }

    std::cout << "\n=== 3. Мажоритарний кворум 2oo3 при дрейфі одного давача ===\n";
    constexpr float t1 = 25.1f;
    constexpr float t2 = 25.3f;
    constexpr float t3_drifted = 33.8f;
    const auto qr = SensorHealthGuard::vote_2oo3(t1, t2, t3_drifted, 1.0f);

    std::cout << "Входи: S1=" << t1 << ", S2=" << t2 << ", S3=" << t3_drifted << '\n';
    std::cout << "Результат: кворум=" << (qr.quorum_valid ? "ВАЛІДНИЙ" : "ВТРАЧЕНО")
              << ", Т=" << qr.voted_value
              << ", маска дефекту=0x" << std::hex << static_cast<int>(qr.faulty_sensor_mask) << '\n';

    return 0;
}
