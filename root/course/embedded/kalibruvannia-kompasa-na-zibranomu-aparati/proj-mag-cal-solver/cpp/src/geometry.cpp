// ===========================================================================
//  geometry.cpp — власні числа симетричної 3×3 та зумовленість
// ===========================================================================

#include "mag_cal/geometry.hpp"

#include <algorithm>
#include <functional>

namespace mag_cal {

std::array<float, 3> Mat3::symmetric_eigenvalues() const noexcept {
    const float a01 = rows_[0][1];
    const float a02 = rows_[0][2];
    const float a12 = rows_[1][2];
    const float off_sq = a01 * a01 + a02 * a02 + a12 * a12;

    if (off_sq < 1e-12F) {
        // Матриця вже діагональна — власні числа стоять на діагоналі
        std::array<float, 3> diag{rows_[0][0], rows_[1][1], rows_[2][2]};
        std::ranges::sort(diag, std::ranges::greater{});
        return diag;
    }

    // Замкнена формула О. Сміта (1961): три косинуси замість ітерацій QR
    const float q = (rows_[0][0] + rows_[1][1] + rows_[2][2]) / 3.0F;
    const float e0 = rows_[0][0] - q;
    const float e1 = rows_[1][1] - q;
    const float e2 = rows_[2][2] - q;
    const float p = std::sqrt((e0 * e0 + e1 * e1 + e2 * e2 + 2.0F * off_sq) / 6.0F);

    const float inv_p = 1.0F / p;
    Rows scaled{};
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 0; j < 3; ++j) {
            scaled[i][j] = inv_p * (rows_[i][j] - (i == j ? q : 0.0F));
        }
    }

    const float r = std::clamp(Mat3{scaled}.determinant() * 0.5F, -1.0F, 1.0F);
    const float phi = std::acos(r) / 3.0F;

    const float eig_max = q + 2.0F * p * std::cos(phi);
    const float eig_min = q + 2.0F * p * std::cos(phi + 2.09439510F);  // +2π/3
    return {eig_max, 3.0F * q - eig_max - eig_min, eig_min};           // слід сталий
}

float Mat3::condition_number() const noexcept {
    if (!all_finite()) {
        return 1.0e6F;
    }
    const auto eig = symmetric_eigenvalues();

    float max_abs = 0.0F;
    float min_abs = std::abs(eig[0]);
    for (const float value : eig) {
        max_abs = std::max(max_abs, std::abs(value));
        min_abs = std::min(min_abs, std::abs(value));
    }

    if (min_abs < 1e-6F) {
        return 1.0e6F;   // вироджена: скінченне велике число замість нескінченності
    }
    return max_abs / min_abs;
}

bool Mat3::all_finite() const noexcept {
    for (const auto& row : rows_) {
        for (const float value : row) {
            if (!std::isfinite(value)) {
                return false;
            }
        }
    }
    return true;
}

}  // namespace mag_cal
