#pragma once

// Передстартова перевірка цілі: геозона, здоров'я навігації та енергетичний
// бюджет «дійти до цілі й повернутися додому» з урахуванням вітру.

#include <expected>

#include "goal.hpp"

namespace autonomy {

struct FlightEnvelope {
    // Прямокутна геозона в NED, метри.
    float min_x{-500.0F};
    float min_y{-500.0F};
    float max_x{500.0F};
    float max_y{500.0F};
    float max_altitude{120.0F};    // максимальна висота над точкою старту, метри
    Vec3 home{};                   // точка повернення
    float ekf_variance_limit{1.0F};// допустима дисперсія оцінки позиції, м²
    float rth_voltage{21.6F};      // напруга запуску повернення, В
    float rth_airspeed{14.0F};     // швидкість на зворотному відрізку, м/с
    float energy_reserve{1.25F};   // коефіцієнт резерву: 1.25 = запас 25%
};

// Час прольоту відрізка за трикутником швидкостей. Помилка означає, що трек
// недосяжний: або боковий знос більший за повітряну швидкість, або зустрічний
// вітер сильніший за апарат.
[[nodiscard]] std::expected<Seconds, RejectReason> leg_time(Vec3 from, Vec3 to, float airspeed,
                                                            Vec3 wind) noexcept;

// Скільки Вт·год треба на «дійти й повернутися».
[[nodiscard]] std::expected<float, RejectReason> round_trip_energy(const Goal& g, const Vehicle& v,
                                                                   const FlightEnvelope& env) noexcept;

// Повна перевірка допуску цілі: порожній результат означає «можна виконувати».
[[nodiscard]] std::expected<void, RejectReason> preflight(const Goal& g, const Vehicle& v,
                                                          const FlightEnvelope& env) noexcept;

} // namespace autonomy
