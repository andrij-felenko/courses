#include <system_error>
#include <optional>

namespace atmospheric {

enum class Status {
    Ok = 0,
    NullPointer,
    RhOutOfRange,
    TempOutOfRange,
    MathDomainError
};

// Валідований метод розрахунку з поверненням результату через структуру з відновлюваним статусом
struct CalculationResult {
    float dewPoint;
    Status status;
};

CalculationResult calculateDewPointSafe(float temp, float rh, const MagnusParams& params) noexcept {
    if (rh <= 0.0f || rh > 100.0f) {
        return {0.0f, Status::RhOutOfRange};
    }
    if (temp < -50.0f || temp > 100.0f) {
        return {0.0f, Status::TempOutOfRange};
    }

    float gamma = logf(rh / 100.0f) + (params.b * temp) / (params.c + temp);
    float denom = params.b - gamma;

    if (denom == 0.0f) {
        return {0.0f, Status::MathDomainError};
    }

    return {(params.c * gamma) / denom, Status::Ok};
}

} // namespace atmospheric
