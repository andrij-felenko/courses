#pragma once

#include "linalg.hpp"

#include <expected>
#include <optional>
#include <span>
#include <string_view>

namespace nav {

// Статичні дані бачать лише MᵀM, тому за представника класу беремо нижню трикутну M:
// вона єдина з додатною діагоналлю. Обертальної частини тумблінг не спостерігає
// взагалі — її дає механічне пристосування, а не набір позицій.
enum class SensorModel {
    Diagonal,   // 3 масштаби + 3 зсуви: вистачає шести граней
    Triaxial    // 6 елементів M + 3 зсуви: потрібно щонайменше дев'ять положень
};

struct TumbleFit {
    Matrix3 m{Matrix3::identity()};
    Vector3 bias{};
    float rms_rel{};      // нев'язка норми як частка від g
    int iterations{};
};

enum class FitError {
    TooFewPositions,
    FacesNotCovered,
    BadSample,
    SingularNormalEquations,
    NoConvergence
};

[[nodiscard]] std::string_view describe(FitError e) noexcept;

// Гаус-Ньютон із демпфуванням Левенберга: вписує хмару вимірів в еліпсоїд
// і шукає деформацію, що стискає його у сферу радіуса g.
[[nodiscard]] std::expected<TumbleFit, FitError> fit_static_positions(
    std::span<const Vector3> averages, float gravity, SensorModel model);

// Позиція годиться, лише якщо апарат справді стояв.
[[nodiscard]] std::optional<Vector3> still_average(std::span<const Vector3> samples,
                                                   float tolerance) noexcept;

}  // namespace nav
