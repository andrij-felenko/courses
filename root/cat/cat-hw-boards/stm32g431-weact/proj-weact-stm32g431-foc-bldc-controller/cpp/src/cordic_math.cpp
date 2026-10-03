#include "cordic_math.hpp"
#include <algorithm>

namespace foc {

bool CordicMath::init() {
#ifdef CORDIC
    // Включення тактування апаратного CORDIC у регістрі AHB1ENR
    RCC->AHB1ENR |= RCC_AHB1ENR_CORDICEN;
#endif
    return true;
}

SinCos CordicMath::calculateSinCos(float angle_rad) {
    // Нормалізація кута у діапазон [-PI, PI]
    constexpr float M_PI_F = 3.14159265358979323846f;
    while (angle_rad > M_PI_F)  { angle_rad -= 2.0f * M_PI_F; }
    while (angle_rad < -M_PI_F) { angle_rad += 2.0f * M_PI_F; }

#ifdef CORDIC
    // Масштабування кута у формат з фіксованою точкою Q1.31 [-1.0 .. 1.0)
    int32_t q31_angle = static_cast<int32_t>((angle_rad / M_PI_F) * 2147483648.0f);

    // Конфігурація CORDIC:
    // FUNC = 0 (Cosine), PRECISION = 6 (24 ітерації / 6 циклів), NRES = 2 (повертати і cos, і sin)
    CORDIC->CSR = (0u << CORDIC_CSR_FUNC_Pos) |
                  (6u << CORDIC_CSR_PRECISION_Pos) |
                  CORDIC_CSR_NRES;

    // Запис вхідного кута у WDATA
    CORDIC->WDATA = static_cast<uint32_t>(q31_angle);

    // Читання результатів у форматі Q1.31: Перше читання — Cosine, друге — Sine
    int32_t q31_cos = static_cast<int32_t>(CORDIC->RDATA);
    int32_t q31_sin = static_cast<int32_t>(CORDIC->RDATA);

    SinCos result;
    result.cos_val = static_cast<float>(q31_cos) / 2147483648.0f;
    result.sin_val = static_cast<float>(q31_sin) / 2147483648.0f;
    return result;
#else
    // Програмна реалізація у разі відсутності апаратного модуля CORDIC
    SinCos result;
    result.sin_val = std::sin(angle_rad);
    result.cos_val = std::cos(angle_rad);
    return result;
#endif
}

Vector2D CordicMath::clarkeTransform(float i_a, float i_b) {
    Vector2D out;
    out.x = i_a;
    out.y = (i_a + 2.0f * i_b) * ONE_BY_SQRT3;
    return out;
}

Vector2D CordicMath::parkTransform(float alpha, float beta, float sin_th, float cos_th) {
    Vector2D out;
    out.x = alpha * cos_th + beta * sin_th;
    out.y = -alpha * sin_th + beta * cos_th;
    return out;
}

Vector2D CordicMath::invParkTransform(float d, float q, float sin_th, float cos_th) {
    Vector2D out;
    out.x = d * cos_th - q * sin_th;
    out.y = d * sin_th + q * cos_th;
    return out;
}

void CordicMath::invClarkeSVPWM(float v_alpha, float v_beta, float v_dc,
                                float& duty_a, float& duty_b, float& duty_c) {
    if (v_dc <= 0.0f) {
        duty_a = 0.5f; duty_b = 0.5f; duty_c = 0.5f;
        return;
    }

    // Зворотне перетворення Кларка для фазних напруг
    float v_a = v_alpha;
    float v_b = -0.5f * v_alpha + SQRT3_BY_2 * v_beta;
    float v_c = -0.5f * v_alpha - SQRT3_BY_2 * v_beta;

    // Центрування третьої гармоніки (SVPWM centering) для максимального використання шини Vdc
    float v_max = std::max({v_a, v_b, v_c});
    float v_min = std::min({v_a, v_b, v_c});
    float v_zero = -0.5f * (v_max + v_min);

    // Нормалізація напруг відносно Vdc та зміщення у діапазон [0.0 .. 1.0]
    duty_a = (v_a + v_zero) / v_dc + 0.5f;
    duty_b = (v_b + v_zero) / v_dc + 0.5f;
    duty_c = (v_c + v_zero) / v_dc + 0.5f;

    duty_a = std::clamp(duty_a, 0.0f, 1.0f);
    duty_b = std::clamp(duty_b, 0.0f, 1.0f);
    duty_c = std::clamp(duty_c, 0.0f, 1.0f);
}

} // namespace foc
