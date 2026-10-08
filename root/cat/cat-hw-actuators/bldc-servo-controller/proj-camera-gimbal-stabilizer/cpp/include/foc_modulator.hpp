#pragma once

#include <cstdint>

namespace gimbal {

/// @brief Двофазна непорушна система координат Кларка (Alpha, Beta)
struct AlphaBeta {
    float alpha{0.0f};
    float beta{0.0f};
};

/// @brief Двофазна обертова система координат Парка (Direct, Quadrature)
struct DQ {
    float d{0.0f};
    float q{0.0f};
};

/// @brief Трифазні коефіцієнти заповнення ШІМ для силового інвертора [0.0 ... 1.0]
struct DutyCycles {
    float a{0.0f};
    float b{0.0f};
    float c{0.0f};
};

/// @brief Клас векторного керування BLDC мотором (FOC & SVPWM)
class FocModulator {
public:
    FocModulator() = default;

    /// @brief Конфігурація апаратних параметрів мотора та живлення
    /// @param pole_pairs Кількість полюсних пар ротора
    /// @param bus_voltage_v Напруга шини постійного струму DC Bus (В)
    void init(uint8_t pole_pairs, float bus_voltage_v);

    /// @brief Пряме перетворення Кларка (3 фази -> Alpha/Beta)
    static AlphaBeta clarke_transform(float ia, float ib, float ic);

    /// @brief Пряме перетворення Парка (Alpha/Beta -> D/Q)
    static DQ park_transform(AlphaBeta ab, float electrical_angle_rad);

    /// @brief Зворотне перетворення Парка (D/Q -> Alpha/Beta)
    static AlphaBeta inverse_park_transform(DQ dq, float electrical_angle_rad);

    /// @brief Просторово-векторна модуляція ШІМ (SVPWM) з додаванням третьої гармоніки
    /// @param ab Напруги в ортогональній системі Alpha/Beta
    /// @return Коефіцієнти трифазного ШІМ для фаз A, B, C
    DutyCycles compute_svpwm(AlphaBeta ab);

    /// @brief Повний розрахунок вектора керування та генерація ШІМ
    /// @param target_dq Задані вектори напруги / струму (Id, Iq)
    /// @param mechanical_angle_rad Поточний механічний кут ротора
    /// @return Згенеровані коефіцієнти ШІМ
    DutyCycles update(DQ target_dq, float mechanical_angle_rad);

    /// @brief Розрахунок електричного кута за механічним кутом та кількістю полюсів
    float calculate_electrical_angle(float mechanical_angle_rad) const;

private:
    static float clamp(float val, float min_v, float max_v);

    uint8_t pole_pairs_{7};
    float bus_voltage_v_{12.0f};
    bool initialized_{false};
};

} // namespace gimbal
