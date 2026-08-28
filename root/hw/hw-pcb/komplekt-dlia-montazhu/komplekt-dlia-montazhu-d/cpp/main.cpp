#include <concepts>
#include <cstdint>

enum class SolderPowderType : uint8_t {
    Type3 = 3,
    Type4 = 4,
    Type5 = 5,
    Type6 = 6
};

struct StencilSpec {
    double foil_thickness_um{120.0};
    SolderPowderType powder{SolderPowderType::Type4};
};

struct StencilCheckResult {
    double aspect_ratio{0.0};
    double area_ratio{0.0};
    bool is_aspect_valid{false};
    bool is_area_valid{false};
    bool is_powder_valid{false};
    bool overall_pass{false};
};

class StencilValidator {
public:
    [[nodiscard]] static constexpr double max_powder_diameter_um(SolderPowderType type) noexcept {
        switch (type) {
            case SolderPowderType::Type3: return 45.0;
            case SolderPowderType::Type4: return 38.0;
            case SolderPowderType::Type5: return 25.0;
            case SolderPowderType::Type6: return 15.0;
        }
        return 45.0;
    }

    [[nodiscard]] static constexpr StencilCheckResult check_rect_aperture(
        const StencilSpec& spec,
        double width_um,
        double length_um) noexcept {
        const double t = spec.foil_thickness_um;
        const double d_max = max_powder_diameter_um(spec.powder);

        const double ar_aspect = width_um / t;
        const double ar_area = (width_um * length_um) / (2.0 * (width_um + length_um) * t);

        const bool aspect_ok = (ar_aspect >= 1.50);
        const bool area_ok = (ar_area >= 0.66);
        const bool powder_ok = (width_um >= 5.0 * d_max);

        return StencilCheckResult{
            .aspect_ratio = ar_aspect,
            .area_ratio = ar_area,
            .is_aspect_valid = aspect_ok,
            .is_area_valid = area_ok,
            .is_powder_valid = powder_ok,
            .overall_pass = (aspect_ok && area_ok && powder_ok)
        };
    }

    [[nodiscard]] static constexpr StencilCheckResult check_circle_aperture(
        const StencilSpec& spec,
        double diameter_um) noexcept {
        const double t = spec.foil_thickness_um;
        const double d_max = max_powder_diameter_um(spec.powder);

        const double ar_aspect = diameter_um / t;
        const double ar_area = diameter_um / (4.0 * t);

        const bool aspect_ok = (ar_aspect >= 1.50);
        const bool area_ok = (ar_area >= 0.66);
        const bool powder_ok = (diameter_um >= 5.0 * d_max);

        return StencilCheckResult{
            .aspect_ratio = ar_aspect,
            .area_ratio = ar_area,
            .is_aspect_valid = aspect_ok,
            .is_area_valid = area_ok,
            .is_powder_valid = powder_ok,
            .overall_pass = (aspect_ok && area_ok && powder_ok)
        };
    }
};
