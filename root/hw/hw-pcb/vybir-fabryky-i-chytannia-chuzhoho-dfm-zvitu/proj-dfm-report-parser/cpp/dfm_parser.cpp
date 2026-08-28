/*
 * dfm_parser.cpp — Об'єктно-орієнтований рушій DFM-аудиту друкованих плат (C++20).
 */

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <cmath>
#include <numbers>
#include <expected>
#include <iomanip>
#include <algorithm>

namespace dfm {

enum class Severity : uint8_t {
    Info,
    Warning,
    Critical
};

enum class DefectCategory : uint8_t {
    AcidTrap,
    MaskSliver,
    AnnularBreakout,
    AnnularTangency,
    CopperToEdge
};

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] double distance_to(const Point2D& other) const noexcept {
        return std::hypot(x - other.x, y - other.y);
    }
};

struct TraceSegment {
    Point2D start;
    Point2D end;
    double width_mm{0.15};
    std::string net_name;
};

struct ViaElement {
    Point2D center;
    double pad_diameter_mm{0.60};
    double finished_hole_mm{0.30};
    std::string net_name;
};

struct OutlineSegment {
    Point2D p1;
    Point2D p2;
};

struct AuditRules {
    double min_trace_width_mm{0.10};
    double min_trace_clearance_mm{0.10};
    double min_mask_sliver_mm{0.09};
    double min_annular_ring_mm{0.05};
    double min_copper_to_edge_mm{0.30};
    double max_acute_angle_deg{85.0};
    double drill_runout_tolerance_mm{0.04};
    double drill_plating_allowance_mm{0.10};
};

struct DefectRecord {
    DefectCategory category;
    Severity severity;
    Point2D position;
    std::string description;
    std::string recommendation;
};

class DfmEngine {
public:
    explicit DfmEngine(AuditRules rules) : rules_(std::move(rules)) {}

    [[nodiscard]] std::vector<DefectRecord> execute_audit(
        std::span<const TraceSegment> traces,
        std::span<const ViaElement> vias,
        std::span<const OutlineSegment> outline) const
    {
        std::vector<DefectRecord> report;
        inspect_acid_traps(traces, report);
        inspect_annular_rings(vias, report);
        inspect_copper_to_edge(vias, outline, report);
        return report;
    }

private:
    AuditRules rules_;

    static double vector_angle_deg(Point2D v1, Point2D v2) noexcept {
        const double l1 = std::hypot(v1.x, v1.y);
        const double l2 = std::hypot(v2.x, v2.y);
        if (l1 < 1e-6 || l2 < 1e-6) return 180.0;

        const double dot = v1.x * v2.x + v1.y * v2.y;
        const double cos_val = std::clamp(dot / (l1 * l2), -1.0, 1.0);
        return std::acos(cos_val) * (180.0 / std::numbers::pi);
    }

    static double distance_to_segment(Point2D pt, const OutlineSegment& seg) noexcept {
        const double dx = seg.p2.x - seg.p1.x;
        const double dy = seg.p2.y - seg.p1.y;
        const double len_sq = dx * dx + dy * dy;

        if (len_sq < 1e-9) {
            return pt.distance_to(seg.p1);
        }

        const double t = std::clamp(
            ((pt.x - seg.p1.x) * dx + (pt.y - seg.p1.y) * dy) / len_sq,
            0.0, 1.0
        );

        const Point2D nearest_point{seg.p1.x + t * dx, seg.p1.y + t * dy};
        return pt.distance_to(nearest_point);
    }

