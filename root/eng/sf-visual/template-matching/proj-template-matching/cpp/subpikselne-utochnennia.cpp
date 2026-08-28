#include <cmath>
#include <utility>
#include <algorithm>

struct SubpixelOffset {
    float dx{0.0f};
    float dy{0.0f};
};

[[nodiscard]] SubpixelOffset refine_subpixel(double r_c, double r_left, double r_right,
                                            double r_top, double r_bottom) noexcept {
    SubpixelOffset off;
    const double denom_x = 2.0 * (2.0 * r_c - r_left - r_right);
    if (std::abs(denom_x) > 1e-7) {
        off.dx = std::clamp(static_cast<float>((r_right - r_left) / denom_x), -1.0f, 1.0f);
    }

    const double denom_y = 2.0 * (2.0 * r_c - r_top - r_bottom);
    if (std::abs(denom_y) > 1e-7) {
        off.dy = std::clamp(static_cast<float>((r_bottom - r_top) / denom_y), -1.0f, 1.0f);
    }

    return off;
}
