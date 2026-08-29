#pragma once

#include "rotation.hpp"

#include <cstdint>
#include <optional>

namespace nav {

// Двошвидкісний оцінювач орієнтації для базису NED/FRD.
// Швидкий контур (1–8 кГц) накопичує приріст кута й конічну поправку,
// повільний (100–250 Гц) застосовує його одним поворотом і підтягує вертикаль.
class AttitudeEstimator {
public:
    struct Gains {
        float kp{1.0F};   // сила корекції за акселерометром
        float ki{0.05F};  // швидкість вивчення зсуву нуля гіроскопа
    };

    explicit AttitudeEstimator(Gains gains, bool coning_enabled = true) noexcept
        : gains_(gains), coning_enabled_(coning_enabled) {}

    void push_gyro(const Vector3& omega_body, float dt) noexcept;
    // std::nullopt — такт лише поширює орієнтацію, без корекції вертикалі.
    void update(std::optional<Vector3> accel_body, float dt) noexcept;

    [[nodiscard]] Quaternion orientation() const noexcept { return q_; }
    [[nodiscard]] EulerAngles euler() const noexcept { return q_.to_euler(); }
    [[nodiscard]] Vector3 gyro_bias() const noexcept { return bias_; }
    [[nodiscard]] std::uint32_t rejected_accel() const noexcept { return rejected_; }
    [[nodiscard]] std::uint32_t faults() const noexcept { return faults_; }

private:
    Gains gains_{};
    bool coning_enabled_{true};
    float accel_gate_{0.10F};        // допустиме відхилення |a| від 1g, частка
    Quaternion q_{};
    Vector3 bias_{};
    Vector3 delta_theta_{};
    Vector3 prev_delta_{};
    Vector3 coning_{};
    std::uint32_t fast_steps_{};
    std::uint32_t rejected_{};
    std::uint32_t faults_{};
};

}  // namespace nav
