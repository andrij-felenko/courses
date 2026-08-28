/*
 * dfm_audit_core.cpp — Базовий модуль верифікації топологічних норм DFM (C++20).
 * Застосовує структуровані типи, std::expected та розширені звіти.
 */

#include <iostream>
#include <string_view>
#include <vector>
#include <expected>
#include <cstdint>

enum class DfmViolation : uint8_t {
    AnnularBreakout,
    AnnularTangency,
    CopperToEdgeTooClose
};

struct DfmRules {
    double min_annular_ring_mm{0.05};
    double min_copper_to_edge_mm{0.30};
    double drill_tool_oversize_mm{0.10};
};

struct ViaMetric {
    double pad_diameter_mm;
    double finished_hole_mm;
    double drill_misregistration_mm;
    double distance_to_outline_mm;
};

class DfmAuditor {
public:
    explicit DfmAuditor(DfmRules rules) : rules_(rules) {}

    [[nodiscard]] std::expected<void, std::vector<DfmViolation>> audit_via(const ViaMetric& via) const {
        std::vector<DfmViolation> violations;

        const double actual_drill_tool = via.finished_hole_mm + rules_.drill_tool_oversize_mm;
        const double nominal_ar = (via.pad_diameter_mm - actual_drill_tool) / 2.0;
        const double worst_case_ar = nominal_ar - via.drill_misregistration_mm;

        if (worst_case_ar < 0.0) {
            violations.push_back(DfmViolation::AnnularBreakout);
        } else if (worst_case_ar < rules_.min_annular_ring_mm) {
            violations.push_back(DfmViolation::AnnularTangency);
        }

        if (via.distance_to_outline_mm < rules_.min_copper_to_edge_mm) {
            violations.push_back(DfmViolation::CopperToEdgeTooClose);
        }

        if (violations.empty()) {
            return {};
        }
        return std::unexpected(std::move(violations));
    }

private:
    DfmRules rules_;
};

int main() {
    DfmRules rules{
        .min_annular_ring_mm = 0.05,
        .min_copper_to_edge_mm = 0.30,
        .drill_tool_oversize_mm = 0.10
    };

    DfmAuditor auditor(rules);

    ViaMetric via{
        .pad_diameter_mm = 0.50,
        .finished_hole_mm = 0.30,
        .drill_misregistration_mm = 0.04,
        .distance_to_outline_mm = 0.22
    };

    auto result = auditor.audit_via(via);

    if (!result.has_value()) {
        std::cout << "Виявлено порушення виробничих норм DFM:\n";
        for (const auto& violation : result.error()) {
            switch (violation) {
                case DfmViolation::AnnularBreakout:
                    std::cout << " - [CRITICAL] Прорив пояска металізації перехідного отвору\n";
                    break;
                case DfmViolation::AnnularTangency:
                    std::cout << " - [WARNING] Поясок менший за 0.05 мм (IPC Class 3 violation)\n";
                    break;
                case DfmViolation::CopperToEdgeTooClose:
                    std::cout << " - [CRITICAL] Зазор міді до контуру плати менший за 0.30 мм\n";
                    break;
            }
        }
    } else {
        std::cout << "Параметри переходу задовольняють вимогам фабрики.\n";
    }

    return 0;
}
