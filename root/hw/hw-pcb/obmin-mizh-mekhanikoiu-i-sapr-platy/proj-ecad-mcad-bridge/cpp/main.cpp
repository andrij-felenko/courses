#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <optional>
#include <iomanip>
#include <span>
#include <algorithm>
#include <format>

namespace ecad_mcad {

constexpr double kEpsilonClosure = 0.05;     // мм
constexpr double kEpsilonHolePos = 0.08;     // мм
constexpr double kEpsilonHoleDia = 0.05;     // мм

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr double distance_to(const Point2D& other) const noexcept {
        const double dx = other.x - x;
        const double dy = other.y - y;
        return std::sqrt(dx * dx + dy * dy);
    }
};

struct Point3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr Point2D to_2d() const noexcept {
        return Point2D{x, y};
    }
};

struct PolyVertex {
    Point2D pt;
    double bulge{0.0}; // tan(theta / 4)
};

struct MountingHole {
    Point2D center;
    double diameter{3.2};
    std::string label;
};

struct BoundingBox2D {
    double min_x{0.0};
    double min_y{0.0};
    double max_x{0.0};
    double max_y{0.0};

    [[nodiscard]] constexpr double width() const noexcept { return max_x - min_x; }
    [[nodiscard]] constexpr double height() const noexcept { return max_y - min_y; }
};

enum class Severity {
    Info,
    Warning,
    Error
};

struct ValidationIssue {
    Severity severity{Severity::Info};
    std::string message;
    double expected{0.0};
    double actual{0.0};
    double delta{0.0};
};

class CadBoard2D {
public:
    std::vector<PolyVertex> vertices;
    std::vector<MountingHole> holes;

    [[nodiscard]] BoundingBox2D compute_bbox() const noexcept {
        if (vertices.empty()) return {};
        BoundingBox2D box{vertices[0].pt.x, vertices[0].pt.y, vertices[0].pt.x, vertices[0].pt.y};
        for (const auto& v : vertices) {
            box.min_x = std::min(box.min_x, v.pt.x);
            box.max_x = std::max(box.max_x, v.pt.x);
            box.min_y = std::min(box.min_y, v.pt.y);
            box.max_y = std::max(box.max_y, v.pt.y);
        }
        return box;
    }

    [[nodiscard]] double compute_polygon_area() const noexcept {
        if (vertices.size() < 3) return 0.0;
        double area = 0.0;
        const size_t n = vertices.size();
        for (size_t i = 0; i < n; ++i) {
            const size_t next = (i + 1) % n;
            area += (vertices[i].pt.x * vertices[next].pt.y - vertices[next].pt.x * vertices[i].pt.y);
        }
        return area * 0.5;
    }
};

class StepBoard3D {
public:
    std::vector<Point3D> boundary_vertices;
    std::vector<MountingHole> holes;
    double substrate_thickness{1.6};

    [[nodiscard]] BoundingBox2D compute_bbox() const noexcept {
        if (boundary_vertices.empty()) return {};
        BoundingBox2D box{boundary_vertices[0].x, boundary_vertices[0].y,
                          boundary_vertices[0].x, boundary_vertices[0].y};
        for (const auto& v : boundary_vertices) {
            box.min_x = std::min(box.min_x, v.x);
            box.max_x = std::max(box.max_x, v.x);
            box.min_y = std::min(box.min_y, v.y);
            box.max_y = std::max(box.max_y, v.y);
        }
        return box;
    }
};

class GeometryValidator {
public:
    explicit GeometryValidator(CadBoard2D dxf, StepBoard3D step)
        : dxf_(std::move(dxf)), step_(std::move(step)) {}

    [[nodiscard]] std::vector<ValidationIssue> run_checks() {
        issues_.clear();
        passed_ = true;

        check_outline_closure();
        check_bounding_boxes();
        check_mounting_holes();

        return issues_;
    }

    [[nodiscard]] bool is_passed() const noexcept { return passed_; }

private:
    CadBoard2D dxf_;
    StepBoard3D step_;
    std::vector<ValidationIssue> issues_;
    bool passed_{true};

    void add_issue(Severity sev, std::string_view msg, double exp_v, double act_v) {
        const double diff = std::abs(act_v - exp_v);
        if (sev == Severity::Error) {
            passed_ = false;
        }
        issues_.emplace_back(ValidationIssue{
            .severity = sev,
            .message = std::string(msg),
            .expected = exp_v,
            .actual = act_v,
            .delta = diff
        });
    }

    void check_outline_closure() {
        if (dxf_.vertices.size() < 3) {
            add_issue(Severity::Error, "DXF Outline: недостатньо вершин для формування контуру (<3)", 3.0, static_cast<double>(dxf_.vertices.size()));
            return;
        }

        const Point2D& first = dxf_.vertices.front().pt;
        const Point2D& last = dxf_.vertices.back().pt;
        const double gap = first.distance_to(last);

        if (gap > kEpsilonClosure) {
            add_issue(Severity::Error, "DXF Outline: розімкнений контур плати (розрив периметра)", 0.0, gap);
        } else {
            add_issue(Severity::Info, "DXF Outline: нерозривність контуру підтверджена", 0.0, gap);
        }

        const double area = dxf_.compute_polygon_area();
        if (area <= 0.0) {
            add_issue(Severity::Warning, "DXF Outline: CW орієнтація замість CCW (можливий внутрішній виріз)", 1.0, area);
        }
    }

