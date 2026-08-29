// ===========================================================================
//  mag_cal/calibration.hpp — результат підгонки та пороги придатності
// ===========================================================================
#pragma once

#include <cstdint>

#include "mag_cal/geometry.hpp"

namespace mag_cal {

// Пороги конвеєра. Не параметри збірки й не поля конфігурації: числа взяті
// з поведінки живого апарата й змінюються разом із кодом, що їх тлумачить.
namespace limits {
inline constexpr float kMaxRmsUt = 3.0F;          // гейт нев'язки, мкТл
inline constexpr float kMaxCondition = 2.5F;      // гейт зумовленості W
inline constexpr float kGyroLimitRadS = 1.745F;   // 100 °/с
inline constexpr float kMinCoveragePct = 60.0F;   // менше — не рахуємо
inline constexpr float kSolveCoveragePct = 80.0F; // стільки — запускаємо
inline constexpr std::size_t kMinSamples = 40;
inline constexpr float kDefaultEarthUt = 45.0F;
inline constexpr float kMaxOffsetUt = 1500.0F;
inline constexpr float kMaxGain = 5.0F;
inline constexpr std::uint32_t kIdleTimeoutMs = 60'000;
}  // namespace limits

struct Calibration {
    Vec3 offset{};                                   // Hard Iron, V0 (мкТл)
    Mat3 soft_iron{};                                // Soft Iron, W
    float earth_field{limits::kDefaultEarthUt};      // еталонний модуль, мкТл
    float rms_residual{0.0F};                        // нев'язка, мкТл
    float sphere_radius{limits::kDefaultEarthUt};    // середній модуль після корекції
    float condition{1.0F};
    float coverage_pct{0.0F};
    std::uint16_t points_used{0};
    std::uint8_t iterations{0};
    std::uint8_t compass_id{0};
    bool valid{false};

    [[nodiscard]] Vec3 apply(const Vec3& raw) const noexcept {
        if (!valid) {
            return raw;   // некалібрований компас віддає вимір як є
        }
        return soft_iron * (raw - offset);
    }

    // Чи має право цей набір коефіцієнтів керувати апаратом
    [[nodiscard]] bool passes_quality_gates() const noexcept {
        return rms_residual <= limits::kMaxRmsUt && condition < limits::kMaxCondition;
    }
};

}  // namespace mag_cal
