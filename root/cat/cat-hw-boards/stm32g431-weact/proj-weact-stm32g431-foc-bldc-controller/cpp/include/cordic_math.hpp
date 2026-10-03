#ifndef CORDIC_MATH_HPP
#define CORDIC_MATH_HPP

#include <cstdint>
#include <cmath>

#if __has_include("stm32g4xx.h")
#include "stm32g4xx.h"
#endif

namespace foc {

/**
 * @brief Структура для збереження парних тригонометричних функцій sin/cos.
 */
struct SinCos {
    float sin_val;
    float cos_val;
};

/**
 * @brief 2D Вектор для представлення струмів/напруг у прямокутних системах координат.
 */
struct Vector2D {
    float x; // alpha або d
    float y; // beta або q
};

/**
 * @brief Обгортка над апаратним співпроцесором CORDIC STM32G4.
 * Використовується для прискореного розрахунку перетворень Кларка й Парка.
 */
class CordicMath {
public:
    CordicMath() = default;

    /**
     * @brief Ініціалізація та тактування апаратного блока CORDIC.
     * @return true у разі успіху.
     */
    bool init();

    /**
     * @brief Апаратне обчислення sin та cos кута через CORDIC.
     * @param angle_rad Електричний кут у радіанах [-PI .. PI].
     * @return Обчислена пара sin/cos.
     */
    SinCos calculateSinCos(float angle_rad);

    /**
     * @brief Пряме перетворення Кларка (з 3-фазних струмів Ia, Ib у двофазні I_alpha, I_beta).
     */
    Vector2D clarkeTransform(float i_a, float i_b);

    /**
     * @brief Пряме перетворення Парка (перехід із стаціонарної Alpha-Beta в обертову d-q систему).
     */
    Vector2D parkTransform(float alpha, float beta, float sin_th, float cos_th);

    /**
     * @brief Зворотне перетворення Парка (перехід із d-q в Alpha-Beta систему напруг).
     */
    Vector2D invParkTransform(float d, float q, float sin_th, float cos_th);

    /**
     * @brief Зворотне перетворення Кларка з генерацією Space Vector PWM (SVPWM).
     * @param v_alpha Напруга осі Alpha.
     * @param v_beta Напруга осі Beta.
     * @param v_dc Напруга живильної шини постійного струму.
     * @param duty_a Розрахований duty cycle фази A [0..1].
     * @param duty_b Розрахований duty cycle фази B [0..1].
     * @param duty_c Розрахований duty cycle фази C [0..1].
     */
    void invClarkeSVPWM(float v_alpha, float v_beta, float v_dc,
                        float& duty_a, float& duty_b, float& duty_c);

private:
    static constexpr float ONE_BY_SQRT3 = 0.57735026919f;
    static constexpr float SQRT3_BY_2   = 0.86602540378f;
};

} // namespace foc

#endif // CORDIC_MATH_HPP
