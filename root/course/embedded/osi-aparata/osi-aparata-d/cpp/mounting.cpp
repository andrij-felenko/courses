#include "mounting.hpp"

#include <algorithm>

namespace {

// Точні косинуси й синуси чвертей оберту: жодного sin(), жодного округлення.
constexpr std::array<float, 4> kCos{1.0F, 0.0F, -1.0F, 0.0F};
constexpr std::array<float, 4> kSin{0.0F, 1.0F, 0.0F, -1.0F};

constexpr int wrap4(int q) noexcept {
    q %= 4;
    return (q < 0) ? q + 4 : q;
}

bool close(const nav::Matrix3& a, const nav::Matrix3& b) noexcept {
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            if (std::fabs(a.r[i][j] - b.r[i][j]) > 1e-3F) return false;
    return true;
}

}  // namespace

namespace nav {

Matrix3 BoardRotation::matrix() const noexcept {
    const int i = wrap4(roll_q);
    const int j = wrap4(pitch_q);
    const int k = wrap4(yaw_q);
    const Matrix3 rx{{{{1.0F, 0.0F, 0.0F},
                       {0.0F, kCos[i], -kSin[i]},
                       {0.0F, kSin[i], kCos[i]}}}};
    const Matrix3 ry{{{{kCos[j], 0.0F, kSin[j]},
                       {0.0F, 1.0F, 0.0F},
                       {-kSin[j], 0.0F, kCos[j]}}}};
    const Matrix3 rz{{{{kCos[k], -kSin[k], 0.0F},
                       {kSin[k], kCos[k], 0.0F},
                       {0.0F, 0.0F, 1.0F}}}};
    return rz * ry * rx;
}

std::vector<Matrix3> enumerate_board_rotations() {
    std::vector<Matrix3> unique;
    unique.reserve(24);
    for (int r = 0; r < 4; ++r) {
        for (int p = 0; p < 4; ++p) {
            for (int y = 0; y < 4; ++y) {
                const Matrix3 m = BoardRotation{r, p, y}.matrix();
                const bool seen = std::ranges::any_of(unique, [&m](const Matrix3& known) {
                    return close(m, known);
                });
                if (!seen) unique.push_back(m);
            }
        }
    }
    return unique;
}

void SensorCalibration::rebuild() noexcept {
    combined_ = board_ * align_ * scale_;
}

void SensorCalibration::set_scale(const Matrix3& scale_ortho) noexcept {
    scale_ = scale_ortho;
    rebuild();
}

std::expected<void, MountingError> SensorCalibration::set_misalignment(
    const Vector3& small_angles_rad) noexcept {
    constexpr float kLimit = 0.175F;   // ~10°: далі малокутове наближення бреше помітно
    if (!small_angles_rad.finite() ||
        std::fabs(small_angles_rad.x) > kLimit ||
        std::fabs(small_angles_rad.y) > kLimit ||
        std::fabs(small_angles_rad.z) > kLimit) {
        return std::unexpected(MountingError::AngleTooLarge);
    }
    const float dphi = small_angles_rad.x;
    const float dtheta = small_angles_rad.y;
    const float dpsi = small_angles_rad.z;
    const Matrix3 approx{{{{1.0F, dpsi, -dtheta},
                           {-dpsi, 1.0F, dphi},
                           {dtheta, -dphi, 1.0F}}}};
    // Наближення не ортогональне точно — Грам-Шмідт повертає його на многовид поворотів.
    const auto clean = approx.orthonormalized();
    if (!clean) return std::unexpected(MountingError::Degenerate);
    align_ = *clean;
    rebuild();
    return {};
}

void SensorCalibration::set_board(const BoardRotation& rotation) noexcept {
    board_ = rotation.matrix();
    rebuild();
}

void SensorCalibration::set_bias_polynomial(std::span<const Vector3, 4> coefficients,
                                            float t_ref_c) noexcept {
    std::ranges::copy(coefficients, bias_.begin());
    t_ref_c_ = t_ref_c;
}

Vector3 SensorCalibration::bias_at(float temp_c) const noexcept {
    if (!std::isfinite(temp_c)) temp_c = t_ref_c_;
    // Поза калібрувальною смугою куб полінома вибухає — тому затискаємо аргумент.
    const float d = std::clamp(temp_c, -40.0F, 85.0F) - t_ref_c_;
    Vector3 b = bias_[3];
    for (int i = 2; i >= 0; --i) b = bias_[static_cast<std::size_t>(i)] + b * d;   // Горнер
    return b;
}

Vector3 SensorCalibration::apply(const Vector3& raw, float temp_c) const noexcept {
    if (!raw.finite()) return {};
    return combined_ * (raw - bias_at(temp_c));
}

float SensorCalibration::orthogonality_error() const noexcept {
    return std::max(align_.orthogonality_error(), board_.orthogonality_error());
}

bool SensorCalibration::sane() const noexcept {
    // Дзеркальна матриця (det < 0) перевернула б знак осі — це вже не поворот.
    if (align_.det() < 0.5F || board_.det() < 0.5F) return false;
    return orthogonality_error() < 1e-3F;
}

}  // namespace nav
