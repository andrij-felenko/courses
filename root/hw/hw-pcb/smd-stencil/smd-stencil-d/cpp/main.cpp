#include <iostream>
#include <iomanip>
#include <cmath>
#include <algorithm>
#include <string_view>

enum class ApertureShape {
    Rectangle,
    Circle
};

struct StencilAperture {
    ApertureShape shape{ApertureShape::Rectangle};
    double width_mm{0.0};
    double length_mm{0.0};
    double foil_thick_mm{0.12};
    bool has_nano_coating{false};
};

struct ValidationResult {
    double area_ratio{0.0};
    double aspect_ratio{0.0};
    double expected_transfer_eff{0.0};
    bool is_ipc_ar_valid{false};
    bool is_ipc_as_valid{false};

    [[nodiscard]] constexpr double ar_threshold(bool nano) const noexcept {
        return nano ? 0.55 : 0.66;
    }
};

class StencilValidator {
public:
    [[nodiscard]] static ValidationResult evaluate(const StencilAperture& ap) noexcept {
        ValidationResult res;
        const double w = ap.width_mm;
        const double l = ap.length_mm;
        const double t = ap.foil_thick_mm;

        if (ap.shape == ApertureShape::Circle) {
            res.area_ratio = w / (4.0 * t);
            res.aspect_ratio = w / t;
        } else {
            const double a_pad = w * l;
            const double a_walls = 2.0 * (w + l) * t;
            res.area_ratio = a_pad / a_walls;
            res.aspect_ratio = std::min(w, l) / t;
        }

        const double ar_limit = res.ar_threshold(ap.has_nano_coating);
        res.is_ipc_ar_valid = (res.area_ratio >= ar_limit);
        res.is_ipc_as_valid = (res.aspect_ratio >= 1.50);

        const double k = ap.has_nano_coating ? 14.0 : 11.0;
        const double ar0 = ap.has_nano_coating ? 0.45 : 0.55;
        res.expected_transfer_eff = 0.95 / (1.0 + std::exp(-k * (res.area_ratio - ar0)));

        return res;
    }
};

int main() {
    constexpr StencilAperture qfn_lead{
        .shape = ApertureShape::Rectangle,
        .width_mm = 0.20,
        .length_mm = 0.80,
        .foil_thick_mm = 0.12,
        .has_nano_coating = true
    };

    const auto r = StencilValidator::evaluate(qfn_lead);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Аналіз апертури QFN 0.4mm (Фольга 120 мкм, Нанопокриття):\n";
    std::cout << "  Area Ratio:   " << r.area_ratio << " (Норма >= " 
              << r.ar_threshold(qfn_lead.has_nano_coating) << ") -> "
              << (r.is_ipc_ar_valid ? "PASS" : "FAIL") << "\n";
    std::cout << "  Aspect Ratio: " << r.aspect_ratio << " (Норма >= 1.500) -> "
              << (r.is_ipc_as_valid ? "PASS" : "FAIL") << "\n";
    std::cout << "  Очікуваний Transfer Efficiency: " 
              << std::setprecision(1) << (r.expected_transfer_eff * 100.0) << "%\n";

    return 0;
}
