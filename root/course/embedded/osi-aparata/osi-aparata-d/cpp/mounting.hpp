#pragma once

#include "linalg.hpp"

#include <expected>
#include <span>
#include <vector>

namespace nav {

// Дискретна орієнтація плати чвертями оберту, R = Rz·Ry·Rx.
struct BoardRotation {
    int roll_q{};
    int pitch_q{};
    int yaw_q{};

    [[nodiscard]] Matrix3 matrix() const noexcept;
};

// Усі унікальні положення плати; їх рівно 24 — стільки в куба поворотів.
[[nodiscard]] std::vector<Matrix3> enumerate_board_rotations();

enum class MountingError { AngleTooLarge, Degenerate };

// Калібрування чипа відносно тіла апарата: зсув, чутливість, перекіс, орієнтація плати.
class SensorCalibration {
public:
    void set_scale(const Matrix3& scale_ortho) noexcept;
    [[nodiscard]] std::expected<void, MountingError> set_misalignment(const Vector3& small_angles_rad) noexcept;
    void set_board(const BoardRotation& rotation) noexcept;
    void set_bias_polynomial(std::span<const Vector3, 4> coefficients, float t_ref_c) noexcept;

    [[nodiscard]] Vector3 bias_at(float temp_c) const noexcept;
    // v_body = R_board·R_align·S·(v_raw − b_bias(T))
    [[nodiscard]] Vector3 apply(const Vector3& raw, float temp_c) const noexcept;

    [[nodiscard]] const Matrix3& board() const noexcept { return board_; }
    [[nodiscard]] float orthogonality_error() const noexcept;
    [[nodiscard]] bool sane() const noexcept;

private:
    void rebuild() noexcept;

    std::array<Vector3, 4> bias_{};
    float t_ref_c_{25.0F};
    Matrix3 scale_{Matrix3::identity()};
    Matrix3 align_{Matrix3::identity()};
    Matrix3 board_{Matrix3::identity()};
    Matrix3 combined_{Matrix3::identity()};   // рахуємо раз, у циклі одне множення
};

}  // namespace nav