    void inspect_acid_traps(std::span<const TraceSegment> traces, std::vector<DefectRecord>& report) const {
        for (size_t i = 0; i < traces.size(); ++i) {
            for (size_t j = i + 1; j < traces.size(); ++j) {
                bool is_joined = false;
                Point2D vertex{};
                Point2D v1{}, v2{};

                if (traces[i].start.distance_to(traces[j].start) < 1e-4) {
                    is_joined = true;
                    vertex = traces[i].start;
                    v1 = {traces[i].end.x - vertex.x, traces[i].end.y - vertex.y};
                    v2 = {traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
                } else if (traces[i].end.distance_to(traces[j].start) < 1e-4) {
                    is_joined = true;
                    vertex = traces[i].end;
                    v1 = {traces[i].start.x - vertex.x, traces[i].start.y - vertex.y};
                    v2 = {traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
                } else if (traces[i].end.distance_to(traces[j].end) < 1e-4) {
                    is_joined = true;
                    vertex = traces[i].end;
                    v1 = {traces[i].start.x - vertex.x, traces[i].start.y - vertex.y};
                    v2 = {traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
                }

                if (is_joined) {
                    const double angle = vector_angle_deg(v1, v2);
                    if (angle < rules_.max_acute_angle_deg) {
                        report.push_back(DefectRecord{
                            .category = DefectCategory::AcidTrap,
                            .severity = Severity::Warning,
                            .position = vertex,
                            .description = "Гострий кут сходження доріжок " + std::to_string(angle) +
                                           " deg у колі " + traces[i].net_name,
                            .recommendation = "Застосуйте поворот на 45 deg або додайте скруглення"
                        });
                    }
                }
            }
        }
    }

    void inspect_annular_rings(std::span<const ViaElement> vias, std::vector<DefectRecord>& report) const {
        for (const auto& via : vias) {
            const double tool_size = via.finished_hole_mm + rules_.drill_plating_allowance_mm;
            const double nominal_ar = (via.pad_diameter_mm - tool_size) / 2.0;
            const double worst_case_ar = nominal_ar - rules_.drill_runout_tolerance_mm;

            if (worst_case_ar < 0.0) {
                report.push_back(DefectRecord{
                    .category = DefectCategory::AnnularBreakout,
                    .severity = Severity::Critical,
                    .position = via.center,
                    .description = "Критичний зрив пояска (Breakout) переходу " + via.net_name +
                                   ": дефіцит " + std::to_string(-worst_case_ar) + " мм",
                    .recommendation = "Збільште розмір контактного майданчика або додайте Teardrop"
                });
            } else if (worst_case_ar < rules_.min_annular_ring_mm) {
                report.push_back(DefectRecord{
                    .category = DefectCategory::AnnularTangency,
                    .severity = Severity::Warning,
                    .position = via.center,
                    .description = "Поясок переходу " + via.net_name +
                                   " менший за норму IPC Class 3 (" + std::to_string(worst_case_ar) + " мм)",
                    .recommendation = "Збільште діаметр майданчика на 0.05 мм"
                });
            }
        }
    }

    void inspect_copper_to_edge(
        std::span<const ViaElement> vias,
        std::span<const OutlineSegment> outline,
        std::vector<DefectRecord>& report) const
    {
        for (const auto& via : vias) {
            double min_edge_dist = 1e9;
            for (const auto& seg : outline) {
                min_edge_dist = std::min(min_edge_dist, distance_to_segment(via.center, seg));
            }

            const double net_clearance = min_edge_dist - (via.pad_diameter_mm / 2.0);
            if (net_clearance < rules_.min_copper_to_edge_mm) {
                report.push_back(DefectRecord{
                    .category = DefectCategory::CopperToEdge,
                    .severity = Severity::Critical,
                    .position = via.center,
                    .description = "Неприпустимо малий відступ міді до контуру плати: " +
                                   std::to_string(net_clearance) + " мм",
                    .recommendation = "Зсуньте елемент усередину плати на безпечну відстань >= 0.30 мм"
                });
            }
        }
    }
};

} // namespace dfm

int main() {
    dfm::AuditRules rules{
        .min_trace_width_mm = 0.10,
        .min_trace_clearance_mm = 0.10,
        .min_mask_sliver_mm = 0.09,
        .min_annular_ring_mm = 0.05,
        .min_copper_to_edge_mm = 0.30,
        .max_acute_angle_deg = 85.0,
        .drill_runout_tolerance_mm = 0.04,
        .drill_plating_allowance_mm = 0.10
    };

    dfm::DfmEngine auditor(rules);

    std::vector<dfm::TraceSegment> traces{
        {{12.0, 15.0}, {25.0, 25.0}, 0.15, "NET_SPI_MOSI"},
        {{25.0, 25.0}, {28.0, 16.0}, 0.15, "NET_SPI_MOSI"}
    };

    std::vector<dfm::ViaElement> vias{
        {{30.0, 40.0}, 0.45, 0.30, "NET_VDD_IO"},
        {{49.85, 25.0}, 0.50, 0.30, "NET_GND"}
    };

    std::vector<dfm::OutlineSegment> outline{
        {{0.0, 0.0}, {50.0, 0.0}},
        {{50.0, 0.0}, {50.0, 50.0}},
        {{50.0, 50.0}, {0.0, 50.0}},
        {{0.0, 50.0}, {0.0, 0.0}}
    };

    const auto findings = auditor.execute_audit(traces, vias, outline);

    std::cout << "=================================================================\n";
    std::cout << "             ЗВІТ АУДИТУ DFM (C++20 ENGINE)                      \n";
    std::cout << "=================================================================\n";

    for (size_t idx = 0; idx < findings.size(); ++idx) {
        const auto& item = findings[idx];
        std::string_view tag = (item.severity == dfm::Severity::Critical) ? "CRITICAL" : "WARNING";
        std::cout << "[" << tag << "] Порушення #" << (idx + 1)
                  << " у координаті (X: " << std::fixed << std::setprecision(2)
                  << item.position.x << ", Y: " << item.position.y << ")\n";
        std::cout << "  Опис: " << item.description << "\n";
        std::cout << "  Дія:  " << item.recommendation << "\n\n";
    }

    std::cout << "=================================================================\n";
    return 0;
}
