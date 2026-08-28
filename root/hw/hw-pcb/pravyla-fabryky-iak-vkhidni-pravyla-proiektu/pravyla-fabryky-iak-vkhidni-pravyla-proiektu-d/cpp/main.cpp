#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <format>

namespace dfm {

/* Фізичні обмеження технологічного процесу виготовлення друкованої плати */
struct FactoryCapabilities {
    double min_trace_width{0.150};    // 6 mil (мм)
    double min_trace_space{0.150};    // 6 mil
    double min_drill_dia{0.300};      // 12 mil
    double min_annular_ring{0.150};   // 6 mil
    double min_mask_dam{0.100};       // 4 mil
    double mask_expansion{0.050};     // 2 mil
    double min_edge_milling{0.300};   // 12 mil
    double min_edge_vcut{0.500};      // 20 mil
};

/* Тип механічної обробки краю контуру */
enum class EdgeType {
    Milling,
    VScoring
};

/* Геометрія елемента топології плати */
struct BoardFeature {
    std::string_view net_name;
    double trace_width{0.200};
    double trace_space{0.200};
    double pad_dia{0.600};
    double drill_dia{0.300};
    double pad_to_pad_copper_space{0.300};
    double copper_to_edge_dist{0.400};
    EdgeType edge_type{EdgeType::Milling};
};

/* Структура звіту про порушення правила DFM */
struct DfmViolation {
    std::string_view rule_name;
    std::string message;
    double actual_value;
    double limit_value;
};

class DfmValidator {
public:
    explicit constexpr DfmValidator(FactoryCapabilities caps) noexcept
        : caps_(caps) {}

    [[nodiscard]] std::vector<DfmViolation> validate(const BoardFeature& feat) const {
        std::vector<DfmViolation> violations;

        // 1. Перевірка ширини провідника
        if (feat.trace_width < caps_.min_trace_width - 1e-5) {
            violations.push_back({
                "MinTraceWidth",
                std::format("Доріжка '{}': ширина {:.3f} мм менша за ліміт {:.3f} мм",
                            feat.net_name, feat.trace_width, caps_.min_trace_width),
                feat.trace_width,
                caps_.min_trace_width
            });
        }

        // 2. Перевірка зазору між провідниками
        if (feat.trace_space < caps_.min_trace_space - 1e-5) {
            violations.push_back({
                "MinTraceSpace",
                std::format("Доріжка '{}': зазор {:.3f} мм менший за ліміт {:.3f} мм",
                            feat.net_name, feat.trace_space, caps_.min_trace_space),
                feat.trace_space,
                caps_.min_trace_space
            });
        }

        // 3. Перевірка діаметра свердління
        if (feat.drill_dia < caps_.min_drill_dia - 1e-5) {
            violations.push_back({
                "MinDrillDia",
                std::format("Отвір у колі '{}': діаметр свердла {:.3f} мм менший за ліміт {:.3f} мм",
                            feat.net_name, feat.drill_dia, caps_.min_drill_dia),
                feat.drill_dia,
                caps_.min_drill_dia
            });
        }

        // 4. Перевірка пояска металізації (Annular Ring)
        const double annular_ring = (feat.pad_dia - feat.drill_dia) / 2.0;
        if (annular_ring < caps_.min_annular_ring - 1e-5) {
            violations.push_back({
                "MinAnnularRing",
                std::format("Поясок металізації {:.3f} мм менший за ліміт {:.3f} мм (Pad={:.3f}, Drill={:.3f})",
                            annular_ring, caps_.min_annular_ring, feat.pad_dia, feat.drill_dia),
                annular_ring,
                caps_.min_annular_ring
            });
        }

        // 5. Перевірка містка паяльної маски (Solder Mask Dam)
        const double mask_dam = feat.pad_to_pad_copper_space - 2.0 * caps_.mask_expansion;
        if (mask_dam < caps_.min_mask_dam - 1e-5) {
            violations.push_back({
                "MinMaskDam",
                std::format("Місток маски {:.3f} мм менший за ліміт {:.3f} мм (ризик відшарування)",
                            mask_dam, caps_.min_mask_dam),
                mask_dam,
                caps_.min_mask_dam
            });
        }

        // 6. Перевірка відступу до краю контуру плати
        const double required_edge = (feat.edge_type == EdgeType::VScoring)
                                     ? caps_.min_edge_vcut
                                     : caps_.min_edge_milling;
        if (feat.copper_to_edge_dist < required_edge - 1e-5) {
            violations.push_back({
                "MinEdgeClearance",
                std::format("Відступ до краю {:.3f} мм менший за ліміт {:.3f} мм для {}",
                            feat.copper_to_edge_dist, required_edge,
                            feat.edge_type == EdgeType::VScoring ? "V-cut" : "фрезерування"),
                feat.copper_to_edge_dist,
                required_edge
            });
        }

        return violations;
    }

private:
    FactoryCapabilities caps_;
};

} // namespace dfm

int main() {
    using namespace dfm;

    constexpr FactoryCapabilities jlc_std{
        .min_trace_width = 0.150,
        .min_trace_space = 0.150,
        .min_drill_dia   = 0.300,
        .min_annular_ring= 0.150,
        .min_mask_dam    = 0.100,
        .mask_expansion  = 0.050,
        .min_edge_milling= 0.300,
        .min_edge_vcut   = 0.500
    };

    const DfmValidator validator(jlc_std);

    const BoardFeature test_feature{
        .net_name = "SPI_SCK",
        .trace_width = 0.180,
        .trace_space = 0.160,
        .pad_dia     = 0.500,        // Поясок = (0.5 - 0.3)/2 = 0.10 мм (< 0.15 мм)
        .drill_dia   = 0.300,
        .pad_to_pad_copper_space = 0.250,
        .copper_to_edge_dist = 0.350, // Для V-cut ліміт 0.50 мм
        .edge_type   = EdgeType::VScoring
    };

    std::cout << "=== DFM-аналіз топології плати (C++20) ===\n";
    const auto violations = validator.validate(test_feature);

    if (violations.empty()) {
        std::cout << "Топологія повністю відповідає технологічному стандарту фабрики.\n";
        return 0;
    }

    std::cout << std::format("Виявлено {} порушень технологічних правил:\n", violations.size());
    for (const auto& [rule, msg, val, lim] : violations) {
        std::cout << std::format("  • [{}] {}\n", rule, msg);
    }

    return 1;
}
