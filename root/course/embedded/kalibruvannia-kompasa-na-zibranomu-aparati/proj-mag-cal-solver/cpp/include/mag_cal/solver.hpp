// ===========================================================================
//  mag_cal/solver.hpp — підгонка еліпсоїда методом Левенберга — Марквардта
//
//  Розв'язувач не знає ні про накопичувач, ні про автомат: йому подають
//  суцільний масив вимірів і очікуваний модуль поля. Помилка повертається
//  значенням через std::expected — код повернення нікуди не губиться.
// ===========================================================================
#pragma once

#include <expected>
#include <span>
#include <string_view>

#include "mag_cal/calibration.hpp"
#include "mag_cal/geometry.hpp"

namespace mag_cal {

enum class SolveError : std::uint8_t {
    LowCoverage,      // заповнено менше 60 % секторів
    FewSamples,       // точок менше за limits::kMinSamples
    SingularSystem,   // нормальні рівняння вироджені навіть із демпфуванням
    Diverged,         // NaN або втеча параметрів у нефізичну область
    NoConvergence,    // вичерпано ліміт ітерацій без жодного прийнятого кроку
    PoorFitness,      // RMS > 3.0 мкТл
    IllConditioned    // cond(W) >= 2.5
};

[[nodiscard]] std::string_view describe(SolveError error) noexcept;

// Результат невдалої підгонки теж має цінність: оператору треба показати,
// наскільки саме не зійшлося, тому помилка несе останні коефіцієнти.
struct SolveFailure {
    SolveError error{SolveError::FewSamples};
    Calibration partial{};
};

[[nodiscard]] std::expected<Calibration, SolveFailure> fit_ellipsoid(
    std::span<const Vec3> samples, float earth_field_ut,
    float coverage_pct) noexcept;

}  // namespace mag_cal
