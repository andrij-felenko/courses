// keepout_validator.cpp — Об'єктно-орієнтований валідатор правил топології на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numbers>
#include <span>
#include <format>
#include <algorithm>

enum class KeepoutFlag : uint32_t {
    None         = 0,
    Component    = 1U << 0,
    Route        = 1U << 1,
    Copper       = 1U << 2,
    Via          = 1U << 3,
    SmtRail      = 1U << 4
};

constexpr KeepoutFlag operator|(KeepoutFlag a, KeepoutFlag b) noexcept {
    return static_cast<KeepoutFlag>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr bool has_flag(KeepoutFlag mask, KeepoutFlag flag) noexcept {
    return (static_cast<uint32_t>(mask) & static_cast<uint32_t>(flag)) != 0;
}

struct Vec2 {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vec2 operator+(Vec2 o) const noexcept { return {x + o.x, y + o.y}; }
    [[nodiscard]] constexpr Vec2 operator-(Vec2 o) const noexcept { return {x - o.x, y - o.y}; }
    [[nodiscard]] constexpr double dot(Vec2 o) const noexcept { return x * o.x + y * o.y; }
    [[nodiscard]] constexpr double dist_sq(Vec2 o) const noexcept { return (x - o.x)*(x - o.x) + (y - o.y)*(y - o.y); }
    [[nodiscard]] double dist(Vec2 o) const noexcept { return std::sqrt(dist_sq(o)); }
};

struct Polygon {
    std::vector<Vec2> vertices;

    [[nodiscard]] bool contains(Vec2 p) const noexcept {
        if (vertices.size() < 3) return false;
        bool inside = false;
        for (size_t i = 0, j = vertices.size() - 1; i < vertices.size(); j = i++) {
            if (((vertices[i].y > p.y) != (vertices[j].y > p.y)) &&
                (p.x < (vertices[j].x - vertices[i].x) * (p.y - vertices[i].y) /
                 (vertices[j].y - vertices[i].y) + vertices[i].x)) {
                inside = !inside;
            }
        }
        return inside;
    }
};

struct KeepoutZone {
    std::string name;
    Polygon poly;
    Vec2 circle_center{0.0, 0.0};
    double circle_radius{0.0};
    bool is_circular{false};
    KeepoutFlag flags{KeepoutFlag::None};
    int layer{-1}; // -1 = All layers
};

struct Component {
    std::string refdes;
    Vec2 center;
    double width;
    double height;
    double rotation_deg;
    int layer{0};
    bool is_mlcc{false};

    [[nodiscard]] std::vector<Vec2> get_obb_vertices() const {
        const double rad = rotation_deg * (std::numbers::pi / 180.0);
        const double cos_a = std::cos(rad);
        const double sin_a = std::sin(rad);
        const double hw = width / 2.0;
        const double hh = height / 2.0;

        const double dx[4] = {-hw,  hw,  hw, -hw};
        const double dy[4] = {-hh, -hh,  hh,  hh};

        std::vector<Vec2> pts(4);
        for (int i = 0; i < 4; ++i) {
            pts[i] = {
                center.x + dx[i] * cos_a - dy[i] * sin_a,
                center.y + dx[i] * sin_a + dy[i] * cos_a
            };
        }
        return pts;
    }
};

struct TraceSegment {
    std::string net_name;
    Vec2 start;
    Vec2 end;
    double width{0.2};
    int layer{0};
};

struct Violation {
    std::string object_id;
    std::string rule_name;
    std::string description;
    double distance{0.0};
};

[[nodiscard]] double dist_point_to_segment(Vec2 c, Vec2 a, Vec2 b) noexcept {
    const double l2 = a.dist_sq(b);
    if (l2 < 1e-9) return c.dist(a);
    double t = (c - a).dot(b - a) / l2;
    t = std::clamp(t, 0.0, 1.0);
    const Vec2 projection = {a.x + t * (b.x - a.x), a.y + t * (b.y - a.y)};
    return c.dist(projection);
}

class LayoutValidator {
public:
    explicit LayoutValidator(Polygon board_outline)
        : m_outline(std::move(board_outline)) {}

    void add_keepout(KeepoutZone kz) {
        m_keepouts.push_back(std::move(kz));
    }

    void validate(const Component& cmp) {
        const auto obb = cmp.get_obb_vertices();

        for (const auto& kz : m_keepouts) {
            if (!has_flag(kz.flags, KeepoutFlag::Component)) continue;
            if (kz.layer != -1 && kz.layer != cmp.layer) continue;

            if (kz.is_circular) {
                for (const auto& pt : obb) {
                    if (const double d = pt.dist(kz.circle_center); d < kz.circle_radius) {
                        m_violations.push_back({
                            .object_id = cmp.refdes,
                            .rule_name = "Component-Keepout",
                            .description = std::format("Колізія з зоною кріплення '{}' (глибина {:.2f} мм)", kz.name, kz.circle_radius - d),
                            .distance = d
                        });
                        break;
                    }
                }
            } else {
                for (const auto& pt : obb) {
                    if (kz.poly.contains(pt)) {
                        m_violations.push_back({
                            .object_id = cmp.refdes,
                            .rule_name = "Component-Keepout",
                            .description = std::format("Корпус компонента перетинає полігон заборони '{}'", kz.name),
                            .distance = 0.0
                        });
                        break;
                    }
                }
            }
        }

        double min_edge_dist = 1e9;
        for (const auto& pt : obb) {
            for (size_t e = 0; e < m_outline.vertices.size(); ++e) {
                const size_t next = (e + 1) % m_outline.vertices.size();
                const double d = dist_point_to_segment(pt, m_outline.vertices[e], m_outline.vertices[next]);
                min_edge_dist = std::min(min_edge_dist, d);
            }
        }

        const double threshold = cmp.is_mlcc ? 3.0 : 1.0;
        if (min_edge_dist < threshold) {
            if (cmp.is_mlcc) {
                m_violations.push_back({
                    .object_id = cmp.refdes,
                    .rule_name = "DFM-Edge-Stress",
                    .description = std::format("Керамічний MLCC занадто близько до краю плати ({:.2f} мм < 3.0 мм, ризик тріщин)", min_edge_dist),
                    .distance = min_edge_dist
                });
            } else {
                m_violations.push_back({
                    .object_id = cmp.refdes,
                    .rule_name = "DFM-Board-Edge",
                    .description = std::format("Компонент занадто близько до контуру фрезерування ({:.2f} мм < 1.0 мм)", min_edge_dist),
                    .distance = min_edge_dist
                });
            }
        }
    }

    void validate(const TraceSegment& trace) {
        for (const auto& kz : m_keepouts) {
            if (!has_flag(kz.flags, KeepoutFlag::Route)) continue;
            if (kz.layer != -1 && kz.layer != trace.layer) continue;

            if (kz.is_circular) {
                const double eff_r = kz.circle_radius + (trace.width / 2.0);
                if (dist_point_to_segment(kz.circle_center, trace.start, trace.end) <= eff_r) {
                    m_violations.push_back({
                        .object_id = trace.net_name,
                        .rule_name = "Route-Keepout",
                        .description = std::format("Провідник net '{}' перетинає кругову зону кріплення '{}'", trace.net_name, kz.name),
                        .distance = 0.0
                    });
                }
            } else {
                const Vec2 mid = {(trace.start.x + trace.end.x) / 2.0, (trace.start.y + trace.end.y) / 2.0};
                if (kz.poly.contains(trace.start) || kz.poly.contains(trace.end) || kz.poly.contains(mid)) {
                    m_violations.push_back({
                        .object_id = trace.net_name,
                        .rule_name = "Route-Keepout",
                        .description = std::format("Доріжка net '{}' проходить крізь заборонений полігон '{}'", trace.net_name, kz.name),
                        .distance = 0.0
                    });
                }
            }
        }
    }

    [[nodiscard]] std::span<const Violation> violations() const noexcept {
        return m_violations;
    }

private:
    Polygon m_outline;
    std::vector<KeepoutZone> m_keepouts;
    std::vector<Violation> m_violations;
};

int main() {
    LayoutValidator validator({{{0, 0}, {100, 0}, {100, 60}, {0, 60}}});

    validator.add_keepout({
        .name = "M3_Hole_Corner",
        .circle_center = {10.0, 10.0},
        .circle_radius = 4.0,
        .is_circular = true,
        .flags = KeepoutFlag::Component | KeepoutFlag::Route | KeepoutFlag::Copper
    });

    validator.add_keepout({
        .name = "TO220_Heatsink_Area",
        .poly = {{{40, 20}, {70, 20}, {70, 40}, {40, 40}}},
        .flags = KeepoutFlag::Route,
        .layer = 0
    });

    validator.add_keepout({
        .name = "SMT_Top_Rail_4mm",
        .poly = {{{0, 56}, {100, 56}, {100, 60}, {0, 60}}},
        .flags = KeepoutFlag::Component,
        .layer = 0
    });

    validator.validate(Component{
        .refdes = "C1_MLCC_0805",
        .center = {50.0, 1.2},
        .width = 2.0,
        .height = 1.25,
        .rotation_deg = 0.0,
        .layer = 0,
        .is_mlcc = true
    });

    validator.validate(Component{
        .refdes = "R2_0603",
        .center = {12.0, 10.0},
        .width = 1.6,
        .height = 0.8,
        .rotation_deg = 45.0,
        .layer = 0
    });

    validator.validate(Component{
        .refdes = "LED_PWR",
        .center = {80.0, 58.0},
        .width = 2.0,
        .height = 1.2,
        .rotation_deg = 0.0,
        .layer = 0
    });

    validator.validate(TraceSegment{
        .net_name = "SPI_MISO",
        .start = {35.0, 30.0},
        .end = {75.0, 30.0},
        .width = 0.25,
        .layer = 0
    });

    std::cout << "=================================================================\n";
    std::cout << "       ЗВІТ АУДИТУ ЗОН ЗАБОРОНИ ТА МЕХАНІЧНИХ ОБМЕЖЕНЬ (C++20)  \n";
    std::cout << "=================================================================\n";
    const auto viols = validator.violations();
    std::cout << std::format("Всього знайдено порушень: {}\n\n", viols.size());
    for (size_t i = 0; i < viols.size(); ++i) {
        std::cout << std::format("[{}] Об'єкт: {:<16} | Правило: {:<18}\n    Деталі: {}\n\n",
                                 i + 1, viols[i].object_id, viols[i].rule_name, viols[i].description);
    }

    return 0;
}
