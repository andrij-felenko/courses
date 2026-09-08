#include "swashplate_mixer.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "=== Тестування математичного мікшера автомата перекосу CCPM ===\n\n";

    SwashplateConfig config{};
    config.type = CcpmType::CCPM_120;
    config.arm_length_mm = 20.0f;
    config.max_travel_mm = 12.0f;
    config.ring_limit_norm = 1.0f;

    SwashplateMixer mixer(config);

    // Тест 1: Нейтральне положення
    ControlInput in_neutral{0.0f, 0.0f, 0.0f};
    ServoOutput out_neutral = mixer.update(in_neutral);
    std::cout << "1. Нейтраль (coll=0, pitch=0, roll=0):\n";
    std::cout << "   ШІМ серво [мкс]: S1=" << out_neutral.pwm_us[0]
              << ", S2=" << out_neutral.pwm_us[1]
              << ", S3=" << out_neutral.pwm_us[2] << "\n\n";

    // Тест 2: Повний спільний крок
    ControlInput in_coll{1.0f, 0.0f, 0.0f};
    ServoOutput out_coll = mixer.update(in_coll);
    std::cout << "2. Максимальний спільний крок (coll=1.0):\n";
    std::cout << "   ШІМ серво [мкс]: S1=" << out_coll.pwm_us[0]
              << ", S2=" << out_coll.pwm_us[1]
              << ", S3=" << out_coll.pwm_us[2] << "\n\n";

    // Тест 3: Спрацьовування Swashplate Ring Limiter при перевищенні ходу
    ControlInput in_extreme{0.0f, 1.0f, 1.0f}; // Вектор довжиною sqrt(2) ≈ 1.414 > 1.0
    ServoOutput out_extreme = mixer.update(in_extreme);
    std::cout << "3. Екстремальний перекіс тангажу й крену (pitch=1.0, roll=1.0):\n";
    std::cout << "   (Ring Limiter нормалізував вектор до радіуса 1.0)\n";
    std::cout << "   ШІМ серво [мкс]: S1=" << out_extreme.pwm_us[0]
              << ", S2=" << out_extreme.pwm_us[1]
              << ", S3=" << out_extreme.pwm_us[2] << "\n\n";

    std::cout << "Тестування мікшера успішно завершено.\n";
    return 0;
}
