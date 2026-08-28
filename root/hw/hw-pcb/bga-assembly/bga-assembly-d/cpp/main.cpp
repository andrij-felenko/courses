#include <iostream>
#include <iomanip>
#include <numbers>
#include <cmath>
#include <expected>
#include <string_view>

struct BgaGeometryConfig {
    double pitch_mm{0.80};           // Крок кульок
    double ball_diam_mm{0.45};       // Діаметр кульки
    double pad_diam_mm{0.38};        // Діаметр площадки
    double mask_clearance_mm{0.05};  // Зазор маски
    bool   is_nsmd{true};            // Тип площадки NSMD vs SMD
    double trace_width_mm{0.10};     // Ширина доріжки
    double trace_clearance_mm{0.10}; // Зазор доріжки
};

struct BgaVerificationReport {
    double escape_channel_mm{0.0};
    int    max_traces_in_ch{0};
    double area_ratio{0.0};
    double estimated_standoff_mm{0.0};
};

enum class LayoutError {
    ChannelTooNarrow,
    ApertureRatioViolated,
    InsufficientStandoff
};

class BgaValidator {
public:
    [[nodiscard]] static constexpr std::expected<BgaVerificationReport, LayoutError>
    validate(const BgaGeometryConfig& cfg, double stencil_thick_mm) noexcept {
        BgaVerificationReport rep{};
        
        if (cfg.is_nsmd) {
            rep.escape_channel_mm = cfg.pitch_mm - cfg.pad_diam_mm;
        } else {
            const double copper_pad = cfg.pad_diam_mm + 2.0 * cfg.mask_clearance_mm;
            rep.escape_channel_mm = cfg.pitch_mm - copper_pad;
        }
        
        if (rep.escape_channel_mm < 0.10) {
            return std::unexpected(LayoutError::ChannelTooNarrow);
        }
        
        const double needed = cfg.trace_width_mm + cfg.trace_clearance_mm;
        if (rep.escape_channel_mm > cfg.trace_clearance_mm) {
            rep.max_traces_in_ch = static_cast<int>(
                (rep.escape_channel_mm - cfg.trace_clearance_mm) / needed
            );
        }
        
        rep.area_ratio = cfg.pad_diam_mm / (4.0 * stencil_thick_mm);
        if (rep.area_ratio < 0.66) {
            return std::unexpected(LayoutError::ApertureRatioViolated);
        }
        
        const double ratio = cfg.pad_diam_mm / cfg.ball_diam_mm;
        rep.estimated_standoff_mm = cfg.ball_diam_mm * (1.0 - 0.25 * (ratio * ratio));
        if (rep.estimated_standoff_mm < 0.15) {
            return std::unexpected(LayoutError::InsufficientStandoff);
        }
        
        return rep;
    }
};

int main() {
    constexpr BgaGeometryConfig config{
        .pitch_mm = 0.80,
        .ball_diam_mm = 0.45,
        .pad_diam_mm = 0.38,
        .mask_clearance_mm = 0.05,
        .is_nsmd = true,
        .trace_width_mm = 0.10,
        .trace_clearance_mm = 0.10
    };
    
    constexpr double stencil_thickness = 0.12;
    const auto result = BgaValidator::validate(config, stencil_thickness);
    
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== C++20 BGA DFM Verification Engine ===\n";
    
    if (result.has_value()) {
        const auto& rep = result.value();
        std::cout << "Ширина каналу трасування: " << rep.escape_channel_mm << " мм\n";
        std::cout << "Доріжок у каналі:         " << rep.max_traces_in_ch << "\n";
        std::cout << "Area Ratio апертури:      " << rep.area_ratio << " (>= 0.66 OK)\n";
        std::cout << "Висота зазору Standoff:   " << rep.estimated_standoff_mm << " мм\n";
        std::cout << "Результат валідації:      УСПІШНО (DFM Passed)\n";
    } else {
        std::cout << "Помилка валідації топології BGA!\n";
    }
    
    return 0;
}
