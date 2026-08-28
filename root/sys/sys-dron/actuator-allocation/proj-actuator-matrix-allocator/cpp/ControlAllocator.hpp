// ============================================================================
// ControlAllocator.hpp
// Модуль матричного розподілу керування польотного контролера (C++20)
// ============================================================================
#pragma once

#include <array>
#include <span>
#include <algorithm>
#include <cmath>
#include <cstdint>

namespace drone::control {

template <std::size_t NumActuators, std::size_t NumAxes = 4>
class ControlAllocator {
public:
    static_assert(NumActuators >= NumAxes, "Кількість приводів має бути не меншою за кількість керованих осей");

    struct Config {
        // Псевдообернена матриця ефективності B^+ (NumActuators рядків, NumAxes стовпчиків)
        std::array<std::array<float, NumAxes>, NumActuators> pseudoInverse{};
        std::array<float, NumActuators> minLimits{}; // Зазвичай 0.0f
        std::array<float, NumActuators> maxLimits{}; // Зазвичай 1.0f
    };

    explicit constexpr ControlAllocator(const Config& cfg) noexcept : config_(cfg) {}

    // Обчислення фізичних сигналів приводів
    [[nodiscard]] std::array<float, NumActuators> allocate(std::span<const float, NumAxes> tau) const noexcept {
        std::array<float, NumActuators> uThrust{};
        std::array<float, NumActuators> uRollPitch{};
        std::array<float, NumActuators> uYaw{};
        std::array<float, NumActuators> uOut{};

        // 1. Роздільне матричне множення
        for (std::size_t i = 0; i < NumActuators; ++i) {
            uThrust[i]    = config_.pseudoInverse[i][0] * tau[0];
            uRollPitch[i] = config_.pseudoInverse[i][1] * tau[1] + config_.pseudoInverse[i][2] * tau[2];
            uYaw[i]       = (NumAxes > 3) ? config_.pseudoInverse[i][3] * tau[3] : 0.0f;
            uOut[i]       = uThrust[i] + uRollPitch[i] + uYaw[i];
        }

        // 2. Пошук екстремумів
        auto [minIt, maxIt] = std::minmax_element(uOut.begin(), uOut.end());
        float minVal = *minIt;
        float maxVal = *maxIt;

        // 3. Десатурація зсувом (Shift Desaturation)
        if (maxVal > 1.0f) {
            const float shift = maxVal - 1.0f;
            for (auto& val : uOut) val -= shift;
            minVal -= shift;
            maxVal = 1.0f;
        }
        if (minVal < 0.0f) {
            const float shift = -minVal;
            for (auto& val : uOut) val += shift;
            maxVal += shift;
            minVal = 0.0f;
        }

        // 4. Пріоритезація: стиснення рискання заради збереження крену й тангажу
        if (maxVal > 1.0f && NumAxes > 3) {
            float maxRp = 0.0f;
            float maxYaw = 0.0f;
            for (std::size_t i = 0; i < NumActuators; ++i) {
                maxRp = std::max(maxRp, std::abs(uRollPitch[i]));
                maxYaw = std::max(maxYaw, std::abs(uYaw[i]));
            }

            const float yawHeadroom = std::max(0.0f, 0.5f - maxRp);
            const float yawScale = (maxYaw > 1e-4f && maxYaw > yawHeadroom) ? (yawHeadroom / maxYaw) : 1.0f;

            for (std::size_t i = 0; i < NumActuators; ++i) {
                uOut[i] = uThrust[i] + uRollPitch[i] + uYaw[i] * yawScale;
            }

            auto [newMin, newMax] = std::minmax_element(uOut.begin(), uOut.end());
            if (*newMax > 1.0f) {
                const float shift = *newMax - 1.0f;
                for (auto& val : uOut) val -= shift;
            }
        }

        // 5. Фінальне жорстке затискання в дозволені фізичні межі
        for (std::size_t i = 0; i < NumActuators; ++i) {
            uOut[i] = std::clamp(uOut[i], config_.minLimits[i], config_.maxLimits[i]);
        }

        return uOut;
    }

private:
    Config config_;
};

} // namespace drone::control
