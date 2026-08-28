#include <iostream>
#include <format>
#include <string_view>
#include <expected>
#include <cmath>

struct FootprintParams {
    double pitch_mm;           // Крок між сусідніми виводами
    double pad_width_mm;       // Ширина мідної площадки X
    double pad_length_mm;      // Довжина мідної площадки Y
    double mask_expansion_mm;  // Розширення вікна паяльної маски
    double min_mask_dam_mm;    // Мінімальний технологічний місток маски
};

enum class FootprintError {
    SolderBridgeRisk,
    InvalidDimensions
};

struct FootprintReport {
    double mask_dam_mm;
    bool nsmd_recommended;
};

class FootprintValidator {
public:
    static std::expected<FootprintReport, FootprintError> validate(const FootprintParams& p) noexcept {
        if (p.pitch_mm <= 0.0 || p.pad_width_mm <= 0.0 || p.pad_width_mm >= p.pitch_mm) {
            return std::unexpected(FootprintError::InvalidDimensions);
        }

        const double copper_gap = p.pitch_mm - p.pad_width_mm;
        const double dam = copper_gap - (2.0 * p.mask_expansion_mm);

        if (dam < p.min_mask_dam_mm) {
            return std::unexpected(FootprintError::SolderBridgeRisk);
        }

        return FootprintReport{
            .mask_dam_mm = dam,
            .nsmd_recommended = (p.pitch_mm <= 0.50)
        };
    }
};

int main() {
    constexpr FootprintParams qfn32{
        .pitch_mm = 0.50,
        .pad_width_mm = 0.28,
        .pad_length_mm = 0.85,
        .mask_expansion_mm = 0.04,
        .min_mask_dam_mm = 0.075
    };

    const auto result = FootprintValidator::validate(qfn32);

    if (result.has_value()) {
        std::cout << "Параметри посадкового місця валідні.\n";
        std::cout << "Місток маски: " << result->mask_dam_mm << " мм\n";
        std::cout << "Конфігурація: " << (result->nsmd_recommended ? "NSMD" : "SMD") << "\n";
    } else {
        std::cout << "Помилка валідації посадкового місця!\n";
    }

    return 0;
}
