#include <iostream>
#include <array>
#include <cmath>
#include <expected>
#include <string_view>

namespace pcb::vision {

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct AffineTransform {
    double a{1.0}, b{0.0}, x_offset{0.0};
    double c{0.0}, d{1.0}, y_offset{0.0};

    [[nodiscard]] constexpr Point2D Apply(Point2D cad_pt) const noexcept {
        return {
            a * cad_pt.x + b * cad_pt.y + x_offset,
            c * cad_pt.x + d * cad_pt.y + y_offset
        };
    }
};

class FiducialAlignment {
public:
    [[nodiscard]] static std::expected<AffineTransform, std::string_view> ComputeTransform(
        const std::array<Point2D, 3>& cad,
        const std::array<Point2D, 3>& real) noexcept
    {
        double det = cad[0].x * (cad[1].y - cad[2].y) +
                     cad[1].x * (cad[2].y - cad[0].y) +
                     cad[2].x * (cad[0].y - cad[1].y);

        if (std::abs(det) < 1.0e-9) {
            return std::unexpected("Вироджена конфігурація: реперні мітки лежать на одній прямій");
        }

        double inv_det = 1.0 / det;
        AffineTransform tf;

        tf.a = (real[0].x * (cad[1].y - cad[2].y) +
                real[1].x * (cad[2].y - cad[0].y) +
                real[2].x * (cad[0].y - cad[1].y)) * inv_det;

        tf.b = (real[0].x * (cad[2].x - cad[1].x) +
                real[1].x * (cad[0].x - cad[2].x) +
                real[2].x * (cad[1].x - cad[0].x)) * inv_det;

        tf.x_offset = (real[0].x * (cad[1].x * cad[2].y - cad[2].x * cad[1].y) +
                       real[1].x * (cad[2].x * cad[0].y - cad[0].x * cad[2].y) +
                       real[2].x * (cad[0].x * cad[1].y - cad[1].x * cad[0].y)) * inv_det;

        tf.c = (real[0].y * (cad[1].y - cad[2].y) +
                real[1].y * (cad[2].y - cad[0].y) +
                real[2].y * (cad[0].y - cad[1].y)) * inv_det;

        tf.d = (real[0].y * (cad[2].x - cad[1].x) +
                real[1].y * (cad[0].x - cad[2].x) +
                real[2].y * (cad[1].x - cad[0].x)) * inv_det;

        tf.y_offset = (real[0].y * (cad[1].x * cad[2].y - cad[2].x * cad[1].y) +
                       real[1].y * (cad[2].x * cad[0].y - cad[0].x * cad[2].y) +
                       real[2].y * (cad[0].x * cad[1].y - cad[1].x * cad[0].y)) * inv_det;

        return tf;
    }
};

} // namespace pcb::vision