    void check_bounding_boxes() {
        const auto bbox_dxf = dxf_.compute_bbox();
        const auto bbox_step = step_.compute_bbox();

        if (std::abs(bbox_dxf.width() - bbox_step.width()) > kEpsilonClosure) {
            add_issue(Severity::Error, "BBox Width: розбіжність габаритної ширини X між DXF та STEP", bbox_dxf.width(), bbox_step.width());
        } else {
            add_issue(Severity::Info, "BBox Width: повний збіг ширини", bbox_dxf.width(), bbox_step.width());
        }

        if (std::abs(bbox_dxf.height() - bbox_step.height()) > kEpsilonClosure) {
            add_issue(Severity::Error, "BBox Height: розбіжність габаритної висоти Y між DXF та STEP", bbox_dxf.height(), bbox_step.height());
        } else {
            add_issue(Severity::Info, "BBox Height: повний збіг висоти", bbox_dxf.height(), bbox_step.height());
        }
    }

    void check_mounting_holes() {
        if (dxf_.holes.size() != step_.holes.size()) {
            add_issue(Severity::Error, "Holes Count: невідповідність кількості кріпильних отворів",
                      static_cast<double>(dxf_.holes.size()), static_cast<double>(step_.holes.size()));
        }

        for (const auto& dh : dxf_.holes) {
            bool found_coaxial = false;
            for (const auto& sh : step_.holes) {
                const double pos_delta = dh.center.distance_to(sh.center);
                if (pos_delta <= kEpsilonHolePos) {
                    found_coaxial = true;
                    const double dia_delta = std::abs(dh.diameter - sh.diameter);
                    if (dia_delta > kEpsilonHoleDia) {
                        add_issue(Severity::Warning,
                                  std::format("Hole {} ({}): відхилення діаметра", dh.label, sh.label),
                                  dh.diameter, sh.diameter);
                    } else {
                        add_issue(Severity::Info,
                                  std::format("Hole {}: співвісність та діаметр підтверджені", dh.label),
                                  0.0, pos_delta);
                    }
                    break;
                }
            }

            if (!found_coaxial) {
                add_issue(Severity::Error,
                          std::format("Hole {}: отвір із DXF не має аналога в 3D STEP", dh.label),
                          0.0, 1.0);
            }
        }
    }
};

void render_report(std::span<const ValidationIssue> issues, bool passed) {
    std::cout << "=================================================================\n";
    std::cout << "     ЗВІТ ВАЛІДАЦІЇ ГЕОМЕТРІЇ (C++20 ECAD-MCAD BRIDGE)           \n";
    std::cout << "=================================================================\n";
    for (const auto& issue : issues) {
        std::string_view tag = "[INFO]";
        if (issue.severity == Severity::Warning) tag = "[WARN]";
        if (issue.severity == Severity::Error)   tag = "[FAIL]";

        std::cout << std::format("{:<7} {:<55}\n", tag, issue.message);
        if (issue.severity != Severity::Info || issue.delta > 0.0001) {
            std::cout << std::format("        Очікувано: {:8.3f} мм | Фактично: {:8.3f} мм | Відхилення: {:8.3f} мм\n",
                                     issue.expected, issue.actual, issue.delta);
        }
    }
    std::cout << "-----------------------------------------------------------------\n";
    if (passed) {
        std::cout << "РЕЗУЛЬТАТ: УСПІХ — 2D контур повністю узгоджений із 3D моделлю STEP.\n";
    } else {
        std::cout << "РЕЗУЛЬТАТ: КРИТИЧНІ ПОМИЛКИ — виявлено геометричну несумісність!\n";
    }
    std::cout << "=================================================================\n";
}

} // namespace ecad_mcad

int main() {
    using namespace ecad_mcad;

    CadBoard2D dxf;
    dxf.vertices = {
        {{0.0, 0.0}, 0.0},
        {{100.0, 0.0}, 0.41421356},
        {{100.0, 60.0}, 0.0},
        {{0.0, 60.0}, 0.0},
        {{0.0, 0.0}, 0.0}
    };
    dxf.holes = {
        {{4.0, 4.0}, 3.2, "H1"},
        {{96.0, 4.0}, 3.2, "H2"},
        {{96.0, 56.0}, 3.2, "H3"},
        {{4.0, 56.0}, 3.2, "H4"}
    };

    StepBoard3D step;
    step.boundary_vertices = {
        {0.0, 0.0, 0.0},
        {100.0, 0.0, 0.0},
        {100.0, 60.0, 0.0},
        {0.0, 60.0, 0.0}
    };
    step.holes = {
        {{4.0, 4.0}, 3.2, "STEP_H1"},
        {{96.12, 4.0}, 3.2, "STEP_H2"}, // Зсув +0.12 мм
        {{96.0, 56.0}, 3.2, "STEP_H3"},
        {{4.0, 56.0}, 3.2, "STEP_H4"}
    };

    GeometryValidator validator(std::move(dxf), std::move(step));
    const auto issues = validator.run_checks();
    render_report(issues, validator.is_passed());

    return validator.is_passed() ? 0 : 1;
}
