#include <array>
#include <span>
#include <algorithm>
#include <cmath>

namespace drone::control {

template <std::size_t NumActuators = 4>
class ControlAllocator {
public:
    struct Config {
        // Рядки - приводи, стовпчики - [F_z, M_x, M_y, M_z]
        std::array<std::array<float, 4>, NumActuators> bPseudoInv{};
    };

    explicit constexpr ControlAllocator(const Config& config) noexcept : config_(config) {}

    [[nodiscard]] std::array<float, NumActuators> allocate(float thrust, float roll, float pitch, float yaw) const noexcept {
        std::array<float, NumActuators> uThrust{};
        std::array<float, NumActuators> uRollPitch{};
        std::array<float, NumActuators> uYaw{};
        std::array<float, NumActuators> u{};

        // 1. Проектування векторів
        for (std::size_t i = 0; i < NumActuators; ++i) {
            uThrust[i]    = config_.bPseudoInv[i][0] * thrust;
            uRollPitch[i] = config_.bPseudoInv[i][1] * roll + config_.bPseudoInv[i][2] * pitch;
            uYaw[i]       = config_.bPseudoInv[i][3] * yaw;
            u[i]          = uThrust[i] + uRollPitch[i] + uYaw[i];
        }

        // 2. Пошук меж
        auto [minIt, maxIt] = std::minmax_element(u.begin(), u.end());
        float minVal = *minIt;
        float maxVal = *maxIt;

        // 3. Зсув тяги (Thrust Shift)
        if (maxVal > 1.0f) {
            const float shift = maxVal - 1.0f;
            for (auto& val : u) val -= shift;
            minVal -= shift;
            maxVal = 1.0f;
        }
        if (minVal < 0.0f) {
            const float shift = -minVal;
            for (auto& val : u) val += shift;
            maxVal += shift;
            minVal = 0.0f;
        }

        // 4. Стиснення моменту рискання при дефіциті діапазону
        if (maxVal > 1.0f) {
            float maxRp = 0.0f;
            float maxYaw = 0.0f;
            for (std::size_t i = 0; i < NumActuators; ++i) {
                maxRp  = std::max(maxRp, std::abs(uRollPitch[i]));
                maxYaw = std::max(maxYaw, std::abs(uYaw[i]));
            }

            const float yawMargin = std::max(0.0f, 0.5f - maxRp);
            const float kYaw = (maxYaw > 1e-4f && maxYaw > yawMargin) ? (yawMargin / maxYaw) : 1.0f;

            for (std::size_t i = 0; i < NumActuators; ++i) {
                u[i] = uThrust[i] + uRollPitch[i] + uYaw[i] * kYaw;
            }

            auto [newMinIt, newMaxIt] = std::minmax_element(u.begin(), u.end());
            if (*newMaxIt > 1.0f) {
                const float shift = *newMaxIt - 1.0f;
                for (auto& val : u) val -= shift;
            }
        }

        // 5. Затискання в апаратні межі [0.0, 1.0]
        std::array<float, NumActuators> uOut{};
        for (std::size_t i = 0; i < NumActuators; ++i) {
            uOut[i] = std::clamp(u[i], 0.0f, 1.0f);
        }
        return uOut;
    }

private:
    Config config_;
};

} // namespace drone::control
