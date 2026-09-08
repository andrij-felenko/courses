#include "swashplate_mixer.hpp"
#include <cmath>
#include <algorithm>

SwashplateMixer::SwashplateMixer(const SwashplateConfig& config) noexcept
    : config_(config) {}

ControlInput SwashplateMixer::applyRingLimiter(const ControlInput& input) const noexcept {
    ControlInput filtered = input;
    
    // Обчислення довжини результуючого вектора циклічного перекосу
    const float pitch = input.cyclic_pitch;
    const float roll = input.cyclic_roll;
    const float cyclic_magnitude = std::sqrt(pitch * pitch + roll * roll);
    
    const float max_limit = (config_.ring_limit_norm > 0.0f) ? config_.ring_limit_norm : 1.0f;
    
    // Якщо сумарний вектор перевищує межу кругового вікна ходу тарілки
    if (cyclic_magnitude > max_limit && cyclic_magnitude > 1e-6f) {
        const float scale = max_limit / cyclic_magnitude;
        filtered.cyclic_pitch = pitch * scale;
        filtered.cyclic_roll = roll * scale;
    }
    
    // Обмеження спільного кроку діапазоном [-1.0, 1.0]
    filtered.collective = std::clamp(input.collective, -1.0f, 1.0f);
    
    return filtered;
}

float SwashplateMixer::linearizeServoArm(float linear_travel_mm) const noexcept {
    if (config_.arm_length_mm <= 1e-3f) {
        return 0.0f;
    }
    // Нормалізований аргумент для arcsin: sin(alpha) = Delta_z / L_arm
    const float sin_val = std::clamp(linear_travel_mm / config_.arm_length_mm, -1.0f, 1.0f);
    return std::asin(sin_val);
}

uint16_t SwashplateMixer::angleToPwmUs(float angle_rad) noexcept {
    // Припускаємо максимальний робочий кут сервопривода ±60° (±pi/3 рад)
    constexpr float MAX_ANGLE_RAD = 1.04719755f; // 60 градусів у радіанах
    constexpr float CENTER_PWM_US = 1500.0f;
    constexpr float HALF_RANGE_US = 500.0f; // Діапазон від 1000 до 2000 мкс
    
    const float norm = std::clamp(angle_rad / MAX_ANGLE_RAD, -1.0f, 1.0f);
    const float pwm = CENTER_PWM_US + norm * HALF_RANGE_US;
    
    return static_cast<uint16_t>(std::clamp(pwm, 1000.0f, 2000.0f));
}

ServoOutput SwashplateMixer::update(const ControlInput& input) noexcept {
    // Крок 1: Захист від заклинювання тарілки через круговий обмежувач
    const ControlInput safe_input = applyRingLimiter(input);
    
    // Крок 2: Базові зміщення трьох тяг у міліметрах залежно від кінематичної схеми
    const float half_travel = config_.max_travel_mm * 0.5f;
    const float coll_mm = safe_input.collective * half_travel;
    const float pitch_mm = safe_input.cyclic_pitch * half_travel;
    const float roll_mm = safe_input.cyclic_roll * half_travel;
    
    std::array<float, 3> travel_mm{};
    
    switch (config_.type) {
        case CcpmType::CCPM_120: {
            // CCPM 120°: Серво 1 (задній пітч), Серво 2 (передній лівий), Серво 3 (передній правий)
            constexpr float SIN_60 = 0.86602540f; // sqrt(3)/2
            travel_mm[0] = coll_mm + pitch_mm;
            travel_mm[1] = coll_mm - 0.5f * pitch_mm + SIN_60 * roll_mm;
            travel_mm[2] = coll_mm - 0.5f * pitch_mm - SIN_60 * roll_mm;
            break;
        }
        case CcpmType::CCPM_140: {
            // CCPM 140°: геометрія зі зміщеними на 140° бічними тягами
            constexpr float COS_70 = 0.34202014f;
            constexpr float SIN_70 = 0.93969262f;
            travel_mm[0] = coll_mm + pitch_mm;
            travel_mm[1] = coll_mm - COS_70 * pitch_mm + SIN_70 * roll_mm;
            travel_mm[2] = coll_mm - COS_70 * pitch_mm - SIN_70 * roll_mm;
            break;
        }
        case CcpmType::CCPM_90: {
            // CCPM 90°: пряме розділення без перехресного мікшування кутів
            travel_mm[0] = coll_mm + pitch_mm; // Поздовжнє серво
            travel_mm[1] = coll_mm + roll_mm;  // Поперечне серво
            travel_mm[2] = coll_mm - roll_mm;  // Симетричне поперечне серво
            break;
        }
    }
    
    // Крок 3: Тригонометрична лінеаризація кутів повороту важелів сервомашинок
    ServoOutput output{};
    for (size_t i = 0; i < 3; ++i) {
        const float angle_rad = linearizeServoArm(travel_mm[i]);
        output.pwm_us[i] = angleToPwmUs(angle_rad);
    }
    
    return output;
}
